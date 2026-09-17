"""Nature Risk Profile Engine (Phase 6).

Intermediate diagnosis layer between environmental observation and intervention selection.
Deterministic, multi-metric, explainable, and scientific evidence-backed.
Strictly eliminates arbitrary numerical risk scores in favor of discrete, transparent grades:
Low, Medium, High, Unknown.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
from backend.app.core.logging import logger
from backend.app.knowledge.multi_metric_engine import (
    MultiMetricReasoningEngine,
)
from backend.app.knowledge.rag_service import (
    ScientificRAGService,
    get_rag_service,
)
from backend.app.knowledge.reasoning_engine import (
    EcologicalReasoningEngine,
    get_reasoning_engine,
)
from backend.app.schemas.environmental_state import EnvironmentalState
from backend.app.schemas.knowledge import (
    EvidenceStrength,
    ReasoningChain,
    ReasoningChainLink,
)
from backend.app.schemas.risk_profile import (
    ExplainabilityChain,
    ExplainabilityChainStep,
    NatureRiskProfile,
    RiskDimension,
    RiskLevel,
)
from backend.app.schemas.scientific_rag import (
    EvidenceChunkPacket,
    GeographicApplicability,
    MultiMetricAnalysisResponse,
    NaturePressure,
    ScientificSearchQuery,
)


class NatureRiskProfileEngine:
    """Deterministic Nature Risk Profile Diagnostic Engine."""

    def __init__(
        self,
        multi_metric_engine: Optional[MultiMetricReasoningEngine] = None,
        rag_service: Optional[ScientificRAGService] = None,
    ):
        self.rag_service = rag_service or get_rag_service()
        self.multi_metric_engine = multi_metric_engine or MultiMetricReasoningEngine(
            rag_service=self.rag_service
        )

    # ==========================================================================
    # Helper: Build 5-Stage Explainability Chain
    # ==========================================================================

    def _build_explainability_chain(
        self,
        dimension_id: str,
        observed: Dict[str, Any],
        drivers: List[str],
        mechanism: str,
        pressure_name: str,
        evidence_citations: List[str],
    ) -> ExplainabilityChain:
        """Constructs a formal 5-stage machine-readable explainability chain."""
        steps = [
            ExplainabilityChainStep(
                stage="observed_conditions",
                description=f"Directly observed environmental parameters for {dimension_id}",
                details=observed,
            ),
            ExplainabilityChainStep(
                stage="ecological_drivers",
                description="Biophysical stressors resulting from observed baseline conditions",
                details={"drivers": drivers},
            ),
            ExplainabilityChainStep(
                stage="mechanism",
                description="Underlying biological, chemical, or physical process cascade",
                details={"mechanism": mechanism},
            ),
            ExplainabilityChainStep(
                stage="nature_pressure",
                description="Diagnosed ecological vulnerability or degradation state",
                details={"pressure": pressure_name},
            ),
            ExplainabilityChainStep(
                stage="evidence",
                description="Scientific peer-reviewed literature or global assessment backing",
                details={"citations": evidence_citations},
            ),
        ]

        return ExplainabilityChain(
            dimension=dimension_id,
            observed_conditions=observed,
            ecological_drivers=drivers,
            biophysical_mechanism=mechanism,
            nature_pressure=pressure_name,
            evidence_citations=evidence_citations,
            steps=steps,
        )

    # ==========================================================================
    # 1. Dimension: Water Stress
    # ==========================================================================

    def evaluate_water_stress(
        self,
        observed: Dict[str, Any],
        pressures: List[NaturePressure],
        ecosystem: str,
        region: str,
    ) -> RiskDimension:
        """Evaluates hydrologic water stress across rainfall, soil moisture, SOC, and temperature."""
        rainfall = observed.get("climate.rainfall")
        moisture = observed.get("soil.moisture")
        temperature = observed.get("climate.temperature")
        soc = observed.get("soil.organic_carbon")

        contributing = []
        obs_cond = {}
        for k in ["climate.rainfall", "soil.moisture", "climate.temperature", "soil.organic_carbon"]:
            if k in observed:
                contributing.append(k)
                obs_cond[k] = observed[k]

        # Check if insufficient data
        if rainfall is None and moisture is None and temperature is None:
            return RiskDimension(
                dimension_id="water_stress",
                name="Hydrologic & Soil Water Stress",
                level=RiskLevel.UNKNOWN,
                contributing_metrics=contributing,
                observed_conditions=obs_cond,
                inferred_drivers=["Insufficient hydrologic data observed"],
                evidence_ids=[],
                evidence_chunks=[],
                evidence_strength=EvidenceStrength.REQUIRES_EVIDENCE,
                geographic_applicability=GeographicApplicability.GLOBALLY_RELEVANT,
                uncertainty="Rainfall, soil moisture, and ambient temperature are all unmeasured. Risk cannot be reliably inferred.",
                limitations=["Requires at least one hydrologic indicator (annual precipitation, volumetric soil water, or ambient temperature)."],
            )

        # Check if matching multi-metric pressure already computed
        existing_pressure = next(
            (p for p in pressures if p.pressure_type == "thermal_hydro_drought"),
            None,
        )

        drivers: List[str] = []
        mechanisms: List[str] = []
        evidence_ids: List[str] = []
        evidence_chunks: List[EvidenceChunkPacket] = []
        reasoning_chain: Optional[ReasoningChain] = None

        # Determine level deterministically
        level: RiskLevel = RiskLevel.LOW
        uncertainty = "Adequate hydrologic balance observed across moisture and rainfall indicators."

        # High conditions
        is_severe_rainfall = rainfall is not None and rainfall < 550.0
        is_severe_moisture = moisture is not None and moisture < 18.0
        is_high_temp = temperature is not None and temperature > 30.0
        is_low_soc = soc is not None and soc < 1.5

        if (rainfall is not None and rainfall < 600.0 and moisture is not None and moisture < 20.0) or \
           (is_severe_rainfall and is_high_temp) or \
           (is_severe_moisture and is_high_temp) or \
           (is_severe_rainfall and is_severe_moisture):
            level = RiskLevel.HIGH
            drivers.append("Severe hydrologic precipitation deficit")
            drivers.append("Root zone soil moisture exhaustion")
            if is_high_temp:
                drivers.append("Elevated atmospheric vapor pressure deficit (VPD)")
            if is_low_soc:
                drivers.append("Depleted soil organic carbon impairing water holding capacity")

            mech = (
                "Combined precipitation shortfall and high evaporative demand trigger root zone water exhaustion, "
                "inducing plant stomatal closure, xylem cavitation, and severe hydraulic deficit."
            )
            mechanisms.append(mech)
            uncertainty = "Severe stress detected; local sandy soil textures or shallow rooting depths may further accelerate hydraulic failure."

        elif (rainfall is not None and rainfall < 800.0) or \
             (moisture is not None and moisture < 28.0) or \
             (temperature is not None and temperature > 32.0):
            level = RiskLevel.MEDIUM
            if rainfall is not None and rainfall < 800.0:
                drivers.append("Moderate sub-optimal precipitation regime")
            if moisture is not None and moisture < 28.0:
                drivers.append("Marginal soil moisture reserves in topsoil layer")
            if temperature is not None and temperature > 32.0:
                drivers.append("Thermal stress accelerating evapotranspiration")

            mech = "Moderate hydrologic deficit restricts seasonal biomass growth and increases vulnerability to dry spells."
            mechanisms.append(mech)
            uncertainty = "Moderate water stress; seasonal precipitation timing and organic mulching could mitigate deficits."

        else:
            # Low water stress
            drivers.append("Precipitation regime meets or exceeds regional vegetative transpiration demand")
            drivers.append("Adequate soil moisture retention in rooting matrix")
            mech = "Sufficient water availability maintains cellular turgor, uninterrupted transpiration, and nutrient uptake."
            mechanisms.append(mech)

        # Attach evidence and reasoning
        if existing_pressure and level == RiskLevel.HIGH:
            evidence_chunks = existing_pressure.evidence_packet
            evidence_ids = ["DOC_IPCC_WG2_2022_CH2", "DOC_RAWLS_2003_SOIL_WATER", "DOC_LAL_2004_SOIL_CARBON"]
            reasoning_chain = existing_pressure.reasoning_chain
        else:
            # Query scientific RAG if needed
            rag_query = f"water stress soil moisture {rainfall or ''}mm precipitation drought {ecosystem}"
            rag_res = self.rag_service.search_evidence(
                ScientificSearchQuery(
                    query=rag_query,
                    metrics=["climate.rainfall", "soil.moisture"],
                    ecosystem=ecosystem,
                    geographic_scope=region,
                    top_k=4,
                )
            )
            evidence_chunks = rag_res.evidence_chunks
            evidence_ids = [c.document_id for c in rag_res.evidence_chunks]

        citations = [c.citation for c in evidence_chunks]
        explainability = self._build_explainability_chain(
            dimension_id="water_stress",
            observed=obs_cond,
            drivers=drivers,
            mechanism=mechanisms[0] if mechanisms else "Hydrologic equilibrium maintained.",
            pressure_name=f"{level.value.capitalize()} Water Stress",
            evidence_citations=citations,
        )

        limitations = []
        if rainfall is None:
            limitations.append("Rainfall not recorded; evaluated primarily on soil moisture.")
        if moisture is None:
            limitations.append("Soil moisture not recorded; evaluated primarily on macroclimate rainfall.")
        if soc is None:
            limitations.append("Soil organic carbon unknown; soil water retention buffer capacity could not be verified.")

        return RiskDimension(
            dimension_id="water_stress",
            name="Hydrologic & Soil Water Stress",
            level=level,
            contributing_metrics=contributing,
            observed_conditions=obs_cond,
            inferred_drivers=drivers,
            ecological_reasoning_chain=reasoning_chain,
            explainability_chain=explainability,
            evidence_ids=evidence_ids,
            evidence_chunks=evidence_chunks,
            evidence_strength=EvidenceStrength.CONSENSUS if level == RiskLevel.HIGH else EvidenceStrength.STRONG,
            geographic_applicability=GeographicApplicability.GLOBALLY_RELEVANT,
            uncertainty=uncertainty,
            limitations=limitations,
        )

    # ==========================================================================
    # 2. Dimension: Habitat Pressure
    # ==========================================================================

    def evaluate_habitat_pressure(
        self,
        observed: Dict[str, Any],
        pressures: List[NaturePressure],
        ecosystem: str,
        region: str,
    ) -> RiskDimension:
        """Evaluates landscape structural fragmentation, land use intensity, and cover loss."""
        land_use = observed.get("land.land_use")
        land_cover = observed.get("land.land_cover")
        deforestation = observed.get("human_impact.deforestation")
        habitat_div = observed.get("biodiversity.habitat_diversity")

        contributing = []
        obs_cond = {}
        for k in ["land.land_use", "land.land_cover", "human_impact.deforestation", "biodiversity.habitat_diversity"]:
            if k in observed:
                contributing.append(k)
                obs_cond[k] = observed[k]

        if land_use is None and land_cover is None and deforestation is None and habitat_div is None:
            return RiskDimension(
                dimension_id="habitat_pressure",
                name="Habitat Degradation & Structural Simplification",
                level=RiskLevel.UNKNOWN,
                contributing_metrics=contributing,
                observed_conditions=obs_cond,
                inferred_drivers=["Insufficient habitat or land structure data observed"],
                evidence_ids=[],
                evidence_chunks=[],
                evidence_strength=EvidenceStrength.REQUIRES_EVIDENCE,
                geographic_applicability=GeographicApplicability.GLOBALLY_RELEVANT,
                uncertainty="No land use, land cover, deforestation rate, or habitat diversity metrics were provided.",
                limitations=["Requires land cover or land use classification to diagnose structural integrity."],
            )

        existing_pressure = next(
            (p for p in pressures if p.pressure_type in ("habitat_simplification", "anthropogenic_compound_stress")),
            None,
        )

        drivers: List[str] = []
        mechanisms: List[str] = []
        evidence_ids: List[str] = []
        evidence_chunks: List[EvidenceChunkPacket] = []
        reasoning_chain: Optional[ReasoningChain] = None

        level: RiskLevel = RiskLevel.LOW
        uncertainty = "Habitat structure is heterogeneous with low physical disruption."

        # High risk conditions
        is_monoculture = str(land_use).lower() in ("monoculture", "intensive_agriculture", "industrial", "urban")
        is_fragmented_cover = str(land_cover).lower() in ("fragmented_canopy", "barren", "cleared", "degraded")
        is_severe_deforest = deforestation is not None and float(deforestation) > 10.0
        is_very_low_div = habitat_div is not None and float(habitat_div) < 35.0

        if is_monoculture or is_severe_deforest or (is_fragmented_cover and is_very_low_div):
            level = RiskLevel.HIGH
            if is_monoculture:
                drivers.append("Intensive monoculture eliminating non-crop floral niches and microhabitats")
            if is_severe_deforest:
                drivers.append(f"High deforestation rate ({deforestation}%) severing forest core areas")
            if is_fragmented_cover:
                drivers.append("Fragmented canopy cover creating severe edge effects")
            if is_very_low_div:
                drivers.append("Critical habitat structural homogeneity (<35% diversity)")

            mech = (
                "Removal of native vegetation and spatial fragmentation disrupts dispersal corridors, "
                "magnifies desiccating edge effects, and eliminates microclimatic thermal refugia."
            )
            mechanisms.append(mech)
            uncertainty = "High structural pressure; linear features (hedgerows/windbreaks) may provide unmeasured micro-connectivity."

        elif (deforestation is not None and float(deforestation) > 3.0) or \
             (habitat_div is not None and float(habitat_div) < 55.0) or \
             str(land_use).lower() in ("pasture", "conventional_tillage", "plantation"):
            level = RiskLevel.MEDIUM
            if deforestation is not None and float(deforestation) > 3.0:
                drivers.append(f"Moderate deforestation rate ({deforestation}%)")
            if habitat_div is not None and float(habitat_div) < 55.0:
                drivers.append("Moderate habitat structural diversity constraint")
            if str(land_use).lower() in ("pasture", "conventional_tillage", "plantation"):
                drivers.append(f"Simplified land use regime ({land_use})")

            mech = "Moderate structural simplification reduces niche availability for specialized taxa."
            mechanisms.append(mech)
            uncertainty = "Moderate pressure; matrix permeability depends on surrounding landscape matrix quality."

        else:
            drivers.append("Intact or diverse canopy structure supporting structural niches")
            drivers.append("Low direct land transformation and deforestation rate")
            mech = "Multi-layered vegetation provides structural complexity, micro-refugia, and uninterrupted ecological corridors."
            mechanisms.append(mech)

        if existing_pressure and level == RiskLevel.HIGH:
            evidence_chunks = existing_pressure.evidence_packet
            evidence_ids = ["DOC_HADDAD_2015_FRAGMENTATION", "DOC_BENTON_2003_FARMLAND_BIODIV", "DOC_IPBES_GLOBAL_2019"]
            reasoning_chain = existing_pressure.reasoning_chain
        else:
            rag_query = f"habitat fragmentation land use {land_use or ''} deforestation habitat heterogeneity biodiversity"
            rag_res = self.rag_service.search_evidence(
                ScientificSearchQuery(
                    query=rag_query,
                    metrics=["land.land_use", "biodiversity.habitat_diversity"],
                    ecosystem=ecosystem,
                    geographic_scope=region,
                    top_k=4,
                )
            )
            evidence_chunks = rag_res.evidence_chunks
            evidence_ids = [c.document_id for c in rag_res.evidence_chunks]

        citations = [c.citation for c in evidence_chunks]
        explainability = self._build_explainability_chain(
            dimension_id="habitat_pressure",
            observed=obs_cond,
            drivers=drivers,
            mechanism=mechanisms[0] if mechanisms else "Habitat structural integrity intact.",
            pressure_name=f"{level.value.capitalize()} Habitat Pressure",
            evidence_citations=citations,
        )

        limitations = []
        if land_cover is None:
            limitations.append("Land cover satellite classification not provided.")
        if habitat_div is None:
            limitations.append("Fine-scale habitat structural diversity index not measured.")

        return RiskDimension(
            dimension_id="habitat_pressure",
            name="Habitat Degradation & Structural Simplification",
            level=level,
            contributing_metrics=contributing,
            observed_conditions=obs_cond,
            inferred_drivers=drivers,
            ecological_reasoning_chain=reasoning_chain,
            explainability_chain=explainability,
            evidence_ids=evidence_ids,
            evidence_chunks=evidence_chunks,
            evidence_strength=EvidenceStrength.CONSENSUS if level == RiskLevel.HIGH else EvidenceStrength.STRONG,
            geographic_applicability=GeographicApplicability.GLOBALLY_RELEVANT,
            uncertainty=uncertainty,
            limitations=limitations,
        )

    # ==========================================================================
    # 3. Dimension: Biodiversity Pressure
    # ==========================================================================

    def evaluate_biodiversity_pressure(
        self,
        observed: Dict[str, Any],
        pressures: List[NaturePressure],
        ecosystem: str,
        region: str,
    ) -> RiskDimension:
        """Evaluates species richness loss, trophic redundancy collapse, and community simplification."""
        species_rich = observed.get("biodiversity.species_richness")
        habitat_div = observed.get("biodiversity.habitat_diversity")
        land_use = observed.get("land.land_use")
        deforestation = observed.get("human_impact.deforestation")

        contributing = []
        obs_cond = {}
        for k in ["biodiversity.species_richness", "biodiversity.habitat_diversity", "land.land_use", "human_impact.deforestation"]:
            if k in observed:
                contributing.append(k)
                obs_cond[k] = observed[k]

        if species_rich is None and habitat_div is None:
            # When direct biodiversity metrics are unknown, check if severe driver metrics exist
            is_monoculture = str(land_use).lower() in ("monoculture", "intensive_agriculture")
            is_severe_deforest = deforestation is not None and float(deforestation) > 12.0

            if is_monoculture or is_severe_deforest:
                # Inferred moderate/high with explicit high uncertainty
                level = RiskLevel.MEDIUM
                drivers = ["Inferred from intensive land clearing and landscape simplification (direct biodiversity counts missing)"]
                uncertainty = "Direct species inventory is missing. Level is inferred as Medium based on land use; empirical species survey required."
            else:
                return RiskDimension(
                    dimension_id="biodiversity_pressure",
                    name="Biodiversity Depletion & Trophic Collapse Risk",
                    level=RiskLevel.UNKNOWN,
                    contributing_metrics=contributing,
                    observed_conditions=obs_cond,
                    inferred_drivers=["Direct biodiversity metrics (species richness, habitat diversity) not observed"],
                    evidence_ids=[],
                    evidence_chunks=[],
                    evidence_strength=EvidenceStrength.REQUIRES_EVIDENCE,
                    geographic_applicability=GeographicApplicability.GLOBALLY_RELEVANT,
                    uncertainty="Species richness and habitat diversity are unmeasured. Pressure cannot be verified without taxonomic sampling.",
                    limitations=["Requires taxonomic inventory or species richness count to confirm community state."],
                )
        else:
            level = RiskLevel.LOW
            drivers: List[str] = []
            uncertainty = "Species richness and functional group representation are within stable baseline bounds."

            is_low_species = species_rich is not None and float(species_rich) < 35
            is_low_diversity = habitat_div is not None and float(habitat_div) < 35.0
            is_monoculture = str(land_use).lower() in ("monoculture", "intensive_agriculture")

            if is_low_species or (is_low_diversity and is_monoculture) or (species_rich is not None and float(species_rich) < 45 and is_monoculture):
                level = RiskLevel.HIGH
                if is_low_species:
                    drivers.append(f"Severely depleted species richness ({species_rich} taxa)")
                if is_low_diversity:
                    drivers.append(f"Impaired habitat diversity ({habitat_div}%)")
                if is_monoculture:
                    drivers.append("Agronomic monoculture excluding natural competitors and beneficial guilds")

                uncertainty = "High risk of functional extinction and pest outbreak vulnerability due to low trophic redundancy."
            elif (species_rich is not None and float(species_rich) < 60) or (habitat_div is not None and float(habitat_div) < 55.0):
                level = RiskLevel.MEDIUM
                drivers.append("Sub-optimal species richness or functional guild representation")
                uncertainty = "Moderate trophic buffering; sensitive specialist species may have experienced localized extirpation."
            else:
                drivers.append("Healthy species richness supporting functional guild redundancy")
                drivers.append("Sufficient structural niches sustaining pollinators and predators")

        mechanisms = [
            "Erosion of species richness removes ecological redundancy across trophic levels, "
            "impairing pollination stability, pest predation pressure, and nutrient mineralization rates."
        ]

        existing_pressure = next(
            (p for p in pressures if p.pressure_type == "habitat_simplification"),
            None,
        )

        if existing_pressure and level == RiskLevel.HIGH:
            evidence_chunks = existing_pressure.evidence_packet
            evidence_ids = ["DOC_TILMAN_2014_BIODIVERSITY", "DOC_IPBES_GLOBAL_2019", "DOC_BENTON_2003_FARMLAND_BIODIV"]
            reasoning_chain = existing_pressure.reasoning_chain
        else:
            rag_query = f"species richness biodiversity loss ecosystem functioning trophic redundancy {ecosystem}"
            rag_res = self.rag_service.search_evidence(
                ScientificSearchQuery(
                    query=rag_query,
                    metrics=["biodiversity.species_richness", "biodiversity.habitat_diversity"],
                    ecosystem=ecosystem,
                    geographic_scope=region,
                    top_k=4,
                )
            )
            evidence_chunks = rag_res.evidence_chunks
            evidence_ids = [c.document_id for c in rag_res.evidence_chunks]

        citations = [c.citation for c in evidence_chunks]
        explainability = self._build_explainability_chain(
            dimension_id="biodiversity_pressure",
            observed=obs_cond,
            drivers=drivers,
            mechanism=mechanisms[0],
            pressure_name=f"{level.value.capitalize()} Biodiversity Pressure",
            evidence_citations=citations,
        )

        limitations = []
        if species_rich is None:
            limitations.append("Species richness count was missing; inferred from landscape variables.")
        if habitat_div is None:
            limitations.append("Habitat structural diversity metric unrecorded.")

        return RiskDimension(
            dimension_id="biodiversity_pressure",
            name="Biodiversity Depletion & Trophic Collapse Risk",
            level=level,
            contributing_metrics=contributing,
            observed_conditions=obs_cond,
            inferred_drivers=drivers,
            ecological_reasoning_chain=reasoning_chain if 'reasoning_chain' in locals() else None,
            explainability_chain=explainability,
            evidence_ids=evidence_ids,
            evidence_chunks=evidence_chunks,
            evidence_strength=EvidenceStrength.CONSENSUS if level == RiskLevel.HIGH else EvidenceStrength.STRONG,
            geographic_applicability=GeographicApplicability.GLOBALLY_RELEVANT,
            uncertainty=uncertainty,
            limitations=limitations,
        )

    # ==========================================================================
    # 4. Dimension: Climate Exposure
    # ==========================================================================

    def evaluate_climate_exposure(
        self,
        observed: Dict[str, Any],
        pressures: List[NaturePressure],
        ecosystem: str,
        region: str,
    ) -> RiskDimension:
        """Evaluates macroclimatic exposure to extreme temperatures, precipitation anomalies, and thermal stress."""
        temp = observed.get("climate.temperature")
        rainfall = observed.get("climate.rainfall")

        contributing = []
        obs_cond = {}
        for k in ["climate.temperature", "climate.rainfall"]:
            if k in observed:
                contributing.append(k)
                obs_cond[k] = observed[k]

        if temp is None and rainfall is None:
            return RiskDimension(
                dimension_id="climate_exposure",
                name="Climate Extremes & Thermal-Hydro Exposure",
                level=RiskLevel.UNKNOWN,
                contributing_metrics=contributing,
                observed_conditions=obs_cond,
                inferred_drivers=["No temperature or rainfall observations provided"],
                evidence_ids=[],
                evidence_chunks=[],
                evidence_strength=EvidenceStrength.REQUIRES_EVIDENCE,
                geographic_applicability=GeographicApplicability.GLOBALLY_RELEVANT,
                uncertainty="Climate exposure cannot be diagnosed without baseline temperature or rainfall data.",
                limitations=["Requires temperature and precipitation records."],
            )

        level: RiskLevel = RiskLevel.LOW
        drivers: List[str] = []
        uncertainty = "Climatic temperature and rainfall parameters are within standard biophysical tolerances."

        is_extreme_temp = temp is not None and (float(temp) > 33.0 or float(temp) < -15.0)
        is_severe_drought_climate = rainfall is not None and float(rainfall) < 450.0
        is_extreme_deluge = rainfall is not None and float(rainfall) > 3200.0
        is_compound_thermal_hydro = (temp is not None and float(temp) > 29.0) and (rainfall is not None and float(rainfall) < 600.0)

        if is_extreme_temp or is_severe_drought_climate or is_extreme_deluge or is_compound_thermal_hydro:
            level = RiskLevel.HIGH
            if is_extreme_temp:
                drivers.append(f"Thermal extreme ({temp}°C) exceeding optimal vegetative metabolic envelope")
            if is_severe_drought_climate:
                drivers.append(f"Severe meteorological rainfall deficit ({rainfall} mm/yr)")
            if is_extreme_deluge:
                drivers.append(f"Extreme precipitation regime ({rainfall} mm/yr) risking severe runoff and waterlogging")
            if is_compound_thermal_hydro:
                drivers.append("Synergistic high heat and sub-600mm annual precipitation")

            mech = (
                "Extreme climatic exposure exceeds species thermal/hydraulic limits, accelerating evapotranspiration, "
                "inducing photo-inhibition, and increasing mortality of non-adapted taxa."
            )
            uncertainty = "High climate exposure; local microtopography and deep groundwater access may offer partial microclimate buffering."
        elif (temp is not None and float(temp) > 28.0) or (rainfall is not None and float(rainfall) < 750.0):
            level = RiskLevel.MEDIUM
            if temp is not None and float(temp) > 28.0:
                drivers.append(f"Elevated seasonal temperature ({temp}°C)")
            if rainfall is not None and float(rainfall) < 750.0:
                drivers.append(f"Marginal precipitation regime ({rainfall} mm/yr)")

            mech = "Mild climate exposure stresses sensitive flora during peak summer or dry months."
            uncertainty = "Moderate climate exposure; vulnerable during acute heatwave or drought events."
        else:
            drivers.append("Thermal conditions align with regional photosynthetic optimum")
            drivers.append("Favorable precipitation regime sustaining hydrologic cycle")
            mech = "Stable climatic envelope supports baseline productivity without chronic physiological shock."

        rag_query = f"climate change extreme temperature drought rainfall vulnerability IPCC WGII {ecosystem}"
        rag_res = self.rag_service.search_evidence(
            ScientificSearchQuery(
                query=rag_query,
                metrics=["climate.temperature", "climate.rainfall"],
                ecosystem=ecosystem,
                geographic_scope=region,
                top_k=4,
            )
        )
        evidence_chunks = rag_res.evidence_chunks
        evidence_ids = [c.document_id for c in rag_res.evidence_chunks]

        citations = [c.citation for c in evidence_chunks]
        explainability = self._build_explainability_chain(
            dimension_id="climate_exposure",
            observed=obs_cond,
            drivers=drivers,
            mechanism=mech if 'mech' in locals() else "Climatic envelope within safe baseline limits.",
            pressure_name=f"{level.value.capitalize()} Climate Exposure",
            evidence_citations=citations,
        )

        limitations = []
        if temp is None:
            limitations.append("Temperature unmeasured; evaluated solely on precipitation.")
        if rainfall is None:
            limitations.append("Precipitation unmeasured; evaluated solely on temperature.")

        return RiskDimension(
            dimension_id="climate_exposure",
            name="Climate Extremes & Thermal-Hydro Exposure",
            level=level,
            contributing_metrics=contributing,
            observed_conditions=obs_cond,
            inferred_drivers=drivers,
            ecological_reasoning_chain=None,
            explainability_chain=explainability,
            evidence_ids=evidence_ids,
            evidence_chunks=evidence_chunks,
            evidence_strength=EvidenceStrength.CONSENSUS if level == RiskLevel.HIGH else EvidenceStrength.STRONG,
            geographic_applicability=GeographicApplicability.GLOBALLY_RELEVANT,
            uncertainty=uncertainty,
            limitations=limitations,
        )

    # ==========================================================================
    # 5. Dimension: Human Disturbance
    # ==========================================================================

    def evaluate_human_disturbance(
        self,
        observed: Dict[str, Any],
        pressures: List[NaturePressure],
        ecosystem: str,
        region: str,
    ) -> RiskDimension:
        """Evaluates anthropogenic pollution, chemical ecotoxicity, and extractive land clearing."""
        pollution = observed.get("human_impact.pollution")
        deforestation = observed.get("human_impact.deforestation")
        land_use = observed.get("land.land_use")

        contributing = []
        obs_cond = {}
        for k in ["human_impact.pollution", "human_impact.deforestation", "land.land_use"]:
            if k in observed:
                contributing.append(k)
                obs_cond[k] = observed[k]

        # Explicit distinction between 0.0 (observed pristine/zero) vs None (unknown)
        if pollution is None and deforestation is None and land_use is None:
            return RiskDimension(
                dimension_id="human_disturbance",
                name="Anthropogenic Disturbance & Ecotoxicity Pressure",
                level=RiskLevel.UNKNOWN,
                contributing_metrics=contributing,
                observed_conditions=obs_cond,
                inferred_drivers=["No human disturbance metrics (pollution, deforestation, land use) provided"],
                evidence_ids=[],
                evidence_chunks=[],
                evidence_strength=EvidenceStrength.REQUIRES_EVIDENCE,
                geographic_applicability=GeographicApplicability.GLOBALLY_RELEVANT,
                uncertainty="Human impact parameters are unmeasured. Disturbance cannot be determined.",
                limitations=["Requires pollution index or deforestation rate measurements."],
            )

        existing_pressure = next(
            (p for p in pressures if p.pressure_type == "anthropogenic_compound_stress"),
            None,
        )

        level: RiskLevel = RiskLevel.LOW
        drivers: List[str] = []
        uncertainty = "Low anthropogenic disturbance; soil and water systems operate below critical chemical pollution thresholds."

        poll_val = float(pollution) if pollution is not None and isinstance(pollution, (int, float)) else None
        defor_val = float(deforestation) if deforestation is not None and isinstance(deforestation, (int, float)) else None

        is_high_poll = poll_val is not None and poll_val > 25.0
        is_high_defor = defor_val is not None and defor_val > 10.0
        is_industrial_land = str(land_use).lower() in ("industrial", "open_pit_mining", "intensive_urban")
        is_synergistic_disturbance = (poll_val is not None and poll_val > 15.0) and (defor_val is not None and defor_val > 6.0)

        if is_high_poll or is_high_defor or is_industrial_land or is_synergistic_disturbance:
            level = RiskLevel.HIGH
            if is_high_poll:
                drivers.append(f"Elevated pollution index ({poll_val}) inducing chemical ecotoxicity")
            if is_high_defor:
                drivers.append(f"High ongoing deforestation rate ({defor_val}%)")
            if is_industrial_land:
                drivers.append(f"Intensive industrial or extractive land use ({land_use})")
            if is_synergistic_disturbance:
                drivers.append("Coupled spatial clearing and chemical contaminant load")

            mech = (
                "Anthropogenic pollutant deposition and habitat clearing induce biological toxicity, "
                "degrade soil microbiota, and severely disturb natural biogeochemical recycling."
            )
            uncertainty = "High disturbance detected; bioaccumulation rates vary by contaminant type (heavy metals vs synthetic agrochemicals)."
        elif (poll_val is not None and poll_val > 8.0) or (defor_val is not None and defor_val > 3.0):
            level = RiskLevel.MEDIUM
            if poll_val is not None and poll_val > 8.0:
                drivers.append(f"Moderate chronic pollution index ({poll_val})")
            if defor_val is not None and defor_val > 3.0:
                drivers.append(f"Moderate forest clearing rate ({defor_val}%)")

            mech = "Sub-lethal chemical disturbance and edge encroachment reduce population fitness of sensitive taxa."
            uncertainty = "Moderate disturbance; natural buffer zones (e.g. riparian strips) may mitigate runoff toxicity."
        else:
            drivers.append("Pristine or minimal anthropogenic chemical pollutant loading")
            drivers.append("Negligible ongoing deforestation rate")
            mech = "Absence of significant anthropogenic disturbances allows natural regenerative processes to proceed uninhibited."

        if existing_pressure and level == RiskLevel.HIGH:
            evidence_chunks = existing_pressure.evidence_packet
            evidence_ids = ["DOC_UNEP_GEO6_2019", "DOC_IPBES_GLOBAL_2019", "DOC_HADDAD_2015_FRAGMENTATION"]
            reasoning_chain = existing_pressure.reasoning_chain
        else:
            rag_query = f"chemical pollution deforestation human disturbance ecotoxicity {ecosystem} UNEP GEO6"
            rag_res = self.rag_service.search_evidence(
                ScientificSearchQuery(
                    query=rag_query,
                    metrics=["human_impact.pollution", "human_impact.deforestation"],
                    ecosystem=ecosystem,
                    geographic_scope=region,
                    top_k=4,
                )
            )
            evidence_chunks = rag_res.evidence_chunks
            evidence_ids = [c.document_id for c in rag_res.evidence_chunks]

        citations = [c.citation for c in evidence_chunks]
        explainability = self._build_explainability_chain(
            dimension_id="human_disturbance",
            observed=obs_cond,
            drivers=drivers,
            mechanism=mech if 'mech' in locals() else "Anthropogenic footprint remains minimal.",
            pressure_name=f"{level.value.capitalize()} Human Disturbance",
            evidence_citations=citations,
        )

        limitations = []
        if pollution is None:
            limitations.append("Chemical/air/water pollution index was not measured.")
        if deforestation is None:
            limitations.append("Tree cover loss / deforestation rate was not measured.")

        return RiskDimension(
            dimension_id="human_disturbance",
            name="Anthropogenic Disturbance & Ecotoxicity Pressure",
            level=level,
            contributing_metrics=contributing,
            observed_conditions=obs_cond,
            inferred_drivers=drivers,
            ecological_reasoning_chain=reasoning_chain if 'reasoning_chain' in locals() else None,
            explainability_chain=explainability,
            evidence_ids=evidence_ids,
            evidence_chunks=evidence_chunks,
            evidence_strength=EvidenceStrength.CONSENSUS if level == RiskLevel.HIGH else EvidenceStrength.STRONG,
            geographic_applicability=GeographicApplicability.GLOBALLY_RELEVANT,
            uncertainty=uncertainty,
            limitations=limitations,
        )

    # ==========================================================================
    # Main Diagnostic Entrypoint
    # ==========================================================================

    def diagnose_risk_profile(
        self,
        state: EnvironmentalState,
        existing_analysis: Optional[MultiMetricAnalysisResponse] = None,
    ) -> NatureRiskProfile:
        """Produces a comprehensive, evidence-backed Nature Risk Profile without numerical scoring."""
        # Step 1: Obtain or reuse multi-metric reasoning analysis
        if existing_analysis:
            analysis = existing_analysis
        else:
            analysis = self.multi_metric_engine.analyze_environmental_state(state)

        observed = analysis.observed_conditions
        pressures = analysis.pressures

        ecosystem = state.spatial_context.ecosystem if state.spatial_context and state.spatial_context.ecosystem else "all"
        region = state.spatial_context.region if state.spatial_context and state.spatial_context.region else "global"

        # Step 2: Evaluate 5 core risk dimensions
        water_stress = self.evaluate_water_stress(observed, pressures, ecosystem, region)
        habitat_pressure = self.evaluate_habitat_pressure(observed, pressures, ecosystem, region)
        biodiversity_pressure = self.evaluate_biodiversity_pressure(observed, pressures, ecosystem, region)
        climate_exposure = self.evaluate_climate_exposure(observed, pressures, ecosystem, region)
        human_disturbance = self.evaluate_human_disturbance(observed, pressures, ecosystem, region)

        # Step 3: Identify missing important variables
        missing_vars: List[str] = []
        canonical_keys = [
            ("soil.ph", "Soil pH"),
            ("soil.organic_carbon", "Soil Organic Carbon"),
            ("soil.moisture", "Soil Moisture"),
            ("climate.rainfall", "Annual Precipitation"),
            ("climate.temperature", "Mean Temperature"),
            ("land.land_use", "Land Use Classification"),
            ("land.land_cover", "Land Cover Type"),
            ("biodiversity.species_richness", "Species Richness Count"),
            ("biodiversity.habitat_diversity", "Habitat Structural Diversity"),
            ("human_impact.pollution", "Pollution / Ecotoxicity Index"),
            ("human_impact.deforestation", "Deforestation Rate"),
        ]
        for key, name in canonical_keys:
            if key not in observed or observed[key] is None:
                missing_vars.append(f"{name} ({key})")

        # Step 4: Aggregate system-wide limitations
        overall_limitations: List[str] = [
            "Diagnostic assessments are strictly qualitative and deterministic; numerical composite scoring is omitted to prevent overclaiming.",
            "Assessments are grounded in available observed metrics; missing variables are preserved as Unknown rather than assumed zero.",
            "Evidence packets are mapped from curated peer-reviewed studies and global institutional syntheses (IPCC, IPBES, FAO, UNEP).",
        ]
        if missing_vars:
            overall_limitations.append(
                f"{len(missing_vars)} important ecological variables are missing from the input state."
            )

        # Step 5: Deduplicate all attached evidence chunks
        seen_chunks: Set[str] = set()
        evidence_summary: List[EvidenceChunkPacket] = []
        for dim in [water_stress, habitat_pressure, biodiversity_pressure, climate_exposure, human_disturbance]:
            for chunk in dim.evidence_chunks:
                if chunk.chunk_id not in seen_chunks:
                    seen_chunks.add(chunk.chunk_id)
                    evidence_summary.append(chunk)

        return NatureRiskProfile(
            water_stress=water_stress,
            habitat_pressure=habitat_pressure,
            biodiversity_pressure=biodiversity_pressure,
            climate_exposure=climate_exposure,
            human_disturbance=human_disturbance,
            overall_limitations=overall_limitations,
            missing_important_variables=missing_vars,
            evidence_summary=evidence_summary,
            evaluation_timestamp=datetime.now(timezone.utc).isoformat(),
        )


# Singleton factory
_risk_engine: Optional[NatureRiskProfileEngine] = None


def get_risk_engine() -> NatureRiskProfileEngine:
    """Returns singleton instance of NatureRiskProfileEngine."""
    global _risk_engine
    if _risk_engine is None:
        _risk_engine = NatureRiskProfileEngine()
    return _risk_engine
