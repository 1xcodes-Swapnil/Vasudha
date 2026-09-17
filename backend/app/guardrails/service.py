"""Centralized VASUDHA Guardrail Service orchestrator."""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timezone
import logging

from backend.app.schemas.environmental_state import EnvironmentalState, SpatialContext
from backend.app.schemas.intervention import (
    InterventionDefinition,
    InterventionRecommendation,
    RecommendationSetResponse,
    ExpectedMetricEffect,
)
from backend.app.schemas.scientific_rag import EvidenceChunkPacket
from backend.app.guardrails.models import (
    GuardrailAction,
    GuardrailEvaluationSummary,
    GuardrailResult,
    GuardrailSeverity,
    QuantitativeClaimValidation,
)
from backend.app.guardrails.input_guardrails import InputGuardrails
from backend.app.guardrails.environmental_guardrails import EnvironmentalGuardrails
from backend.app.guardrails.geographic_guardrails import GeographicGuardrails
from backend.app.guardrails.evidence_guardrails import EvidenceGuardrails
from backend.app.guardrails.recommendation_guardrails import RecommendationGuardrails
from backend.app.guardrails.llm_guardrails import LLMGuardrails
from backend.app.guardrails.security_guardrails import SecurityGuardrails

logger = logging.getLogger("vasudha.earth")


class VASUDHAGuardrailService:
    """Production-quality centralized guardrail service for scientific integrity and safety."""

    def __init__(self):
        self.input_rules = InputGuardrails
        self.env_rules = EnvironmentalGuardrails
        self.geo_rules = GeographicGuardrails
        self.evidence_rules = EvidenceGuardrails
        self.rec_rules = RecommendationGuardrails
        self.llm_rules = LLMGuardrails
        self.sec_rules = SecurityGuardrails

    def validate_incoming_raw_input(self, data: Dict[str, Any]) -> GuardrailEvaluationSummary:
        """Validate raw incoming parameter dictionary before ingestion."""
        results = self.input_rules.validate_raw_input_dict(data)
        
        has_block = any(r.action == GuardrailAction.BLOCK for r in results)
        has_warning = any(r.action == GuardrailAction.ALLOW_WITH_WARNING for r in results)
        warnings = [r.message for r in results if r.severity == GuardrailSeverity.WARNING]

        overall_action = GuardrailAction.BLOCK if has_block else (
            GuardrailAction.ALLOW_WITH_WARNING if has_warning else GuardrailAction.ALLOW
        )

        return GuardrailEvaluationSummary(
            overall_passed=not has_block,
            action=overall_action,
            results=results,
            warnings=warnings,
        )

    def validate_environmental_state(
        self,
        state: EnvironmentalState,
        require_multi_metric: bool = True,
    ) -> GuardrailEvaluationSummary:
        """Execute full state validation: physical boundaries, zero vs unknown, plausibility, and multi-metric sufficiency."""
        results: List[GuardrailResult] = []

        # 1. Canonical State Semantics (Unknown vs Zero)
        results.extend(self.input_rules.validate_canonical_state(state))

        # 2. Ecological Plausibility
        results.extend(self.env_rules.check_ecological_plausibility(state))

        # 3. Multi-Metric Reasoning Sufficiency
        clarification_prompt = None
        if require_multi_metric:
            multi_metric_res = self.env_rules.evaluate_multi_metric_sufficiency(state)
            results.append(multi_metric_res)
            if multi_metric_res.action == GuardrailAction.REQUEST_CLARIFICATION:
                clarification_prompt = multi_metric_res.message

        has_block = any(r.action == GuardrailAction.BLOCK for r in results)
        has_clarification = any(r.action == GuardrailAction.REQUEST_CLARIFICATION for r in results)
        has_warning = any(r.action == GuardrailAction.ALLOW_WITH_WARNING for r in results)
        warnings = [r.message for r in results if r.severity == GuardrailSeverity.WARNING]

        if has_block:
            overall_action = GuardrailAction.BLOCK
        elif has_clarification:
            overall_action = GuardrailAction.REQUEST_CLARIFICATION
        elif has_warning:
            overall_action = GuardrailAction.ALLOW_WITH_WARNING
        else:
            overall_action = GuardrailAction.ALLOW

        return GuardrailEvaluationSummary(
            overall_passed=not has_block,
            action=overall_action,
            results=results,
            clarification_prompt=clarification_prompt,
            warnings=warnings,
        )

    def guard_recommendation_pipeline(
        self,
        recommendations: List[InterventionRecommendation],
        state: EnvironmentalState,
        evidence_packets: List[EvidenceChunkPacket],
    ) -> Tuple[List[InterventionRecommendation], GuardrailEvaluationSummary]:
        """Apply all recommendation, evidence, quantitative claim, and safety guardrails to intervention output."""
        sanitized_recs: List[InterventionRecommendation] = []
        all_results: List[GuardrailResult] = []
        all_warnings: List[str] = []

        # 1. Check overall evidence sufficiency
        ev_suff_res = self.evidence_rules.evaluate_evidence_sufficiency(evidence_packets)
        all_results.append(ev_suff_res)
        if ev_suff_res.severity == GuardrailSeverity.WARNING:
            all_warnings.append(ev_suff_res.message)

        for rec in recommendations:
            rec_results: List[GuardrailResult] = []

            # 2. Time horizon check
            th_res = self.rec_rules.validate_time_horizons(rec)
            rec_results.append(th_res)

            # 3. Quantitative claim validation & softening
            sanitized_effects, claim_reports = self.evidence_rules.validate_and_soften_quantitative_claims(
                metric_effects=rec.expected_metric_effects,
                supporting_evidence=rec.scientific_evidence or evidence_packets,
            )

            # Check if any claims were softened
            softened_count = sum(1 for c in claim_reports if c.action_taken == "softened_to_qualitative")
            if softened_count > 0:
                rec_results.append(GuardrailResult(
                    passed=True,
                    severity=GuardrailSeverity.INFO,
                    code="REC_QUANTITATIVE_CLAIMS_SOFTENED",
                    message=f"Softened {softened_count} ungrounded numerical estimate(s) to qualitative directional trends.",
                    details={"softened_claims": [c.original_claim for c in claim_reports if c.action_taken == "softened_to_qualitative"]},
                    action=GuardrailAction.ALLOW,
                ))

            # 4. Spatial / Geographic transferability check
            if state.spatial_context and state.spatial_context.ecosystem:
                grade, geo_res = self.geo_rules.evaluate_spatial_transferability(
                    user_spatial=state.spatial_context,
                    target_ecosystem=rec.explanation_chain.ecological_pressure if rec.explanation_chain else None,
                )
                rec_results.append(geo_res)
                if not geo_res.passed:
                    all_warnings.append(geo_res.message)

            # Check if any blocking safety rule triggered
            is_blocked = any(r.action == GuardrailAction.BLOCK for r in rec_results)

            if not is_blocked:
                # Update recommendation with sanitized quantitative effects
                rec_copy = rec.model_copy(update={"expected_metric_effects": sanitized_effects})
                sanitized_recs.append(rec_copy)

            all_results.extend(rec_results)

        has_block = len(sanitized_recs) == 0 and len(recommendations) > 0
        overall_action = GuardrailAction.BLOCK if has_block else (
            GuardrailAction.ALLOW_WITH_WARNING if all_warnings else GuardrailAction.ALLOW
        )

        summary = GuardrailEvaluationSummary(
            overall_passed=not has_block,
            action=overall_action,
            results=all_results,
            sanitized_output=sanitized_recs,
            warnings=all_warnings,
        )

        return sanitized_recs, summary

    def sanitize_outgoing_response(self, response_data: Any) -> Any:
        """Scan and redact any accidental secrets in final response dictionaries or objects."""
        # Validate no credentials exist
        scan_res = self.sec_rules.scan_outgoing_payload(response_data)
        if not scan_res.passed:
            logger.error("Guardrail blocked outgoing response containing potential sensitive credential.")
            return {"error": "Response blocked by security guardrails. Please contact administrator."}
        return response_data


# Singleton instance
_guardrail_service: Optional[VASUDHAGuardrailService] = None


def get_guardrail_service() -> VASUDHAGuardrailService:
    """Singleton getter for the VASUDHA Guardrail Service."""
    global _guardrail_service
    if _guardrail_service is None:
        _guardrail_service = VASUDHAGuardrailService()
    return _guardrail_service
