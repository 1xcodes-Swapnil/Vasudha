"""Multi-Metric Ecological Reasoning Engine with Integrated Scientific RAG (Phase 5).

Integrates:
- Structured multi-metric ecological relationship evaluation
- Compound multi-metric stress detection (combining 3+ variables when sufficient data exists)
- Automated Scientific RAG evidence retrieval and compact packet attachment
- Causal reasoning chain synthesis with biophysical mechanism explainability
- Strict preservation of Observed vs Inferred vs Unknown vs Evidence-Backed states
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from backend.app.core.logging import logger
from backend.app.knowledge.reasoning_engine import (
    EcologicalReasoningEngine,
    get_reasoning_engine,
)
from backend.app.knowledge.rag_service import (
    ScientificRAGService,
    get_rag_service,
)
from backend.app.schemas.environmental_state import EnvironmentalState
from backend.app.schemas.knowledge import (
    EvidenceStrength,
    ReasoningChain,
    ReasoningChainLink,
    VariableObservationState,
    VariableStatus,
)
from backend.app.schemas.scientific_rag import (
    EvidenceChunkPacket,
    GeographicApplicability,
    MultiMetricAnalysisResponse,
    NaturePressure,
    NaturePressureSeverity,
    ScientificSearchQuery,
)


class MultiMetricReasoningEngine:
    """Combines deterministic ecological rules with scientific RAG retrieval."""

    def __init__(
        self,
        rule_engine: Optional[EcologicalReasoningEngine] = None,
        rag_service: Optional[ScientificRAGService] = None,
    ):
        self.rule_engine = rule_engine or get_reasoning_engine()
        self.rag_service = rag_service or get_rag_service()

    # --------------------------------------------------------------------------
    # 1. Multi-Metric Compound Stress Evaluation (3+ Variables)
    # --------------------------------------------------------------------------

    def evaluate_multi_metric_pressures(
        self,
        observed: Dict[str, Any],
        spatial_context: Dict[str, Any],
    ) -> List[NaturePressure]:
        """Evaluates complex ecological pressures combining 3+ variables when data permits."""
        pressures: List[NaturePressure] = []

        # Metric extractors
        rainfall = observed.get("climate.rainfall")
        moisture = observed.get("soil.moisture")
        temperature = observed.get("climate.temperature")
        soc = observed.get("soil.organic_carbon")
        ph = observed.get("soil.ph")
        land_use = observed.get("land.land_use")
        land_cover = observed.get("land.land_cover")
        habitat_div = observed.get("biodiversity.habitat_diversity")
        species_rich = observed.get("biodiversity.species_richness")
        deforestation = observed.get("human_impact.deforestation")
        pollution = observed.get("human_impact.pollution")
        ecosystem = spatial_context.get("ecosystem") or "all"
        region = spatial_context.get("region") or "global"

        # ----------------------------------------------------------------------
        # Case 1: Thermal-Hydro Landscape Drought Stress (Rainfall + Moisture + Temperature)
        # ----------------------------------------------------------------------
        if rainfall is not None and moisture is not None and temperature is not None:
            if rainfall < 600.0 and moisture < 20.0 and temperature > 29.0:
                obs_cond = {
                    "climate.rainfall": f"{rainfall} mm/yr (< 600.0)",
                    "soil.moisture": f"{moisture} % (< 20.0)",
                    "climate.temperature": f"{temperature} °C (> 29.0)",
                }
                mechanisms = [
                    "High ambient temperature drives elevated vapor pressure deficit (VPD) and atmospheric evaporative demand.",
                    "Sub-600mm rainfall fails to recharge depleted soil water reserves in the active rooting zone.",
                    "Severe soil moisture deficit (<20%) triggers stomatal closure, xylem cavitation, and canopy hydraulic failure.",
                ]
                # Build RAG query
                query = "compound thermal-hydro drought vapor pressure deficit soil moisture temperature tree mortality"
                rag_resp = self.rag_service.search_evidence(
                    ScientificSearchQuery(
                        query=query,
                        metrics=["climate.rainfall", "soil.moisture", "climate.temperature"],
                        ecosystem=ecosystem,
                        geographic_scope=region,
                        top_k=6,
                    )
                )

                # Assemble reasoning chain
                chain_links = [
                    ReasoningChainLink(
                        step=1,
                        from_concept=f"climate.temperature ({temperature} °C) & climate.rainfall ({rainfall} mm)",
                        to_concept="Atmospheric Evaporative Demand & Hydrologic Deficit",
                        relationship_id="REL_THERMAL_HYDRO_VPD",
                        relationship_type="drives",
                        ecological_mechanism=mechanisms[0],
                        evidence_ids=["DOC_IPCC_WG2_2022_CH2"],
                    ),
                    ReasoningChainLink(
                        step=2,
                        from_concept="Hydrologic Deficit & soil.moisture (<20%)",
                        to_concept="Plant Root Water Stress & Hydraulic Cavitation",
                        relationship_id="REL_HYDRO_CAVITATION",
                        relationship_type="induces",
                        ecological_mechanism=mechanisms[2],
                        evidence_ids=["DOC_RAWLS_2003_SOIL_WATER", "DOC_LAL_2004_SOIL_CARBON"],
                    ),
                ]

                chain = ReasoningChain(
                    chain_id="CHAIN_MULTI_THERMAL_HYDRO_DROUGHT",
                    root_observed_metric="climate.rainfall + soil.moisture + climate.temperature",
                    root_observed_value=f"{rainfall}mm, {moisture}%, {temperature}°C",
                    final_pressure="Thermal-Hydro Landscape Drought Stress",
                    links=chain_links,
                    narrative_summary=(
                        f"Observed rainfall ({rainfall}mm), low soil moisture ({moisture}%), and elevated temperature ({temperature}°C) "
                        f"jointly induce severe thermal-hydro drought stress via elevated atmospheric VPD and root zone cavitation."
                    ),
                )

                pressures.append(
                    NaturePressure(
                        pressure_id="PRESS_THERMAL_HYDRO_DROUGHT",
                        pressure_type="thermal_hydro_drought",
                        name="Compound Thermal-Hydro Landscape Drought Stress",
                        severity=NaturePressureSeverity.CRITICAL,
                        contributing_metrics=["climate.rainfall", "soil.moisture", "climate.temperature"],
                        observed_conditions=obs_cond,
                        inferred_mechanisms=mechanisms,
                        reasoning_chain=chain,
                        evidence_packet=rag_resp.evidence_chunks,
                        evidence_strength=EvidenceStrength.CONSENSUS,
                        confidence=0.95,
                        geographic_applicability=GeographicApplicability.GLOBALLY_RELEVANT,
                        contradictory_evidence_notes=None,
                        uncertainty_and_limitations=[
                            "Drought susceptibility varies depending on local soil texture (sand vs clay) and plant rooting depth."
                        ],
                    )
                )

        # ----------------------------------------------------------------------
        # Case 2: Agro-Homogenization & Trophic Biodiversity Collapse (Land Use + Habitat Diversity + Species Richness)
        # ----------------------------------------------------------------------
        if land_use is not None and habitat_div is not None and species_rich is not None:
            if str(land_use).lower() in ("monoculture", "intensive_agriculture") and habitat_div < 40.0 and species_rich < 40:
                obs_cond = {
                    "land.land_use": f"{land_use} (monoculture)",
                    "biodiversity.habitat_diversity": f"{habitat_div} % (< 40.0)",
                    "biodiversity.species_richness": f"{species_rich} count (< 40)",
                }
                mechanisms = [
                    "Single-crop agronomic management eliminates structural vertical tiers and non-crop floral borders.",
                    "Low habitat diversity (<40%) strips microclimatic refugia and overwintering habitats for natural predators and pollinators.",
                    "Impoverished species richness (<40) removes trophic redundancy, predisposing the system to runaway pest vulnerability and pollination deficit.",
                ]
                rag_resp = self.rag_service.search_evidence(
                    ScientificSearchQuery(
                        query="monoculture habitat heterogeneity species richness trophic collapse farmland biodiversity",
                        metrics=["land.land_use", "biodiversity.habitat_diversity", "biodiversity.species_richness"],
                        ecosystem=ecosystem,
                        geographic_scope=region,
                        top_k=6,
                    )
                )

                chain_links = [
                    ReasoningChainLink(
                        step=1,
                        from_concept=f"land.land_use ({land_use})",
                        to_concept="Landscape Structural Simplification",
                        relationship_id="REL_LAND_SIMPLIFICATION",
                        relationship_type="degrades",
                        ecological_mechanism=mechanisms[0],
                        evidence_ids=["DOC_BENTON_2003_FARMLAND_BIODIV"],
                    ),
                    ReasoningChainLink(
                        step=2,
                        from_concept=f"habitat_diversity ({habitat_div}%) & species_richness ({species_rich})",
                        to_concept="Trophic Multi-Functionality & Redundancy Collapse",
                        relationship_id="REL_TROPHIC_REDUNDANCY_COLLAPSE",
                        relationship_type="limits",
                        ecological_mechanism=mechanisms[2],
                        evidence_ids=["DOC_TILMAN_2014_BIODIVERSITY", "DOC_IPBES_GLOBAL_2019"],
                    ),
                ]

                chain = ReasoningChain(
                    chain_id="CHAIN_MULTI_AGRO_HOMOGENIZATION",
                    root_observed_metric="land.land_use + biodiversity.habitat_diversity + biodiversity.species_richness",
                    root_observed_value=f"{land_use}, {habitat_div}%, {species_rich}",
                    final_pressure="Agro-Homogenization & Trophic Biodiversity Collapse",
                    links=chain_links,
                    narrative_summary=(
                        f"Monocultural cultivation with low habitat diversity ({habitat_div}%) and species richness ({species_rich}) "
                        f"drives trophic redundancy collapse and pollinator/predator guild failure."
                    ),
                )

                pressures.append(
                    NaturePressure(
                        pressure_id="PRESS_AGRO_HOMOGENIZATION",
                        pressure_type="habitat_simplification",
                        name="Agro-Homogenization and Trophic Biodiversity Collapse",
                        severity=NaturePressureSeverity.CRITICAL,
                        contributing_metrics=["land.land_use", "biodiversity.habitat_diversity", "biodiversity.species_richness"],
                        observed_conditions=obs_cond,
                        inferred_mechanisms=mechanisms,
                        reasoning_chain=chain,
                        evidence_packet=rag_resp.evidence_chunks,
                        evidence_strength=EvidenceStrength.CONSENSUS,
                        confidence=0.94,
                        geographic_applicability=GeographicApplicability.GLOBALLY_RELEVANT,
                        contradictory_evidence_notes=None,
                        uncertainty_and_limitations=[
                            "Field-edge hedgerows and wildflower borders can partially buffer against landscape-scale homogenization."
                        ],
                    )
                )

        # ----------------------------------------------------------------------
        # Case 3: Coupled Physical Fragmentation & Ecotoxicity (Deforestation + Land Cover + Pollution)
        # ----------------------------------------------------------------------
        if deforestation is not None and pollution is not None:
            # Check 3-variable combination if land_cover is available, or 2-variable if land_cover is null
            poll_num = float(pollution) if isinstance(pollution, (int, float)) else 0.0
            if deforestation > 8.0 and poll_num > 20.0:
                obs_cond = {
                    "human_impact.deforestation": f"{deforestation} % (> 8.0)",
                    "human_impact.pollution": f"{poll_num} index (> 20.0)",
                }
                metrics_list = ["human_impact.deforestation", "human_impact.pollution"]
                if land_cover:
                    obs_cond["land.land_cover"] = f"{land_cover}"
                    metrics_list.append("land.land_cover")

                mechanisms = [
                    "Canopy removal and fragmentation sever migration corridors and isolate wildlife in remnant patches.",
                    "Elevated pollution creates physiological stress and ecotoxicity in soil and aquatic food webs.",
                    "Synergy: Trapped populations in fragmented patches cannot disperse away from contaminated microhabitats, multiplying localized extirpation risk.",
                ]
                rag_resp = self.rag_service.search_evidence(
                    ScientificSearchQuery(
                        query="habitat fragmentation deforestation chemical pollution ecotoxicity synergy extirpation",
                        metrics=metrics_list,
                        ecosystem=ecosystem,
                        geographic_scope=region,
                        top_k=6,
                    )
                )

                chain_links = [
                    ReasoningChainLink(
                        step=1,
                        from_concept=f"human_impact.deforestation ({deforestation}%)",
                        to_concept="Spatial Habitat Disconnection",
                        relationship_id="REL_DEFOR_DISCONNECTION",
                        relationship_type="induces",
                        ecological_mechanism=mechanisms[0],
                        evidence_ids=["DOC_HADDAD_2015_FRAGMENTATION"],
                    ),
                    ReasoningChainLink(
                        step=2,
                        from_concept=f"human_impact.pollution ({poll_num}) & Spatial Disconnection",
                        to_concept="Compounded Ecotoxicological Extirpation Risk",
                        relationship_id="REL_TOXIC_FRAGMENT_SYNERGY",
                        relationship_type="accelerates",
                        ecological_mechanism=mechanisms[2],
                        evidence_ids=["DOC_UNEP_GEO6_2019", "DOC_IPBES_GLOBAL_2019"],
                    ),
                ]

                chain = ReasoningChain(
                    chain_id="CHAIN_MULTI_ANTHROPOGENIC_SYNERGY",
                    root_observed_metric="human_impact.deforestation + human_impact.pollution",
                    root_observed_value=f"{deforestation}%, {poll_num}",
                    final_pressure="Coupled Physical Fragmentation and Chemical Ecotoxicity",
                    links=chain_links,
                    narrative_summary=(
                        f"Deforestation ({deforestation}%) coupled with elevated pollution ({poll_num}) "
                        f"traps wildlife in isolated, contaminated patches, compounding extirpation risk."
                    ),
                )

                pressures.append(
                    NaturePressure(
                        pressure_id="PRESS_ANTHROPOGENIC_SYNERGY",
                        pressure_type="anthropogenic_compound_stress",
                        name="Coupled Physical Fragmentation and Chemical Ecotoxicity",
                        severity=NaturePressureSeverity.CRITICAL,
                        contributing_metrics=metrics_list,
                        observed_conditions=obs_cond,
                        inferred_mechanisms=mechanisms,
                        reasoning_chain=chain,
                        evidence_packet=rag_resp.evidence_chunks,
                        evidence_strength=EvidenceStrength.CONSENSUS,
                        confidence=0.93,
                        geographic_applicability=GeographicApplicability.GLOBALLY_RELEVANT,
                        contradictory_evidence_notes=None,
                        uncertainty_and_limitations=[
                            "Ecotoxicological sensitivity varies widely across taxa; amphibians and aquatic invertebrates exhibit higher vulnerability."
                        ],
                    )
                )

        # ----------------------------------------------------------------------
        # Case 4: Soil Acidity, Carbon Depletion & Biological Infertility (pH + SOC + Moisture)
        # ----------------------------------------------------------------------
        if ph is not None and soc is not None:
            if ph < 5.5 and soc < 1.5:
                obs_cond = {
                    "soil.ph": f"{ph} (< 5.5)",
                    "soil.organic_carbon": f"{soc} % (< 1.5)",
                }
                metrics_list = ["soil.ph", "soil.organic_carbon"]
                if moisture is not None:
                    obs_cond["soil.moisture"] = f"{moisture} %"
                    metrics_list.append("soil.moisture")

                mechanisms = [
                    "Soil pH < 5.5 solubilizes toxic monomeric Al3+ ions that inhibit root elongation and precipitate phosphorus.",
                    "Soil organic carbon < 1.5% starves heterotrophic microbes and collapses soil aggregate stability.",
                    "Synergy: Root growth inhibition combined with biological starvation creates sterile, non-resilient soil conditions.",
                ]
                rag_resp = self.rag_service.search_evidence(
                    ScientificSearchQuery(
                        query="soil acidity aluminum toxicity phosphorus fixation soil organic carbon microbial biomass",
                        metrics=metrics_list,
                        ecosystem=ecosystem,
                        geographic_scope=region,
                        top_k=6,
                    )
                )

                chain_links = [
                    ReasoningChainLink(
                        step=1,
                        from_concept=f"soil.ph ({ph})",
                        to_concept="Aluminum Solubilization & Root Toxicity",
                        relationship_id="REL_ACIDITY_ALUMINUM",
                        relationship_type="inhibits",
                        ecological_mechanism=mechanisms[0],
                        evidence_ids=["DOC_PENN_2019_PH_NUTRIENTS"],
                    ),
                    ReasoningChainLink(
                        step=2,
                        from_concept=f"soil.organic_carbon ({soc}%)",
                        to_concept="Microbial Starvation & Biological Infertility",
                        relationship_id="REL_SOC_BIOLOGICAL_INERTIA",
                        relationship_type="suppresses",
                        ecological_mechanism=mechanisms[1],
                        evidence_ids=["DOC_FAO_SOIL_STATUS_2020"],
                    ),
                ]

                chain = ReasoningChain(
                    chain_id="CHAIN_MULTI_ACIDIC_INERT_SOIL",
                    root_observed_metric="soil.ph + soil.organic_carbon",
                    root_observed_value=f"pH {ph}, SOC {soc}%",
                    final_pressure="Combined Soil Acidity Toxicity and Biological Inertia",
                    links=chain_links,
                    narrative_summary=(
                        f"Soil acidity (pH {ph}) and low organic carbon ({soc}%) jointly induce "
                        f"aluminum toxicity, phosphorus fixation, and microbial biological inertia."
                    ),
                )

                pressures.append(
                    NaturePressure(
                        pressure_id="PRESS_ACIDIC_INERT_SOIL",
                        pressure_type="soil_degradation",
                        name="Combined Soil Acidity Toxicity and Biological Inertia",
                        severity=NaturePressureSeverity.HIGH,
                        contributing_metrics=metrics_list,
                        observed_conditions=obs_cond,
                        inferred_mechanisms=mechanisms,
                        reasoning_chain=chain,
                        evidence_packet=rag_resp.evidence_chunks,
                        evidence_strength=EvidenceStrength.STRONG,
                        confidence=0.92,
                        geographic_applicability=GeographicApplicability.GLOBALLY_RELEVANT,
                        contradictory_evidence_notes=None,
                        uncertainty_and_limitations=[
                            "Liming and organic amendment responses depend on soil buffering capacity and clay mineralogy."
                        ],
                    )
                )

        return pressures

    # --------------------------------------------------------------------------
    # 2. Comprehensive Multi-Metric Analysis Pipeline
    # --------------------------------------------------------------------------

    def analyze_environmental_state(
        self,
        state: EnvironmentalState,
    ) -> MultiMetricAnalysisResponse:
        """Executes full Multi-Metric Reasoning + Scientific RAG Pipeline."""
        # 1. Evaluate deterministic rule engine
        rule_eval = self.rule_engine.evaluate_state(state)
        observed = rule_eval.observed_metrics
        variables_status = rule_eval.variables_status

        # Extract spatial context
        spatial_dict: Dict[str, Any] = {}
        if state.spatial_context:
            spatial_dict = {
                "latitude": state.spatial_context.latitude,
                "longitude": state.spatial_context.longitude,
                "region": state.spatial_context.region,
                "ecosystem": state.spatial_context.ecosystem,
            }

        # 2. Multi-Metric Compound Pressures
        multi_metric_pressures = self.evaluate_multi_metric_pressures(observed, spatial_dict)

        # 3. For any individual inferred pressures not captured in multi-metric compounds,
        # attach relevant scientific RAG evidence
        all_pressures: List[NaturePressure] = list(multi_metric_pressures)
        covered_metrics: Set[str] = set()
        for mp in multi_metric_pressures:
            covered_metrics.update(mp.contributing_metrics)

        for inf in rule_eval.inferred_pressures:
            if inf.triggering_metric in covered_metrics and inf.severity in ("low", "medium"):
                continue

            # Query scientific RAG for this specific pressure
            rag_query = f"{inf.triggering_metric} {inf.target_metric} {inf.inferred_state} {inf.ecological_mechanism[:60]}"
            rag_resp = self.rag_service.search_evidence(
                ScientificSearchQuery(
                    query=rag_query,
                    metrics=[inf.triggering_metric, inf.target_metric],
                    ecosystem=spatial_dict.get("ecosystem"),
                    geographic_scope=spatial_dict.get("region"),
                    top_k=5,
                )
            )

            # Match reasoning chain if exists
            matching_chain = next(
                (c for c in rule_eval.reasoning_chains if c.root_observed_metric == inf.triggering_metric),
                None,
            )

            sev_enum = NaturePressureSeverity.MEDIUM
            if inf.severity == "critical":
                sev_enum = NaturePressureSeverity.CRITICAL
            elif inf.severity == "high":
                sev_enum = NaturePressureSeverity.HIGH
            elif inf.severity == "low":
                sev_enum = NaturePressureSeverity.LOW

            existing_pids = {p.pressure_id for p in all_pressures}
            final_pid = inf.pressure_id
            if final_pid in existing_pids:
                final_pid = f"{inf.pressure_id}_{inf.triggering_metric.replace('.', '_')}"
                if final_pid in existing_pids:
                    final_pid = f"{inf.pressure_id}_{len(all_pressures)}"

            all_pressures.append(
                NaturePressure(
                    pressure_id=final_pid,
                    pressure_type=inf.target_metric.replace("derived.", ""),
                    name=inf.name,
                    severity=sev_enum,
                    contributing_metrics=[inf.triggering_metric],
                    observed_conditions={inf.triggering_metric: inf.triggering_value},
                    inferred_mechanisms=[inf.ecological_mechanism],
                    reasoning_chain=matching_chain,
                    evidence_packet=rag_resp.evidence_chunks,
                    evidence_strength=EvidenceStrength.STRONG,
                    confidence=inf.confidence,
                    geographic_applicability=GeographicApplicability.GLOBALLY_RELEVANT,
                    contradictory_evidence_notes=None,
                    uncertainty_and_limitations=[
                        f"Single-metric rule for {inf.triggering_metric}; accuracy increases when combined with complementary environmental indicators."
                    ],
                )
            )

        # 4. Unknown metrics extraction
        unknown_metric_ids = [
            v.metric_id for v in variables_status if v.status == VariableObservationState.UNKNOWN
        ]

        # 5. System limitations statement
        system_limitations = [
            "LLM is not used as a scientific source of truth; all relationships are derived from deterministic rules and grounded in cited peer-reviewed publications.",
            "Evidence applicability is weighted according to geographic and biome relevance.",
            f"Missing {len(unknown_metric_ids)} environmental indicators are treated as unknown rather than zero.",
        ]

        total_evidence_chunks = sum(len(p.evidence_packet) for p in all_pressures)

        return MultiMetricAnalysisResponse(
            observed_conditions=observed,
            variables_status=variables_status,
            pressures=all_pressures,
            multi_metric_synergies=rule_eval.compound_pressures,
            reasoning_chains=rule_eval.reasoning_chains,
            total_evidence_chunks_attached=total_evidence_chunks,
            observed_metrics_count=len(observed),
            unknown_metrics_count=len(unknown_metric_ids),
            system_limitations=system_limitations,
            evaluation_timestamp=datetime.now(timezone.utc).isoformat(),
        )


# Singleton factory
_multi_metric_engine_instance: Optional[MultiMetricReasoningEngine] = None


def get_multi_metric_engine() -> MultiMetricReasoningEngine:
    """Returns singleton instance of MultiMetricReasoningEngine."""
    global _multi_metric_engine_instance
    if _multi_metric_engine_instance is None:
        _multi_metric_engine_instance = MultiMetricReasoningEngine()
    return _multi_metric_engine_instance
