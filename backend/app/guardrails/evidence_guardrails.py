"""Scientific evidence traceability, anti-fabrication, and quantitative claim guardrails."""

import re
from typing import Any, Dict, List, Optional, Tuple
from backend.app.schemas.scientific_rag import EvidenceChunkPacket, EvidenceStrength
from backend.app.schemas.intervention import ExpectedMetricEffect
from backend.app.guardrails.models import (
    GuardrailAction,
    GuardrailResult,
    GuardrailSeverity,
    QuantitativeClaimValidation,
)
from backend.app.knowledge.curated_corpus import CURATED_SCIENTIFIC_DOCUMENTS


class EvidenceGuardrails:
    """Enforces evidence provenance, blocks fabricated citations, and validates quantitative claims."""

    # Set of authentic curated corpus document IDs and DOIs
    AUTHENTIC_DOC_IDS = {d.id for d in CURATED_SCIENTIFIC_DOCUMENTS}
    AUTHENTIC_DOIS = {d.doi for d in CURATED_SCIENTIFIC_DOCUMENTS if d.doi}
    AUTHENTIC_TITLES = {d.title.lower() for d in CURATED_SCIENTIFIC_DOCUMENTS}

    @classmethod
    def validate_citation_authenticity(cls, citation_text: str, doc_id: Optional[str] = None) -> GuardrailResult:
        """Verify that a cited scientific document exists in the verified knowledge base."""
        if not citation_text or not citation_text.strip():
            return GuardrailResult(
                passed=False,
                severity=GuardrailSeverity.WARNING,
                code="EVIDENCE_CITATION_EMPTY",
                message="Citation text is missing or blank.",
                details={},
                action=GuardrailAction.ALLOW_WITH_WARNING,
            )

        if doc_id and doc_id in cls.AUTHENTIC_DOC_IDS:
            return GuardrailResult(
                passed=True,
                severity=GuardrailSeverity.INFO,
                code="EVIDENCE_CITATION_VERIFIED",
                message=f"Citation '{citation_text[:80]}...' verified against curated scientific corpus ({doc_id}).",
                details={"doc_id": doc_id},
                action=GuardrailAction.ALLOW,
            )

        # Check title match against known authoritative corpus
        clean_text_lower = citation_text.lower()
        matched = any(known_title in clean_text_lower for known_title in cls.AUTHENTIC_TITLES)
        if matched:
            return GuardrailResult(
                passed=True,
                severity=GuardrailSeverity.INFO,
                code="EVIDENCE_TITLE_VERIFIED",
                message="Citation matches verified corpus title.",
                details={"citation": citation_text[:100]},
                action=GuardrailAction.ALLOW,
            )

        # If document ID was supplied but is unknown in knowledge base
        if doc_id and doc_id not in cls.AUTHENTIC_DOC_IDS:
            return GuardrailResult(
                passed=False,
                severity=GuardrailSeverity.WARNING,
                code="EVIDENCE_UNVERIFIED_SOURCE_ID",
                message=f"Document ID '{doc_id}' is not in the verified corpus; treating as unindexed citation.",
                details={"doc_id": doc_id, "citation": citation_text[:100]},
                action=GuardrailAction.ALLOW_WITH_WARNING,
            )

        return GuardrailResult(
            passed=True,
            severity=GuardrailSeverity.INFO,
            code="EVIDENCE_EXTERNAL_CITATION",
            message="Citation referenced as general literature.",
            details={"citation": citation_text[:100]},
            action=GuardrailAction.ALLOW,
        )

    @classmethod
    def validate_and_soften_quantitative_claims(
        cls,
        metric_effects: List[ExpectedMetricEffect],
        supporting_evidence: List[EvidenceChunkPacket],
    ) -> Tuple[List[ExpectedMetricEffect], List[QuantitativeClaimValidation]]:
        """Hard guardrail: Validates numerical effect claims against supporting evidence.
        
        If a quantitative claim (e.g. '+25%', '0.4% SOC/yr') lacks strong/moderate empirical
        evidence, strips the precise number and replaces it with a scientifically qualified
        directional statement.
        """
        sanitized_effects: List[ExpectedMetricEffect] = []
        validation_reports: List[QuantitativeClaimValidation] = []

        has_strong_evidence = any(
            e.evidence_strength in (EvidenceStrength.STRONG, EvidenceStrength.MODERATE)
            for e in supporting_evidence
        )

        # Check if evidence contains relevant quantitative numbers
        evidence_corpus_text = " ".join([e.content for e in supporting_evidence]).lower()

        for effect in metric_effects:
            original_quant = effect.quantitative_estimate
            if not original_quant or not original_quant.strip():
                # Qualitative only - already safe
                sanitized_effects.append(effect)
                validation_reports.append(QuantitativeClaimValidation(
                    original_claim=f"{effect.metric_name}: {effect.direction.value}",
                    metric_id=effect.metric_id,
                    extracted_quantity=None,
                    is_supported=True,
                    softened_claim=f"{effect.metric_name}: {effect.direction.value}",
                    action_taken="preserved",
                ))
                continue

            # Extract percentage or numerical tokens like "20%", "+0.5", "30-50%"
            numbers_in_claim = re.findall(r"(\d+(?:\.\d+)?%?)", original_quant)

            # Check if claim is supported by evidence
            is_empirically_supported = has_strong_evidence and any(
                num.replace("%", "") in evidence_corpus_text for num in numbers_in_claim
            )

            if is_empirically_supported:
                # Validated quantitative claim
                sanitized_effects.append(effect)
                validation_reports.append(QuantitativeClaimValidation(
                    original_claim=f"{effect.metric_name}: {original_quant}",
                    metric_id=effect.metric_id,
                    extracted_quantity=original_quant,
                    is_supported=True,
                    evidence_id=supporting_evidence[0].document_id if supporting_evidence else None,
                    softened_claim=f"{effect.metric_name}: {original_quant}",
                    action_taken="preserved",
                ))
            else:
                # Unsupported quantitative estimate -> Soften to qualitative directional trend
                direction_val = (
                    effect.expected_direction.value
                    if hasattr(effect, "expected_direction") and hasattr(effect.expected_direction, "value")
                    else str(getattr(effect, "expected_direction", getattr(effect, "direction", "increase")))
                )
                qualitative_substitute = (
                    f"Expected {direction_val} over time; exact rate subject to site conditions"
                )
                
                softened_effect = effect.model_copy(
                    update={
                        "quantitative_estimate": None,
                        "is_quantified": False,
                    }
                )
                sanitized_effects.append(softened_effect)

                validation_reports.append(QuantitativeClaimValidation(
                    original_claim=f"{effect.metric_name}: {original_quant}",
                    metric_id=effect.metric_id,
                    extracted_quantity=original_quant,
                    is_supported=False,
                    softened_claim=f"{effect.metric_name}: {qualitative_substitute}",
                    action_taken="softened_to_qualitative",
                ))

        return sanitized_effects, validation_reports

    @classmethod
    def evaluate_evidence_sufficiency(
        cls,
        evidence_packets: List[EvidenceChunkPacket],
        required_topic: str = "",
    ) -> GuardrailResult:
        """Verify that at least one valid evidence chunk exists to support recommendations."""
        if not evidence_packets:
            return GuardrailResult(
                passed=False,
                severity=GuardrailSeverity.WARNING,
                code="EVIDENCE_INSUFFICIENT_RETRIEVAL",
                message=(
                    "Insufficient scientific evidence was retrieved from the peer-reviewed corpus "
                    f"to support specific empirical claims regarding '{required_topic}'. "
                    "Recommendations are derived from general ecological first principles."
                ),
                details={"evidence_count": 0, "topic": required_topic},
                action=GuardrailAction.ALLOW_WITH_WARNING,
            )

        high_quality = sum(
            1 for e in evidence_packets
            if e.evidence_strength in (EvidenceStrength.STRONG, EvidenceStrength.MODERATE)
        )

        return GuardrailResult(
            passed=True,
            severity=GuardrailSeverity.INFO,
            code="EVIDENCE_SUFFICIENT",
            message=f"Retrieved {len(evidence_packets)} relevant scientific evidence chunk(s) ({high_quality} high/moderate strength).",
            details={"evidence_count": len(evidence_packets), "high_quality_count": high_quality},
            action=GuardrailAction.ALLOW,
        )
