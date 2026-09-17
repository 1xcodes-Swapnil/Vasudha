"""Deterministic Ecological Relationship & Reasoning Engine (Phase 3).

Executes forward-chaining ecological reasoning over an EnvironmentalState
without reliance on an LLM for scientific truth.

Strictly preserves the distinction between:
- Observed: Value explicitly supplied in EnvironmentalState (including 0.0)
- Inferred: Derived through structured ecological relationships
- Unknown: Insufficient information / None
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from backend.app.schemas.environmental_state import EnvironmentalState
from backend.app.schemas.knowledge import (
    ConditionOperator,
    EcologicalRelationship,
    EnvironmentalMetricDefinition,
    EvidenceMetadata,
    InferredPressure,
    MetricDomain,
    MultiMetricCompoundPressure,
    ReasoningChain,
    ReasoningChainLink,
    ReasoningEvaluationResult,
    VariableObservationState,
    VariableStatus,
)
from backend.app.knowledge.curated_metrics import CURATED_METRICS
from backend.app.knowledge.curated_evidence import CURATED_EVIDENCE
from backend.app.knowledge.curated_relationships import CURATED_RELATIONSHIPS


class EcologicalReasoningEngine:
    """Deterministic forward-chaining ecological relationship engine."""

    def __init__(
        self,
        relationships: Optional[List[EcologicalRelationship]] = None,
        metrics: Optional[List[EnvironmentalMetricDefinition]] = None,
        evidence: Optional[List[EvidenceMetadata]] = None,
    ) -> None:
        self.relationships = relationships if relationships is not None else CURATED_RELATIONSHIPS
        self.metrics = metrics if metrics is not None else CURATED_METRICS
        self.evidence = evidence if evidence is not None else CURATED_EVIDENCE

        # Fast lookup indices
        self.metric_map: Dict[str, EnvironmentalMetricDefinition] = {m.id: m for m in self.metrics}
        self.evidence_map: Dict[str, EvidenceMetadata] = {e.id: e for e in self.evidence}
        self.relationship_map: Dict[str, EcologicalRelationship] = {r.id: r for r in self.relationships}

    # --------------------------------------------------------------------------
    # 1. State Extraction & Observed vs Unknown Tracking
    # --------------------------------------------------------------------------

    def extract_metrics_status(
        self, state: EnvironmentalState
    ) -> Tuple[Dict[str, Any], List[VariableStatus], List[str]]:
        """Extract observed values, distinguishing explicitly present values (including 0) from None (Unknown)."""
        observed: Dict[str, Any] = {}
        statuses: List[VariableStatus] = []
        unknown_metric_ids: List[str] = []

        # Canonical mapping from EnvironmentalState structure to metric IDs
        field_extractors: List[Tuple[str, Any, MetricDomain]] = [
            ("soil.ph", state.soil.ph, MetricDomain.SOIL),
            ("soil.organic_carbon", state.soil.organic_carbon, MetricDomain.SOIL),
            ("soil.moisture", state.soil.moisture, MetricDomain.SOIL),
            ("land.land_use", state.land.land_use, MetricDomain.LAND),
            ("land.land_cover", state.land.land_cover, MetricDomain.LAND),
            ("biodiversity.species_richness", state.biodiversity.species_richness, MetricDomain.BIODIVERSITY),
            ("biodiversity.habitat_diversity", state.biodiversity.habitat_diversity, MetricDomain.BIODIVERSITY),
            ("climate.temperature", state.climate.temperature, MetricDomain.CLIMATE),
            ("climate.rainfall", state.climate.rainfall, MetricDomain.CLIMATE),
            ("human_impact.pollution", state.human_impact.pollution, MetricDomain.HUMAN_IMPACT),
            ("human_impact.deforestation", state.human_impact.deforestation, MetricDomain.HUMAN_IMPACT),
        ]

        for metric_id, val, domain in field_extractors:
            metric_def = self.metric_map.get(metric_id)
            name = metric_def.name if metric_def else metric_id
            unit = metric_def.unit if metric_def else None

            # Critical: distinguish 0 / 0.0 from None (Unknown)
            if val is not None:
                observed[metric_id] = val
                statuses.append(
                    VariableStatus(
                        metric_id=metric_id,
                        name=name,
                        domain=domain,
                        status=VariableObservationState.OBSERVED,
                        observed_value=val,
                        unit=unit,
                    )
                )
            else:
                unknown_metric_ids.append(metric_id)
                statuses.append(
                    VariableStatus(
                        metric_id=metric_id,
                        name=name,
                        domain=domain,
                        status=VariableObservationState.UNKNOWN,
                        observed_value=None,
                        unit=unit,
                    )
                )

        return observed, statuses, unknown_metric_ids

    # --------------------------------------------------------------------------
    # 2. Condition Evaluation
    # --------------------------------------------------------------------------

    def evaluate_condition(
        self,
        value: Any,
        operator: ConditionOperator,
        threshold: Any,
    ) -> bool:
        """Deterministically evaluates a single condition.
        
        Returns False if value is None or incompatible.
        """
        if value is None:
            return False

        try:
            if operator == ConditionOperator.LESS_THAN:
                return float(value) < float(threshold)
            elif operator == ConditionOperator.LESS_THAN_OR_EQUAL:
                return float(value) <= float(threshold)
            elif operator == ConditionOperator.GREATER_THAN:
                return float(value) > float(threshold)
            elif operator == ConditionOperator.GREATER_THAN_OR_EQUAL:
                return float(value) >= float(threshold)
            elif operator in (ConditionOperator.EQUALS, ConditionOperator.CATEGORY_IS):
                return str(value).lower() == str(threshold).lower()
            elif operator == ConditionOperator.NOT_EQUALS:
                return str(value).lower() != str(threshold).lower()
            elif operator == ConditionOperator.IN_LIST:
                if isinstance(threshold, (list, set, tuple)):
                    return str(value).lower() in [str(t).lower() for t in threshold]
                return str(value).lower() == str(threshold).lower()
            elif operator == ConditionOperator.RANGE:
                if isinstance(threshold, (list, tuple)) and len(threshold) == 2:
                    return float(threshold[0]) <= float(value) <= float(threshold[1])
                return False
            return False
        except (ValueError, TypeError):
            return False

    # --------------------------------------------------------------------------
    # 3. Multi-Metric Compound Stresses
    # --------------------------------------------------------------------------

    def evaluate_compound_pressures(
        self, observed: Dict[str, Any]
    ) -> List[MultiMetricCompoundPressure]:
        """Identifies synergistic ecological pressures arising from ≥2 observed variables."""
        compounds: List[MultiMetricCompoundPressure] = []

        # Compound 1: Rainfall Deficit + High Temperature -> Combined Thermal-Hydrological Drought
        rf = observed.get("climate.rainfall")
        temp = observed.get("climate.temperature")
        if rf is not None and temp is not None:
            if rf < 600.0 and temp > 30.0:
                compounds.append(
                    MultiMetricCompoundPressure(
                        compound_id="COMPOUND_THERMAL_HYDRO_DROUGHT",
                        name="Synergistic Thermal-Hydrological Drought Stress",
                        severity="critical",
                        participating_metrics=["climate.rainfall", "climate.temperature"],
                        triggering_conditions={
                            "climate.rainfall": f"{rf} mm/yr (< 600.0)",
                            "climate.temperature": f"{temp} °C (> 30.0)",
                        },
                        synergistic_mechanism=(
                            "High temperature compounds rainfall deficit by exponentially increasing atmospheric "
                            "vapor pressure deficit (VPD). This escalates plant evapotranspiration demand while soil moisture "
                            "reserves are exhausted, precipitating catastrophic xylem cavitation."
                        ),
                        evidence_ids=["IPCC_WG2_2022_CH2", "IPCC_SRCCL_2019"],
                        confidence=0.96,
                    )
                )

        # Compound 2: Low Soil Organic Carbon + Low Rainfall -> Accelerated Agro-Ecological Vulnerability
        soc = observed.get("soil.organic_carbon")
        if soc is not None and rf is not None:
            if soc < 2.0 and rf < 700.0:
                compounds.append(
                    MultiMetricCompoundPressure(
                        compound_id="COMPOUND_SOC_DROUGHT_VULNERABILITY",
                        name="Depleted Soil Water Buffer under Moisture Limitation",
                        severity="high",
                        participating_metrics=["soil.organic_carbon", "climate.rainfall"],
                        triggering_conditions={
                            "soil.organic_carbon": f"{soc} % (< 2.0)",
                            "climate.rainfall": f"{rf} mm/yr (< 700.0)",
                        },
                        synergistic_mechanism=(
                            "Low organic carbon impairs aggregate stability and shrinks available water capacity (AWC). "
                            "When coupled with sub-700mm rainfall, soils lack the buffering capacity to sustain root growth "
                            "between infrequent rain pulses."
                        ),
                        evidence_ids=["RAWLS_2003_SOIL_WATER", "LAL_2004_CARBON"],
                        confidence=0.93,
                    )
                )

        # Compound 3: Monoculture + Low Species Richness -> Agro-Homogenization Trophic Vulnerability
        lu = observed.get("land.land_use")
        sr = observed.get("biodiversity.species_richness")
        if lu is not None and sr is not None:
            if lu == "monoculture" and sr < 40:
                compounds.append(
                    MultiMetricCompoundPressure(
                        compound_id="COMPOUND_MONOCULTURE_BIODIVERSITY_COLLAPSE",
                        name="Agro-Homogenization with Trophic Diversity Collapse",
                        severity="critical",
                        participating_metrics=["land.land_use", "biodiversity.species_richness"],
                        triggering_conditions={
                            "land.land_use": f"{lu} (== monoculture)",
                            "biodiversity.species_richness": f"{sr} (< 40)",
                        },
                        synergistic_mechanism=(
                            "Monocultural landscape structure coupled with an impoverished species pool eliminates "
                            "functional redundancy across pollination and pest-control guilds, predisposing the system "
                            "to runaway pest outbreaks and pollinator deficit."
                        ),
                        evidence_ids=["BENTON_2003_FARMLAND", "TILMAN_2014_BIODIV", "HOOPER_2005_SYNTHESIS"],
                        confidence=0.94,
                    )
                )

        # Compound 4: Deforestation + Pollution -> Cumulative Anthropogenic Habitat & Toxic Degradation
        defor = observed.get("human_impact.deforestation")
        poll = observed.get("human_impact.pollution")
        if defor is not None and poll is not None:
            if defor > 8.0 and poll > 20.0:
                compounds.append(
                    MultiMetricCompoundPressure(
                        compound_id="COMPOUND_ANTHROPOGENIC_SYNERGY",
                        name="Coupled Physical Fragmentation and Chemical Ecotoxicity",
                        severity="critical",
                        participating_metrics=["human_impact.deforestation", "human_impact.pollution"],
                        triggering_conditions={
                            "human_impact.deforestation": f"{defor} % (> 8.0)",
                            "human_impact.pollution": f"{poll} index (> 20.0)",
                        },
                        synergistic_mechanism=(
                            "Physical habitat loss and canopy fragmentation restrict wildlife movement, trapping "
                            "diminished populations within contaminated micro-habitats where toxic chemical exposure "
                            "exacerbates physiological mortality."
                        ),
                        evidence_ids=["UNEP_LAND_DEGRAD_2021", "IPBES_GLOBAL_2019"],
                        confidence=0.95,
                    )
                )

        # Compound 5: Low Soil pH (< 5.5) + Low SOC (< 1.5) -> Severe Root Toxicity & Biological Infertility
        ph = observed.get("soil.ph")
        if ph is not None and soc is not None:
            if ph < 5.5 and soc < 1.5:
                compounds.append(
                    MultiMetricCompoundPressure(
                        compound_id="COMPOUND_ACIDIC_INERT_SOIL",
                        name="Combined Soil Acidity Toxicity and Biological Inertia",
                        severity="high",
                        participating_metrics=["soil.ph", "soil.organic_carbon"],
                        triggering_conditions={
                            "soil.ph": f"{ph} (< 5.5)",
                            "soil.organic_carbon": f"{soc} % (< 1.5)",
                        },
                        synergistic_mechanism=(
                            "Solubilized aluminum (Al3+) inhibits root apical growth while the absence of organic carbon "
                            "deprives soil microorganisms of energy, creating chemically toxic and biologically sterile soil conditions."
                        ),
                        evidence_ids=["PENN_2019_PH_NUTRIENTS", "FAO_SOIL_2020"],
                        confidence=0.92,
                    )
                )

        return compounds

    # --------------------------------------------------------------------------
    # 4. Forward Chaining & Reasoning Evaluation
    # --------------------------------------------------------------------------

    def evaluate_state(self, state: EnvironmentalState) -> ReasoningEvaluationResult:
        """Executes deterministic ecological relationship inference and builds reasoning chains."""
        observed, variables_status, unknown_metric_ids = self.extract_metrics_status(state)

        # Working dynamic state dictionary for forward chaining:
        # Maps metric_id -> set of active values (strings or scalars)
        dynamic_state_values: Dict[str, Set[Any]] = {
            k: {v} for k, v in observed.items()
        }

        inferred_pressures: List[InferredPressure] = []
        fired_rel_ids: Set[str] = set()

        # Chain tracking: list of chains (root_metric, root_val, final_metric, [links])
        active_chains: List[Tuple[str, Any, str, List[ReasoningChainLink]]] = []

        # Forward chaining passes (max depth 5 to support deep ecological cascades)
        max_depth = 5
        for current_depth in range(1, max_depth + 1):
            newly_derived = False

            for rel in self.relationships:
                if rel.id in fired_rel_ids:
                    continue

                source_values = dynamic_state_values.get(rel.source_metric, set())
                if not source_values:
                    continue

                # Check if any active value for source_metric satisfies the condition
                matching_val = None
                for val in source_values:
                    if self.evaluate_condition(val, rel.operator, rel.threshold_value):
                        matching_val = val
                        break

                if matching_val is not None:
                    fired_rel_ids.add(rel.id)
                    newly_derived = True

                    # Record inferred pressure
                    base_id = f"INF_{rel.target_metric.replace('.', '_')}_{rel.target_state}"
                    existing_ids = {p.pressure_id for p in inferred_pressures}
                    if base_id not in existing_ids:
                        pressure_id = base_id
                    else:
                        disambiguated = f"{base_id}_{rel.source_metric.replace('.', '_')}"
                        if disambiguated in existing_ids:
                            disambiguated = f"{base_id}_{rel.id.lower()}"
                        pressure_id = disambiguated

                    condition_str = f"{rel.source_metric} {rel.operator.value} {rel.threshold_value}"

                    severity = "medium"
                    if rel.target_state in ("critical", "severe", "extirpation_risk", "acute"):
                        severity = "critical"
                    elif rel.target_state in ("elevated", "degraded", "restricted", "impaired", "suppressed", "depleted", "genetic_isolation"):
                        severity = "high"
                    elif rel.target_state in ("enhanced", "high", "elevated_heterogeneity"):
                        severity = "low"

                    inferred_pressures.append(
                        InferredPressure(
                            pressure_id=pressure_id,
                            name=rel.name,
                            target_metric=rel.target_metric,
                            inferred_state=rel.target_state,
                            severity=severity,
                            triggering_metric=rel.source_metric,
                            triggering_value=matching_val,
                            condition_matched=condition_str,
                            ecological_mechanism=rel.ecological_mechanism,
                            evidence_ids=rel.evidence_ids,
                            confidence=rel.confidence,
                            chain_depth=current_depth,
                        )
                    )

                    # Update dynamic state
                    if rel.target_metric not in dynamic_state_values:
                        dynamic_state_values[rel.target_metric] = set()
                    dynamic_state_values[rel.target_metric].add(rel.target_state)

                    # Build chain link
                    link = ReasoningChainLink(
                        step=current_depth,
                        from_concept=f"{rel.source_metric} ({matching_val})",
                        to_concept=f"{rel.target_metric} [{rel.target_state}]",
                        relationship_id=rel.id,
                        relationship_type=rel.relationship_type,
                        ecological_mechanism=rel.ecological_mechanism,
                        evidence_ids=rel.evidence_ids,
                    )

                    # Propagate chains: extend any existing chains that ended at source_metric
                    matching_parent_chains = [
                        c for c in active_chains if c[2] == rel.source_metric
                    ]
                    if matching_parent_chains:
                        for p_root_m, p_root_v, _, p_links in matching_parent_chains:
                            active_chains.append(
                                (p_root_m, p_root_v, rel.target_metric, p_links + [link])
                            )
                    else:
                        active_chains.append(
                            (rel.source_metric, matching_val, rel.target_metric, [link])
                        )

            if not newly_derived:
                break

        # Prune prefix chains to keep only maximal/terminal reasoning chains
        maximal_chains: List[Tuple[str, Any, str, List[ReasoningChainLink]]] = []
        for i, chain_i in enumerate(active_chains):
            links_i = [l.relationship_id for l in chain_i[3]]
            is_prefix = False
            for j, chain_j in enumerate(active_chains):
                if i != j:
                    links_j = [l.relationship_id for l in chain_j[3]]
                    if len(links_j) > len(links_i) and links_j[: len(links_i)] == links_i:
                        is_prefix = True
                        break
            if not is_prefix:
                maximal_chains.append(chain_i)

        # Assemble full reasoning chains
        reasoning_chains: List[ReasoningChain] = []
        for idx, (root_metric, root_val, target_key, links) in enumerate(maximal_chains, start=1):
            steps_text = " → ".join([f"{l.to_concept}" for l in links])
            summary = f"Observed [{root_metric} = {root_val}] leads to {steps_text} via {len(links)} validated ecological step(s)."
            reasoning_chains.append(
                ReasoningChain(
                    chain_id=f"CHAIN_{idx:02d}",
                    root_observed_metric=root_metric,
                    root_observed_value=root_val,
                    final_pressure=target_key,
                    links=links,
                    narrative_summary=summary,
                )
            )

        # Multi-metric compound stresses
        compound_pressures = self.evaluate_compound_pressures(observed)

        return ReasoningEvaluationResult(
            observed_metrics=observed,
            variables_status=variables_status,
            inferred_pressures=inferred_pressures,
            compound_pressures=compound_pressures,
            reasoning_chains=reasoning_chains,
            unknown_metrics_count=len(unknown_metric_ids),
            observed_metrics_count=len(observed),
            inferred_pressures_count=len(inferred_pressures),
            evaluation_timestamp=datetime.now(timezone.utc).isoformat(),
        )


# Singleton engine instance
_default_engine: Optional[EcologicalReasoningEngine] = None


def get_reasoning_engine() -> EcologicalReasoningEngine:
    """Provides access to the shared EcologicalReasoningEngine instance."""
    global _default_engine
    if _default_engine is None:
        _default_engine = EcologicalReasoningEngine()
    return _default_engine
