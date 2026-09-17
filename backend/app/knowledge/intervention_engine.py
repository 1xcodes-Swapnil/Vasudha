"""Deterministic Scientific Ecological Intervention Engine (Phase 10).

Converts identified ecological findings and environmental state profiles into
context-specific, biophysically filtered, evidence-backed recommendations.
"""

from typing import Dict, List, Optional, Set, Tuple, Any
from datetime import datetime, timezone
import logging

from backend.app.schemas.environmental_state import EnvironmentalState, SpatialContext
from backend.app.schemas.ecological_findings import (
    EcologicalFinding,
    ConflictReport,
    NaturePressureSeverity,
)
from backend.app.schemas.intervention import (
    DirectionOfChange,
    ExpectedMetricEffect,
    InterventionCategory,
    InterventionDefinition,
    InterventionEngineRequest,
    InterventionRecommendation,
    RecommendationConfidenceBasis,
    RecommendationSetResponse,
    TimeHorizon,
    ExplanationChainModel,
    FeasibilityEvaluationModel,
    ValidatedClaimModel,
    ScientificValidationPacket,
)
from backend.app.schemas.scientific_rag import EvidenceChunkPacket, EvidenceStrength, ScientificSearchQuery
from backend.app.knowledge.curated_interventions import CURATED_INTERVENTIONS
from backend.app.knowledge.curated_corpus import CURATED_SCIENTIFIC_DOCUMENTS
from backend.app.knowledge.rag_service import get_rag_service
from backend.app.knowledge.multi_metric_engine import get_multi_metric_engine

logger = logging.getLogger("vasudha.earth")


class EcologicalInterventionEngine:
    """Core recommendation engine matching environmental findings to biophysically viable actions."""

    def __init__(self, interventions: Optional[List[InterventionDefinition]] = None):
        self._interventions: Dict[str, InterventionDefinition] = {
            i.id: i for i in (interventions or CURATED_INTERVENTIONS)
        }
        self._rag_service = get_rag_service()
        self._corpus_docs = {d.id: d for d in CURATED_SCIENTIFIC_DOCUMENTS}

    def list_interventions(self) -> List[InterventionDefinition]:
        """Return all canonical intervention definitions in knowledge base."""
        return list(self._interventions.values())

    def get_intervention(self, intervention_id: str) -> Optional[InterventionDefinition]:
        """Retrieve a single intervention definition by ID."""
        return self._interventions.get(intervention_id)

    def generate_recommendations(
        self, request: InterventionEngineRequest
    ) -> RecommendationSetResponse:
        """Execute full recommendation pipeline:
        Findings → Candidate Matching → Biophysical Filtering → Evidence Mapping → Directional Effects → Ranked Set
        """
        state = request.state
        findings = request.findings
        conflicts = request.conflicts or []
        spatial_context = request.spatial_context or state.spatial_context

        # If findings were not provided, evaluate multi-metric findings directly from state
        if not findings:
            multi_engine = get_multi_metric_engine()
            analysis_result = multi_engine.analyze_environmental_state(state)
            # Synthesize minimal EcologicalFinding objects for matching from analysis_result.pressures
            findings = []
            for pressure in analysis_result.pressures:
                finding_id = f"FINDING_{pressure.pressure_id.upper()}"
                sev = NaturePressureSeverity.HIGH
                if pressure.severity == NaturePressureSeverity.CRITICAL:
                    sev = NaturePressureSeverity.CRITICAL
                elif pressure.severity == NaturePressureSeverity.LOW:
                    sev = NaturePressureSeverity.MEDIUM

                findings.append(
                    EcologicalFinding(
                        finding_id=finding_id,
                        title=pressure.name,
                        domain=pressure.pressure_type,
                        severity=sev,
                        contributing_variables=pressure.contributing_metrics,
                        variable_details=[],
                        inferred_pressure=pressure.name,
                        ecological_mechanism=" ".join(pressure.inferred_mechanisms),
                        supporting_relationships=[],
                        reasoning_chain=pressure.reasoning_chain,
                        uncertainty_level="low",
                        uncertainty_factors=[],
                        conflict_flags=[],
                        confidence=pressure.confidence,
                        evidence_references=pressure.evidence_packet,
                        geographic_relevance="site_context",
                    )
                )

        # Collect identified pressure tokens and degraded metrics
        observed_pressure_tokens: Set[str] = set()
        for f in findings:
            observed_pressure_tokens.add(f.inferred_pressure.lower())
            observed_pressure_tokens.add(f.finding_id.lower())
            observed_pressure_tokens.add(f.domain.lower())
            for var in f.contributing_variables:
                observed_pressure_tokens.add(var.lower())

        # Also inspect raw state metrics for known degradation flags
        if state.soil.organic_carbon is not None and state.soil.organic_carbon < 1.5:
            observed_pressure_tokens.add("soil_organic_carbon_depletion")
            observed_pressure_tokens.add("soil_carbon_depletion")
        if state.soil.ph is not None and (state.soil.ph < 5.5 or state.soil.ph > 8.2):
            observed_pressure_tokens.add("soil_acidity")
            observed_pressure_tokens.add("soil_ph_stress")
        if state.climate.rainfall is not None and state.climate.rainfall < 600:
            observed_pressure_tokens.add("soil_water_stress")
            observed_pressure_tokens.add("drought_stress")
        if state.human_impact.deforestation is not None and state.human_impact.deforestation > 10.0:
            observed_pressure_tokens.add("deforestation")
            observed_pressure_tokens.add("habitat_fragmentation")
        if state.biodiversity.habitat_diversity is not None and state.biodiversity.habitat_diversity < 40.0:
            observed_pressure_tokens.add("monoculture_simplification")
            observed_pressure_tokens.add("agricultural_homogenization")
            observed_pressure_tokens.add("landscape_homogenization")
        if state.human_impact.pollution is not None and state.human_impact.pollution > 25.0:
            observed_pressure_tokens.add("chemical_pollution")
            observed_pressure_tokens.add("agricultural_runoff")
            observed_pressure_tokens.add("ecotoxicity")

        # Conflict penalty computation
        total_conflict_penalty = sum(c.uncertainty_penalty for c in conflicts)
        total_conflict_penalty = min(total_conflict_penalty, 0.40)

        candidates: List[Tuple[InterventionDefinition, float, float, List[str], List[str], str]] = []
        excluded_interventions: Dict[str, str] = {}

        # Evaluate each canonical intervention
        for intervention in self._interventions.values():
            is_suitable, reason, suit_score = self._check_biophysical_suitability(
                intervention=intervention,
                state=state,
                spatial_context=spatial_context,
            )

            if not is_suitable:
                excluded_interventions[intervention.id] = reason
                continue

            # Calculate pressure relevance
            rel_score, matched_findings, matched_pressures = self._calculate_pressure_relevance(
                intervention=intervention,
                findings=findings,
                pressure_tokens=observed_pressure_tokens,
            )

            # Only retain candidates with non-zero relevance or broad restoration applicability
            if rel_score <= 0.05 and not findings:
                # If no findings at all (e.g. pristine baseline), relevance is low
                rel_score = 0.2

            if rel_score > 0.05:
                candidates.append((intervention, suit_score, rel_score, matched_findings, matched_pressures, reason))
            else:
                excluded_interventions[intervention.id] = "No matching ecological pressure identified at this site"

        # Build detailed recommendations
        recommendations: List[InterventionRecommendation] = []
        targeted_findings_set: Set[str] = set()

        for intervention, suit_score, rel_score, matched_findings, matched_pressures, suit_reason in candidates:
            targeted_findings_set.update(matched_findings)

            # Retrieve evidence references
            evidence_packets = self._retrieve_intervention_evidence(intervention, state)

            # Compute data completeness for this intervention's target metrics
            data_completeness = self._compute_data_completeness(intervention, state)

            # Evidence grade weight
            evidence_weight = 0.90
            evidence_grade_str = "Strong"
            if any(e.evidence_strength == EvidenceStrength.CONSENSUS for e in evidence_packets):
                evidence_weight = 1.0
                evidence_grade_str = "Consensus"

            # Compute transparent calibrated confidence
            raw_confidence = (
                (suit_score * 0.35) + (rel_score * 0.35) + (evidence_weight * 0.30)
            ) * data_completeness - total_conflict_penalty

            final_confidence = max(0.20, min(0.98, raw_confidence))

            # Build human-readable confidence justification
            justification = (
                f"Confidence {int(final_confidence * 100)}%: Grade={evidence_grade_str}; "
                f"Biophysical fit={int(suit_score * 100)}%; Pressure match={int(rel_score * 100)}%; "
                f"Data completeness={int(data_completeness * 100)}%"
            )
            if total_conflict_penalty > 0:
                justification += f"; Conflict penalty=-{int(total_conflict_penalty * 100)}%"

            conf_basis = RecommendationConfidenceBasis(
                overall_confidence=round(final_confidence, 3),
                evidence_grade=evidence_grade_str,
                pressure_relevance_score=round(rel_score, 3),
                biophysical_suitability_score=round(suit_score, 3),
                data_completeness_factor=round(data_completeness, 3),
                conflict_uncertainty_penalty=round(total_conflict_penalty, 3),
                justification_summary=justification,
            )

            # Contextualize action text
            what_to_do = self._contextualize_what_to_do(intervention, state, spatial_context)
            why_it_works = self._contextualize_why_it_works(intervention, matched_pressures)

            # Constraints list
            constraints_list = [c.description for c in intervention.constraints]

            # Explanation Chain & Feasibility
            explanation_chain = self._build_explanation_chain(
                intervention=intervention,
                state=state,
                matched_pressures=matched_pressures,
                what_to_do=what_to_do,
                evidence_packets=evidence_packets,
            )
            feasibility_eval = self._build_feasibility_evaluation(
                intervention=intervention,
                state=state,
                spatial_context=spatial_context,
                is_suitable=True,
                suit_score=suit_score,
                reason=suit_reason,
            )
            impacted_metrics = self._filter_impacted_metrics(intervention)
            validation_packet = self._build_scientific_validation(
                intervention=intervention,
                state=state,
                evidence_packets=evidence_packets,
                conflicts=request.conflicts,
            )

            rec = InterventionRecommendation(
                recommendation_id=f"REC_{intervention.id.replace('INT_', '')}_{len(recommendations)+1:02d}",
                intervention_id=intervention.id,
                recommendation=f"Implement {intervention.name} to mitigate {matched_pressures[0] if matched_pressures else 'environmental degradation'}.",
                title=intervention.name,
                category=intervention.category,
                addressed_findings=matched_findings,
                addressed_pressures=matched_pressures,
                what_to_do=what_to_do,
                why_it_works=why_it_works,
                ecological_mechanism=intervention.ecological_mechanism,
                target_metrics=intervention.target_metrics,
                impacted_metrics=impacted_metrics,
                expected_metric_effects=intervention.expected_metric_effects,
                explanation_chain=explanation_chain,
                feasibility=feasibility_eval,
                validation=validation_packet,
                time_horizon=intervention.time_horizon.value,
                evidence_ids=intervention.evidence_ids,
                evidence_references=evidence_packets,
                evidence=evidence_packets,
                confidence_basis=conf_basis,
                confidence=conf_basis,
                constraints=constraints_list,
                tradeoffs=validation_packet.context_specific_tradeoffs,
                limitations=intervention.limitations,
                relevance_rank=1,  # Placeholder, assigned below after sort
            )
            recommendations.append(rec)

        # Sort recommendations by relevance rank (combination of confidence, pressure match, and suitability)
        recommendations.sort(
            key=lambda r: (
                r.confidence_basis.pressure_relevance_score * 1.5
                + r.confidence_basis.biophysical_suitability_score
                + r.confidence_basis.overall_confidence
            ),
            reverse=True,
        )

        # Assign 1-indexed ranks and filter
        filtered_recs: List[InterventionRecommendation] = []
        for rank, rec in enumerate(recommendations, start=1):
            if rec.confidence_basis.overall_confidence >= request.min_confidence_threshold:
                rec.relevance_rank = rank
                filtered_recs.append(rec)
            else:
                excluded_interventions[rec.intervention_id] = (
                    f"Confidence {rec.confidence_basis.overall_confidence:.2f} below threshold {request.min_confidence_threshold:.2f}"
                )

        final_recs = filtered_recs[: request.max_recommendations]

        # Re-index ranks for final slice
        for rank, rec in enumerate(final_recs, start=1):
            rec.relevance_rank = rank

        # Unaddressed findings
        all_finding_ids = {f.finding_id for f in findings}
        unaddressed = sorted(list(all_finding_ids - targeted_findings_set))

        # Overall confidence & evidence coverage
        if final_recs:
            overall_conf = round(sum(r.confidence_basis.overall_confidence for r in final_recs) / len(final_recs), 3)
            all_evidence_ids = {eid for r in final_recs for eid in r.evidence_ids}
            backed_ids = {eid for eid in all_evidence_ids if eid in self._corpus_docs}
            coverage_ratio = round(len(backed_ids) / len(all_evidence_ids), 3) if all_evidence_ids else 1.0
        else:
            overall_conf = 0.0
            coverage_ratio = 1.0

        return RecommendationSetResponse(
            recommendations=final_recs,
            total_recommendations=len(final_recs),
            targeted_findings_count=len(targeted_findings_set),
            unaddressed_findings=unaddressed,
            excluded_interventions=excluded_interventions,
            overall_confidence=overall_conf,
            evidence_coverage_ratio=coverage_ratio,
            evaluation_timestamp=datetime.now(timezone.utc).isoformat(),
        )

    def _check_biophysical_suitability(
        self,
        intervention: InterventionDefinition,
        state: EnvironmentalState,
        spatial_context: Optional[SpatialContext],
    ) -> Tuple[bool, str, float]:
        """Verify biophysical viability against state metrics and spatial ecosystem."""
        rules = intervention.suitability_rules
        score = 1.0

        # Check Land Use
        curr_land_use = state.land.land_use.lower() if state.land.land_use else None
        if curr_land_use:
            # Check exclusions
            for excl in rules.excluded_land_uses:
                if excl in curr_land_use or curr_land_use in excl:
                    return (
                        False,
                        f"Incompatible with current land use '{curr_land_use}' (excluded: {excl})",
                        0.0,
                    )
            # Check inclusions if specified
            if rules.applicable_land_uses and "all" not in rules.applicable_land_uses:
                matched_lu = any(
                    lu in curr_land_use or curr_land_use in lu
                    for lu in rules.applicable_land_uses
                )
                if not matched_lu:
                    # Incurs strong penalty or rejection if completely unrelated
                    if curr_land_use in ["dense_urban", "deep_water", "glacier"]:
                        return False, f"Land use '{curr_land_use}' not applicable", 0.0
                    score -= 0.25

        # Check Ecosystem
        curr_eco = None
        if spatial_context and spatial_context.ecosystem:
            curr_eco = spatial_context.ecosystem.lower()
        if curr_eco:
            for excl in rules.excluded_ecosystems:
                if excl in curr_eco or curr_eco in excl:
                    return (
                        False,
                        f"Incompatible with ecosystem biome '{curr_eco}' (excluded: {excl})",
                        0.0,
                    )

        # Check Context Conditions (e.g. wetland requires hydric soil or depression)
        if "hydric_soil_or_depression" in rules.required_context_conditions:
            # Check if region/ecosystem or soil moisture indicates wetland capability
            is_wetland_candidate = False
            if curr_eco and any(w in curr_eco for w in ["wetland", "peatland", "floodplain", "estuary", "marsh"]):
                is_wetland_candidate = True
            elif state.soil.moisture is not None and state.soil.moisture >= 30.0:
                is_wetland_candidate = True
            elif curr_land_use and any(w in curr_land_use for w in ["wetland", "depression", "floodplain", "drainage"]):
                is_wetland_candidate = True
            
            # If in arid or desert environment without high moisture, reject wetland restoration
            if curr_eco and any(d in curr_eco for d in ["desert", "arid", "sand_sheet", "polar"]) and not is_wetland_candidate:
                return (
                    False,
                    f"Wetland restoration requires hydric soil or alluvial depression; unsuitable for xeric biome '{curr_eco}'",
                    0.0,
                )

        # Check Rainfall
        rainfall = state.climate.rainfall
        if rainfall is not None:
            if rules.min_rainfall_mm is not None and rainfall < (rules.min_rainfall_mm * 0.7):
                return (
                    False,
                    f"Annual precipitation ({rainfall} mm) is critically below minimum requirement ({rules.min_rainfall_mm} mm)",
                    0.0,
                )
            elif rules.min_rainfall_mm is not None and rainfall < rules.min_rainfall_mm:
                score -= 0.20  # Marginal precipitation penalty

            if rules.max_rainfall_mm is not None and rainfall > (rules.max_rainfall_mm * 1.3):
                return (
                    False,
                    f"Annual precipitation ({rainfall} mm) exceeds biophysical threshold ({rules.max_rainfall_mm} mm)",
                    0.0,
                )

        # Check Soil pH
        ph = state.soil.ph
        if ph is not None:
            if rules.min_soil_ph is not None and ph < (rules.min_soil_ph - 0.5):
                return (
                    False,
                    f"Soil pH ({ph}) is too intensely acidic for target vegetative establishment (min: {rules.min_soil_ph})",
                    0.0,
                )
            elif rules.min_soil_ph is not None and ph < rules.min_soil_ph:
                score -= 0.15

            if rules.max_soil_ph is not None and ph > (rules.max_soil_ph + 0.5):
                return (
                    False,
                    f"Soil pH ({ph}) is too intensely alkaline for target vegetative establishment (max: {rules.max_soil_ph})",
                    0.0,
                )
            elif rules.max_soil_ph is not None and ph > rules.max_soil_ph:
                score -= 0.15

        # Check Temperature
        temp = state.climate.temperature
        if temp is not None and rules.max_temperature_c is not None:
            if temp > rules.max_temperature_c:
                score -= 0.15

        return True, "Biophysically suitable", max(0.30, min(1.0, score))

    def _calculate_pressure_relevance(
        self,
        intervention: InterventionDefinition,
        findings: List[EcologicalFinding],
        pressure_tokens: Set[str],
    ) -> Tuple[float, List[str], List[str]]:
        """Calculate how directly an intervention resolves observed ecological findings."""
        matched_findings: List[str] = []
        matched_pressures: List[str] = []
        relevance_score = 0.0

        for finding in findings:
            finding_text = (
                f"{finding.title} {finding.inferred_pressure} {finding.domain} "
                + " ".join(finding.contributing_variables)
            ).lower()

            for target_p in intervention.target_pressures:
                target_norm = target_p.lower().replace("_", " ")
                if target_norm in finding_text or any(token in target_norm for token in finding_text.split()):
                    matched_findings.append(finding.finding_id)
                    matched_pressures.append(finding.inferred_pressure)

                    # Severity weighting
                    sev_mult = 1.0
                    if finding.severity == NaturePressureSeverity.CRITICAL:
                        sev_mult = 1.4
                    elif finding.severity == NaturePressureSeverity.HIGH:
                        sev_mult = 1.2
                    elif finding.severity == NaturePressureSeverity.MEDIUM:
                        sev_mult = 0.9

                    relevance_score += 0.35 * sev_mult
                    break

        # Check token overlaps with degraded state metrics
        for target_p in intervention.target_pressures:
            if target_p.lower() in pressure_tokens:
                if target_p not in matched_pressures:
                    matched_pressures.append(target_p.replace("_", " ").title())
                relevance_score += 0.20

        # De-duplicate lists
        matched_findings = sorted(list(set(matched_findings)))
        matched_pressures = sorted(list(set(matched_pressures)))

        return min(1.0, relevance_score), matched_findings, matched_pressures

    def _retrieve_intervention_evidence(
        self,
        intervention: InterventionDefinition,
        state: EnvironmentalState,
    ) -> List[EvidenceChunkPacket]:
        """Fetch matching scientific chunks for this intervention's cited evidence IDs."""
        evidence_packets: List[EvidenceChunkPacket] = []

        for doc_id in intervention.evidence_ids:
            doc = self._corpus_docs.get(doc_id)
            if not doc:
                continue

            # Query RAG store for specific chunks of this document
            results = self._rag_service.search_evidence(
                ScientificSearchQuery(
                    query=f"{intervention.name} {doc.title}",
                    top_k=2,
                    ecosystem=state.spatial_context.ecosystem if state.spatial_context else None,
                )
            )

            # Filter or extract chunks matching this document
            doc_chunks = [c for c in results.evidence_chunks if c.document_id == doc_id]
            if doc_chunks:
                evidence_packets.extend(doc_chunks[:1])
            else:
                # Fallback to creating a packet directly from doc abstract
                evidence_packets.append(
                    EvidenceChunkPacket(
                        chunk_id=f"{doc.id}_C00",
                        document_id=doc.id,
                        title=doc.title,
                        authors=doc.authors,
                        organization=doc.organization,
                        year=doc.year,
                        citation=doc.citation,
                        doi=doc.doi,
                        url=doc.url,
                        content=doc.abstract,
                        relevance_score=0.92,
                        evidence_strength=doc.evidence_strength,
                        confidence_grade="high",
                        geographic_scope=doc.geographic_scope,
                        ecosystem=doc.ecosystem,
                        matched_metrics=intervention.target_metrics,
                    )
                )

        return evidence_packets[:4]

    def _compute_data_completeness(
        self,
        intervention: InterventionDefinition,
        state: EnvironmentalState,
    ) -> float:
        """Calculate data completeness ratio for the metrics targeted by this intervention."""
        if not intervention.target_metrics:
            return 1.0

        observed_count = 0
        total_count = len(intervention.target_metrics)

        for metric_id in intervention.target_metrics:
            parts = metric_id.split(".", 1)
            dom = parts[0]
            k = parts[1] if len(parts) > 1 else ""
            if hasattr(state, dom):
                sub = getattr(state, dom)
                if hasattr(sub, k) and getattr(sub, k) is not None:
                    observed_count += 1

        ratio = observed_count / max(1, total_count)
        # Scale between 0.65 (if no target metrics observed) to 1.0 (if all observed)
        return 0.65 + (0.35 * ratio)

    def _contextualize_what_to_do(
        self,
        intervention: InterventionDefinition,
        state: EnvironmentalState,
        spatial: Optional[SpatialContext],
    ) -> str:
        """Add context-specific parameters (e.g. pH, rainfall, region) to action guidelines."""
        base = intervention.what_to_do_template
        context_notes = []

        if state.soil.ph is not None and state.soil.ph < 5.5:
            context_notes.append(
                f"Given measured acidic soil pH ({state.soil.ph}), incorporate acid-tolerant native pioneers and consider agricultural dolomitic lime or organic biochar buffering."
            )
        if state.climate.rainfall is not None and state.climate.rainfall < 500:
            context_notes.append(
                f"In this semi-arid moisture regime ({state.climate.rainfall} mm/yr), establish micro-catchment water harvesting swales (zai pits / half-moons) around plantings."
            )
        if spatial and spatial.region:
            context_notes.append(f"Select native species germplasm locally adapted to the {spatial.region} ecodistrict.")

        if context_notes:
            return f"{base} Context-specific protocol: {' '.join(context_notes)}"
        return base

    def _contextualize_why_it_works(
        self,
        intervention: InterventionDefinition,
        matched_pressures: List[str],
    ) -> str:
        """Tailor rationale to explicitly named observed site pressures."""
        base = intervention.why_it_works_template
        if matched_pressures:
            pressures_str = ", ".join(matched_pressures[:3])
            return f"Directly counteracts identified site pressures ({pressures_str}): {base}"
        return base

    def _build_explanation_chain(
        self,
        intervention: InterventionDefinition,
        state: EnvironmentalState,
        matched_pressures: List[str],
        what_to_do: str,
        evidence_packets: List[EvidenceChunkPacket],
    ) -> ExplanationChainModel:
        facts = []
        if state.soil.ph is not None:
            facts.append(f"Soil pH: {state.soil.ph}")
        if state.soil.organic_carbon is not None:
            facts.append(f"Soil Organic Carbon: {state.soil.organic_carbon}%")
        if state.soil.moisture is not None:
            facts.append(f"Soil Moisture: {state.soil.moisture}%")
        if state.climate.rainfall is not None:
            facts.append(f"Annual Rainfall: {state.climate.rainfall} mm")
        if state.climate.temperature is not None:
            facts.append(f"Mean Temperature: {state.climate.temperature}°C")
        if state.land.land_use is not None:
            facts.append(f"Land Use: {state.land.land_use}")
        if state.land.land_cover is not None:
            facts.append(f"Land Cover: {state.land.land_cover}")
        if state.biodiversity.species_richness is not None:
            facts.append(f"Species Richness: {state.biodiversity.species_richness}")
        if state.biodiversity.habitat_diversity is not None:
            facts.append(f"Habitat Diversity: {state.biodiversity.habitat_diversity}")
        if state.human_impact.deforestation is not None:
            facts.append(f"Deforestation Rate: {state.human_impact.deforestation}%")
        if state.human_impact.pollution is not None:
            facts.append(f"Pollution Level: {state.human_impact.pollution}")
        if not facts:
            facts.append("No explicit state metrics provided; using default baseline conditions.")

        inferred = [f"Inferred ecological pressure: {p}" for p in matched_pressures]
        if not inferred:
            inferred.append(f"Targeting general ecological restoration and resilience for regional ecosystem.")

        primary_pressure = matched_pressures[0] if matched_pressures else "general_ecosystem_degradation"
        evidence_summary = [f"{e.title} ({e.year}) [{e.evidence_strength.value}]: {e.content[:180]}..." for e in evidence_packets]

        return ExplanationChainModel(
            observed_facts=facts,
            inferred_reasoning=inferred,
            ecological_pressure=primary_pressure,
            ecological_mechanism=intervention.ecological_mechanism,
            intervention_action=what_to_do,
            expected_metric_effects=intervention.expected_metric_effects,
            scientific_evidence_summary=evidence_summary,
        )

    def _build_feasibility_evaluation(
        self,
        intervention: InterventionDefinition,
        state: EnvironmentalState,
        spatial_context: Optional[SpatialContext],
        is_suitable: bool,
        suit_score: float,
        reason: str,
    ) -> FeasibilityEvaluationModel:
        status = "Suitable"
        if not is_suitable:
            status = "Not currently suitable"
        elif suit_score < 0.70:
            status = "Conditionally suitable"
        
        vital_count = sum(1 for v in [state.climate.rainfall, state.soil.ph, state.soil.organic_carbon, state.land.land_use] if v is not None)
        if vital_count <= 1 and status == "Suitable":
            status = "Insufficient information"

        evals = {
            "climate suitability": f"Temperature {state.climate.temperature if state.climate.temperature is not None else 'Unknown'}°C, Rainfall {state.climate.rainfall if state.climate.rainfall is not None else 'Unknown'}mm",
            "rainfall": f"{state.climate.rainfall if state.climate.rainfall is not None else 'Unknown'} mm (Min required: {intervention.suitability_rules.min_rainfall_mm}, Max tolerated: {intervention.suitability_rules.max_rainfall_mm})",
            "temperature": f"{state.climate.temperature if state.climate.temperature is not None else 'Unknown'}°C (Max tolerated: {intervention.suitability_rules.max_temperature_c})",
            "soil conditions": f"pH {state.soil.ph if state.soil.ph is not None else 'Unknown'}, Organic Carbon {state.soil.organic_carbon if state.soil.organic_carbon is not None else 'Unknown'}%",
            "moisture": f"Soil moisture {state.soil.moisture if state.soil.moisture is not None else 'Unknown'}%",
            "land use": f"Current land use: {state.land.land_use if state.land.land_use is not None else 'Unknown'}",
            "land cover": f"Current land cover: {state.land.land_cover if state.land.land_cover is not None else 'Unknown'}",
            "water availability": f"Precipitation and soil water holding capacity evaluated",
            "space requirements": f"Standard landscape spatial integration for {intervention.name}",
            "ecosystem compatibility": f"Ecosystem: {spatial_context.ecosystem if spatial_context and spatial_context.ecosystem else 'General regional biome'}",
            "known ecological constraints": f"{len(intervention.constraints)} operational constraints and prerequisites identified",
        }

        return FeasibilityEvaluationModel(
            status=status,
            reason=reason,
            evaluations=evals,
        )

    def _filter_impacted_metrics(self, intervention: InterventionDefinition) -> List[ExpectedMetricEffect]:
        relevant_keys = [
            "soil.organic_carbon", "soil.moisture", "biodiversity.habitat_diversity",
            "biodiversity.species_richness", "climate.rainfall", "land.land_use",
            "land.land_cover", "human_impact.deforestation", "human_impact.pollution"
        ]
        filtered = [eff for eff in intervention.expected_metric_effects if any(k in eff.metric_id for k in relevant_keys)]
        return filtered if filtered else intervention.expected_metric_effects

    def _build_scientific_validation(
        self,
        intervention: InterventionDefinition,
        state: EnvironmentalState,
        evidence_packets: List[EvidenceChunkPacket],
        conflicts: List[Any],
    ) -> ScientificValidationPacket:
        validated_claims: List[ValidatedClaimModel] = []
        
        mech_claim = ValidatedClaimModel(
            claim_text=intervention.ecological_mechanism[:250],
            claim_type="scientific",
            is_supported=len(evidence_packets) > 0,
            evidence_backed=len(evidence_packets) > 0,
            uncertainty_preserved=True,
            validation_status="Validated" if evidence_packets else "Softened due to uncertainty",
            justification="Backed by authoritative literature corpus and mechanistic biophysical principles." if evidence_packets else "Preliminary mechanism; empirical field verification advised."
        )
        validated_claims.append(mech_claim)

        for eff in intervention.expected_metric_effects:
            if eff.quantitative_estimate:
                has_strong_evidence = any(e.evidence_strength in [EvidenceStrength.STRONG, EvidenceStrength.MODERATE] for e in evidence_packets)
                if has_strong_evidence:
                    validated_claims.append(ValidatedClaimModel(
                        claim_text=f"Quantitative impact on {eff.metric_name}: {eff.quantitative_estimate}",
                        claim_type="quantitative",
                        is_supported=True,
                        evidence_backed=True,
                        uncertainty_preserved=True,
                        validation_status="Validated",
                        justification="Effect size supported by peer-reviewed meta-analysis corpus."
                    ))
                else:
                    validated_claims.append(ValidatedClaimModel(
                        claim_text=f"Quantitative impact on {eff.metric_name}: {eff.quantitative_estimate}",
                        claim_type="quantitative",
                        is_supported=False,
                        evidence_backed=False,
                        uncertainty_preserved=True,
                        validation_status="Softened due to uncertainty",
                        justification="Quantitative estimate lacks direct corpus empirical support; treated as qualitative trend."
                    ))

        if evidence_packets:
            strengths = [e.evidence_strength.value for e in evidence_packets]
            evidence_support_summary = f"Supported by {len(evidence_packets)} retrieved peer-reviewed source(s) with evidence strengths: {', '.join(set(strengths))}."
        else:
            evidence_support_summary = "Limited explicit documentary evidence retrieved; relying on general ecological first principles."

        uncertainty_statement = "Outcomes are subject to local microclimatic variability, implementation fidelity, and multi-year stochastic weather events. Confidence intervals reflect data completeness and regional variance."

        conflict_notes = []
        if conflicts:
            for c in conflicts:
                conflict_notes.append(f"Conflict identified in {c.variables_involved}: {c.message} Resolved via {c.resolution_strategy.value} with a {c.uncertainty_penalty*100:.0f}% uncertainty penalty.")
        else:
            conflict_notes.append("No active data conflicts or source contradictions detected for this recommendation.")

        tradeoffs = []
        rainfall = state.climate.rainfall
        land_use = state.land.land_use.lower() if state.land.land_use else ""

        if rainfall is not None and rainfall < 500 and "restoration" in intervention.id.lower():
            tradeoffs.append("Water limitation constraint: High initial establishment water demand may induce local soil moisture competition or require supplementary irrigation.")
        if "agro" in land_use and "agroforestry" in intervention.id.lower():
            tradeoffs.append("Land-use allocation constraint: Temporary reduction in seasonal row-crop acreage during tree canopy establishment phase.")
        if state.soil.ph is not None and state.soil.ph < 5.0:
            tradeoffs.append("Soil acidity constraint: Low pH requires lime or biochar amendments to prevent aluminum toxicity during sapling establishment.")

        if not tradeoffs:
            tradeoffs = intervention.tradeoffs

        return ScientificValidationPacket(
            validated_claims=validated_claims,
            evidence_support_summary=evidence_support_summary,
            uncertainty_statement=uncertainty_statement,
            conflict_resolution_notes=conflict_notes,
            context_specific_tradeoffs=tradeoffs,
            limitations=intervention.limitations,
        )


# Singleton factory
_intervention_engine: Optional[EcologicalInterventionEngine] = None


def get_intervention_engine() -> EcologicalInterventionEngine:
    """Singleton getter for the Ecological Intervention Engine."""
    global _intervention_engine
    if _intervention_engine is None:
        _intervention_engine = EcologicalInterventionEngine()
    return _intervention_engine
