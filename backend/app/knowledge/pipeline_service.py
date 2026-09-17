"""End-to-End Ecological Reasoning & Findings Pipeline Service (Phase 9).

Orchestrates the transformation:
User input (NL text / state / coordinates)
→ Extraction & Spatial Harmonization
→ Authoritative Dataset Enrichment & Provenance Tracking
→ Conflict & Uncertainty Audit
→ Multi-Metric Deterministic Reasoning (3+ variables)
→ Targeted Scientific RAG Evidence Retrieval
→ Structured Ecological Findings Synthesis
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from backend.app.core.logging import logger
from backend.app.schemas.environmental_state import (
    EnvironmentalState,
    SoilState,
    LandState,
    BiodiversityState,
    ClimateState,
    HumanImpactState,
    SpatialContext,
)
from backend.app.schemas.dataset import (
    VariableProvenance,
    DataQualityReport,
    StateEnrichmentRequest,
)
from backend.app.schemas.knowledge import (
    MetricDomain,
    ReasoningChain,
    ReasoningChainLink,
    VariableObservationState,
    VariableStatus,
)
from backend.app.schemas.scientific_rag import (
    EvidenceChunkPacket,
    NaturePressureSeverity,
    ScientificSearchQuery,
)
from backend.app.schemas.ecological_findings import (
    ConflictReport,
    ConflictType,
    EcologicalFinding,
    EcologicalFindingsRequest,
    EcologicalFindingsResponse,
    ObservationSource,
    VariableFindingDetail,
)
from backend.app.knowledge.text_extractor import text_extractor
from backend.app.knowledge.conflict_detector import conflict_detector
from backend.app.knowledge.reasoning_engine import get_reasoning_engine, EcologicalReasoningEngine
from backend.app.knowledge.multi_metric_engine import get_multi_metric_engine, MultiMetricReasoningEngine
from backend.app.knowledge.rag_service import get_rag_service, ScientificRAGService
from backend.app.datasets.manager import dataset_manager
from backend.app.services.geo.manager import resolve_geo_context


class EcologicalFindingsPipelineService:
    """Production service coordinating dataset enrichment, multi-metric reasoning, conflict detection, and RAG."""

    def __init__(
        self,
        reasoning_engine: Optional[EcologicalReasoningEngine] = None,
        multi_metric_engine: Optional[MultiMetricReasoningEngine] = None,
        rag_service: Optional[ScientificRAGService] = None,
    ):
        self.reasoning_engine = reasoning_engine or get_reasoning_engine()
        self.multi_metric_engine = multi_metric_engine or get_multi_metric_engine()
        self.rag_service = rag_service or get_rag_service()

    def process_request(self, req: EcologicalFindingsRequest) -> EcologicalFindingsResponse:
        """Execute complete Phase 9 ecological reasoning and evidence retrieval pipeline."""
        logger.info("Executing Ecological Reasoning & Findings Pipeline.")

        # ----------------------------------------------------------------------
        # Step 1: Parse Natural Language Text (if supplied) and Harmonize User State
        # ----------------------------------------------------------------------
        extracted_from_text: Dict[str, Any] = {}
        text_state = EnvironmentalState()
        if req.text_description:
            text_state, extracted_from_text = text_extractor.extract_from_text(req.text_description)

        # Merge pre-structured state if supplied
        user_supplied_map: Dict[str, Any] = dict(extracted_from_text)
        base_user_state = text_state

        if req.state:
            # Explicit state overrides or augments text
            req_dict = req.state.model_dump()
            text_dict = text_state.model_dump()

            for domain in ["soil", "land", "biodiversity", "climate", "human_impact", "spatial_context"]:
                req_sub = req_dict.get(domain, {})
                text_sub = text_dict.get(domain, {})
                for k, v in req_sub.items():
                    if v is not None:
                        text_sub[k] = v
                        user_supplied_map[f"{domain}.{k}"] = v
                text_dict[domain] = text_sub

            base_user_state = EnvironmentalState.model_validate(text_dict)

        # Check for explicit coordinate overrides in request
        lat = req.latitude if req.latitude is not None else base_user_state.spatial_context.latitude
        lon = req.longitude if req.longitude is not None else base_user_state.spatial_context.longitude
        region = req.region or base_user_state.spatial_context.region
        ecosystem = req.ecosystem or base_user_state.spatial_context.ecosystem

        # ----------------------------------------------------------------------
        # Step 2: Geographic Context Resolution
        # ----------------------------------------------------------------------
        geo_result = None
        if lat is not None and lon is not None:
            geo_result = resolve_geo_context(lat, lon)
            if not region:
                region = geo_result.region
            if not ecosystem:
                ecosystem = geo_result.ecosystem

        resolved_spatial = SpatialContext(
            latitude=lat,
            longitude=lon,
            region=region,
            ecosystem=ecosystem,
        )
        base_user_state.spatial_context = resolved_spatial

        # ----------------------------------------------------------------------
        # Step 3: Authoritative Dataset Query & Enrichment
        # ----------------------------------------------------------------------
        dataset_derived_state = EnvironmentalState(spatial_context=resolved_spatial)
        provenance_map: Dict[str, VariableProvenance] = {}
        dataset_values_map: Dict[str, Any] = {}

        if req.enrich_from_datasets and lat is not None and lon is not None:
            try:
                point_res = dataset_manager.query_point(
                    latitude=lat,
                    longitude=lon,
                    allow_synthetic=req.allow_synthetic_fallback,
                )
                dataset_derived_state = point_res.canonical_state
                provenance_map = point_res.provenance_records

                # Extract dataset values map
                for var_path, prov in provenance_map.items():
                    if prov.canonical_value is not None:
                        dataset_values_map[var_path] = prov.canonical_value

            except Exception as exc:
                logger.warning(f"Authoritative dataset enrichment failed gracefully: {exc}")

        # ----------------------------------------------------------------------
        # Step 4: Construct Harmonized State with Strict Provenance Tracking
        # ----------------------------------------------------------------------
        harmonized_dict = base_user_state.model_dump()
        ds_dict = dataset_derived_state.model_dump()

        user_metrics_count = 0
        dataset_metrics_count = 0
        variable_sources: Dict[str, ObservationSource] = {}

        # Canonical metric keys list
        metric_keys = [
            ("soil.ph", "soil", "ph"),
            ("soil.organic_carbon", "soil", "organic_carbon"),
            ("soil.moisture", "soil", "moisture"),
            ("land.land_use", "land", "land_use"),
            ("land.land_cover", "land", "land_cover"),
            ("biodiversity.species_richness", "biodiversity", "species_richness"),
            ("biodiversity.habitat_diversity", "biodiversity", "habitat_diversity"),
            ("climate.temperature", "climate", "temperature"),
            ("climate.rainfall", "climate", "rainfall"),
            ("human_impact.pollution", "human_impact", "pollution"),
            ("human_impact.deforestation", "human_impact", "deforestation"),
        ]

        for metric_id, domain, key in metric_keys:
            u_val = harmonized_dict.get(domain, {}).get(key)
            d_val = ds_dict.get(domain, {}).get(key)

            if req.overwrite_user_values and d_val is not None:
                harmonized_dict[domain][key] = d_val
                variable_sources[metric_id] = ObservationSource.DATASET_DERIVED
                dataset_metrics_count += 1
            elif u_val is not None:
                harmonized_dict[domain][key] = u_val
                variable_sources[metric_id] = ObservationSource.USER_SUPPLIED
                user_metrics_count += 1
            elif d_val is not None:
                harmonized_dict[domain][key] = d_val
                variable_sources[metric_id] = ObservationSource.DATASET_DERIVED
                dataset_metrics_count += 1
            else:
                harmonized_dict[domain][key] = None
                variable_sources[metric_id] = ObservationSource.UNKNOWN

        canonical_state = EnvironmentalState.model_validate(harmonized_dict)
        canonical_state.spatial_context = resolved_spatial

        # ----------------------------------------------------------------------
        # Step 5: Detect Conflicts and Compute Uncertainty Penalties
        # ----------------------------------------------------------------------
        conflicts, penalty = conflict_detector.detect_conflicts(
            user_state=base_user_state,
            dataset_state=dataset_derived_state,
            user_extracted_map=user_supplied_map,
            provenance_map=provenance_map,
            resolved_spatial=resolved_spatial,
        )

        # ----------------------------------------------------------------------
        # Step 6: Multi-Metric Reasoning & Finding Generation
        # ----------------------------------------------------------------------
        rule_eval = self.reasoning_engine.evaluate_state(canonical_state)
        observed = rule_eval.observed_metrics
        variables_status = rule_eval.variables_status

        # Execute multi-metric compound stress evaluation (3+ variables)
        spatial_dict = {
            "latitude": resolved_spatial.latitude,
            "longitude": resolved_spatial.longitude,
            "region": resolved_spatial.region or "global",
            "ecosystem": resolved_spatial.ecosystem or "all",
        }
        multi_pressures = self.multi_metric_engine.evaluate_multi_metric_pressures(
            observed=observed,
            spatial_context=spatial_dict,
        )

        findings: List[EcologicalFinding] = []
        covered_metrics: Set[str] = set()

        # Helper to construct VariableFindingDetail
        def make_var_detail(var_id: str) -> VariableFindingDetail:
            parts = var_id.split(".", 1)
            dom = parts[0]
            k = parts[1] if len(parts) > 1 else ""

            val = None
            if hasattr(canonical_state, dom):
                sub_obj = getattr(canonical_state, dom)
                if hasattr(sub_obj, k):
                    val = getattr(sub_obj, k)

            src = variable_sources.get(var_id)
            if src is None:
                if dom == "derived":
                    src = ObservationSource.INFERRED
                elif val is not None:
                    src = ObservationSource.USER_SUPPLIED
                else:
                    src = ObservationSource.UNKNOWN

            prov = provenance_map.get(var_id)
            ds_id = prov.dataset_id if prov else None
            is_synth = prov.is_synthetic if prov else False

            unit_map = {
                "soil.ph": "pH",
                "soil.organic_carbon": "%",
                "soil.moisture": "%",
                "climate.temperature": "°C",
                "climate.rainfall": "mm/yr",
                "biodiversity.species_richness": "species count",
                "biodiversity.habitat_diversity": "%",
                "human_impact.deforestation": "%",
                "human_impact.pollution": "index",
            }
            name_map = {
                "soil.ph": "Soil pH",
                "soil.organic_carbon": "Soil Organic Carbon",
                "soil.moisture": "Soil Moisture",
                "land.land_use": "Land Use",
                "land.land_cover": "Land Cover",
                "biodiversity.species_richness": "Species Richness",
                "biodiversity.habitat_diversity": "Habitat Diversity",
                "climate.temperature": "Ambient Temperature",
                "climate.rainfall": "Annual Rainfall",
                "human_impact.deforestation": "Deforestation Rate",
                "human_impact.pollution": "Pollution Level",
            }
            return VariableFindingDetail(
                variable_id=var_id,
                name=name_map.get(var_id, var_id),
                value=val,
                unit=unit_map.get(var_id),
                source=src,
                dataset_id=ds_id,
                is_synthetic=is_synth,
                confidence=0.95 if src == ObservationSource.USER_SUPPLIED else 0.90 if src == ObservationSource.DATASET_DERIVED else 0.0,
            )

        # Convert multi-metric compound pressures to EcologicalFindings
        for mp in multi_pressures:
            covered_metrics.update(mp.contributing_metrics)
            var_details = [make_var_detail(v) for v in mp.contributing_metrics]

            # Determine domain
            domain = "water_climate"
            if "soil.ph" in mp.contributing_metrics or "soil.organic_carbon" in mp.contributing_metrics:
                domain = "soil_health"
            elif "biodiversity.habitat_diversity" in mp.contributing_metrics or "biodiversity.species_richness" in mp.contributing_metrics:
                domain = "biodiversity_trophic"
            elif "human_impact.deforestation" in mp.contributing_metrics:
                domain = "anthropogenic_pressure"

            # Calculate calibrated confidence
            finding_conf = max(round(mp.confidence - penalty, 2), 0.50)
            uncertainty_lvl = "low" if finding_conf >= 0.85 else "medium" if finding_conf >= 0.70 else "high"

            u_factors = list(mp.uncertainty_and_limitations)
            if penalty > 0:
                u_factors.append(f"Confidence adjusted for {len(conflicts)} data discrepancies/mismatches.")

            # Identify conflict IDs related to this finding
            c_flags = [c.conflict_id for c in conflicts if any(v in mp.contributing_metrics for v in c.variables_involved)]

            findings.append(
                EcologicalFinding(
                    finding_id=f"FINDING_{mp.pressure_id}",
                    title=mp.name,
                    domain=domain,
                    severity=mp.severity,
                    contributing_variables=mp.contributing_metrics,
                    variable_details=var_details,
                    inferred_pressure=mp.name,
                    ecological_mechanism=" ".join(mp.inferred_mechanisms),
                    supporting_relationships=[link.relationship_id for link in (mp.reasoning_chain.links if mp.reasoning_chain else [])],
                    reasoning_chain=mp.reasoning_chain,
                    uncertainty_level=uncertainty_lvl,
                    uncertainty_factors=u_factors,
                    conflict_flags=c_flags,
                    confidence=finding_conf,
                    evidence_references=mp.evidence_packet[: req.top_k_evidence],
                    geographic_relevance=f"Ecosystem: {spatial_dict['ecosystem']}, Region: {spatial_dict['region']}",
                )
            )

        # ----------------------------------------------------------------------
        # Step 7: Single-Metric Findings for Uncovered Triggered Pressures
        # ----------------------------------------------------------------------
        for inf in rule_eval.inferred_pressures:
            if inf.triggering_metric in covered_metrics:
                continue

            # RAG evidence retrieval for single-metric pressure
            rag_query = f"{inf.triggering_metric} {inf.target_metric} {inf.inferred_state} {inf.ecological_mechanism[:60]}"
            rag_resp = self.rag_service.search_evidence(
                ScientificSearchQuery(
                    query=rag_query,
                    metrics=[inf.triggering_metric, inf.target_metric],
                    ecosystem=spatial_dict.get("ecosystem"),
                    geographic_scope=spatial_dict.get("region"),
                    top_k=req.top_k_evidence,
                )
            )

            var_details = [make_var_detail(inf.triggering_metric)]
            sev_enum = NaturePressureSeverity.MEDIUM
            if inf.severity == "critical":
                sev_enum = NaturePressureSeverity.CRITICAL
            elif inf.severity == "high":
                sev_enum = NaturePressureSeverity.HIGH
            elif inf.severity == "low":
                sev_enum = NaturePressureSeverity.LOW

            matching_chain = next(
                (c for c in rule_eval.reasoning_chains if c.root_observed_metric == inf.triggering_metric),
                None,
            )

            c_flags = [c.conflict_id for c in conflicts if inf.triggering_metric in c.variables_involved]
            finding_conf = max(round(inf.confidence - penalty, 2), 0.50)
            uncertainty_lvl = "low" if finding_conf >= 0.85 else "medium" if finding_conf >= 0.70 else "high"

            domain = "soil_health" if "soil." in inf.triggering_metric else "water_climate" if "climate." in inf.triggering_metric else "biodiversity_trophic" if "biodiversity." in inf.triggering_metric else "anthropogenic_pressure"

            findings.append(
                EcologicalFinding(
                    finding_id=f"FINDING_{inf.pressure_id}",
                    title=inf.name,
                    domain=domain,
                    severity=sev_enum,
                    contributing_variables=[inf.triggering_metric],
                    variable_details=var_details,
                    inferred_pressure=inf.name,
                    ecological_mechanism=inf.ecological_mechanism,
                    supporting_relationships=[inf.pressure_id],
                    reasoning_chain=matching_chain,
                    uncertainty_level=uncertainty_lvl,
                    uncertainty_factors=[
                        f"Single-variable inference on '{inf.triggering_metric}'; multi-metric synergy cannot be fully evaluated without complementary variables."
                    ],
                    conflict_flags=c_flags,
                    confidence=finding_conf,
                    evidence_references=rag_resp.evidence_chunks[: req.top_k_evidence],
                    geographic_relevance=f"Ecosystem: {spatial_dict['ecosystem']}, Region: {spatial_dict['region']}",
                )
            )

        # ----------------------------------------------------------------------
        # Step 8: Calculate Overall Metrics, Limitations & Return Response
        # ----------------------------------------------------------------------
        unknown_metric_ids = [
            v.metric_id for v in variables_status if v.status == VariableObservationState.UNKNOWN
        ]

        mean_confidence = (
            round(sum(f.confidence for f in findings) / len(findings), 2)
            if findings
            else 0.0
        )

        limitations = [
            "All ecological mechanisms and findings are derived deterministically from peer-reviewed scientific relationships.",
            "LLM is not used as a scientific source of truth; evidence packets cite verifiable institutional reports and literature.",
            f"Observed state contains {user_metrics_count} user-provided metrics, {dataset_metrics_count} dataset-enriched metrics, and {len(unknown_metric_ids)} unknown variables.",
        ]
        if conflicts:
            limitations.append(f"{len(conflicts)} data discrepancies/mismatches were identified and accounted for in uncertainty scoring.")

        return EcologicalFindingsResponse(
            canonical_state=canonical_state,
            provenance_map=provenance_map,
            variables_status=variables_status,
            observed_user_metrics_count=user_metrics_count,
            dataset_derived_metrics_count=dataset_metrics_count,
            unknown_metrics_count=len(unknown_metric_ids),
            findings=findings,
            total_findings_count=len(findings),
            conflicts_detected=conflicts,
            has_conflicts=len(conflicts) > 0,
            overall_confidence_score=mean_confidence,
            system_limitations=limitations,
            evaluation_timestamp=datetime.now(timezone.utc).isoformat(),
        )


# Global singleton instance
findings_pipeline_service = EcologicalFindingsPipelineService()


def get_findings_pipeline_service() -> EcologicalFindingsPipelineService:
    """Returns singleton instance of EcologicalFindingsPipelineService."""
    global findings_pipeline_service
    return findings_pipeline_service
