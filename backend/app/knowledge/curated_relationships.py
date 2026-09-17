"""Curated deterministic ecological relationships for the Knowledge Base & Reasoning Engine (Phase 3).

Contains 35 peer-reviewed, empirically backed ecological rules modeling biophysical
and landscape mechanisms across Soil, Land, Biodiversity, Climate, and Human Impact.
"""

from typing import List
from backend.app.schemas.knowledge import (
    EcologicalRelationship,
    ConditionOperator,
    RelationshipDirection,
    EvidenceStrength,
)

CURATED_RELATIONSHIPS: List[EcologicalRelationship] = [
    # ==========================================================================
    # SOIL ORGANIC CARBON & BIOLOGY
    # ==========================================================================
    EcologicalRelationship(
        id="REL_SOC_BIOLOGICAL_ACTIVITY",
        name="Soil Organic Carbon Depletion Suppresses Biological Activity",
        source_metric="soil.organic_carbon",
        operator=ConditionOperator.LESS_THAN,
        threshold_value=1.5,
        target_metric="derived.soil_biological_activity",
        target_state="degraded",
        relationship_type="inhibits",
        direction=RelationshipDirection.POSITIVE,
        ecological_mechanism=(
            "Soil organic carbon is the primary substrate and energy source for subterranean heterotrophic microbes. "
            "Depletion below 1.5% restricts microbial biomass turnover, inhibits mycorrhizal fungal networks, "
            "and limits enzymatic mineralization of organic nitrogen and phosphorus."
        ),
        evidence_ids=["FAO_SOIL_2020", "LAL_2004_CARBON"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        confidence=0.95,
        ecosystem_context="all",
        quality_metadata={"domain": "soil", "consensus_tier": 1},
    ),
    EcologicalRelationship(
        id="REL_SOC_WATER_RETENTION_LOW",
        name="Low Soil Organic Carbon Reduces Water Retention",
        source_metric="soil.organic_carbon",
        operator=ConditionOperator.LESS_THAN,
        threshold_value=2.0,
        target_metric="derived.soil_water_retention",
        target_state="reduced",
        relationship_type="degrades",
        direction=RelationshipDirection.POSITIVE,
        ecological_mechanism=(
            "Humic substances and organic macroaggregates govern soil capillary porosity and specific surface area. "
            "When organic carbon drops below 2.0%, soil bulk density increases and available water capacity (AWC) "
            "contracts significantly, accelerating runoff and dry-down rates."
        ),
        evidence_ids=["RAWLS_2003_SOIL_WATER", "LAL_2004_CARBON"],
        evidence_strength=EvidenceStrength.STRONG,
        confidence=0.92,
        ecosystem_context="all",
        quality_metadata={"domain": "soil", "consensus_tier": 1},
    ),
    EcologicalRelationship(
        id="REL_SOC_WATER_RETENTION_HIGH",
        name="High Soil Organic Carbon Enhances Moisture Buffering",
        source_metric="soil.organic_carbon",
        operator=ConditionOperator.GREATER_THAN_OR_EQUAL,
        threshold_value=3.5,
        target_metric="derived.soil_water_retention",
        target_state="enhanced",
        relationship_type="enhances",
        direction=RelationshipDirection.POSITIVE,
        ecological_mechanism=(
            "High organic carbon fractions form spongy organo-mineral complexes with superior intra-aggregate pore volume, "
            "increasing plant-available water holding capacity by 1.5-2.0% per 1% SOC increase."
        ),
        evidence_ids=["RAWLS_2003_SOIL_WATER"],
        evidence_strength=EvidenceStrength.STRONG,
        confidence=0.90,
        ecosystem_context="all",
        quality_metadata={"domain": "soil", "consensus_tier": 1},
    ),

    # ==========================================================================
    # SOIL MOISTURE & PLANT STRESS
    # ==========================================================================
    EcologicalRelationship(
        id="REL_SOIL_MOISTURE_DEFICIT",
        name="Severe Soil Moisture Deficit Induces Plant Hydraulic Stress",
        source_metric="soil.moisture",
        operator=ConditionOperator.LESS_THAN,
        threshold_value=15.0,
        target_metric="derived.plant_water_stress",
        target_state="acute",
        relationship_type="induces",
        direction=RelationshipDirection.NEGATIVE,
        ecological_mechanism=(
            "Volumetric soil water dropping below permanent wilting thresholds collapses xylem water potentials, "
            "forcing stomatal closure, suppressing net carbon assimilation, and triggering cavitation risk."
        ),
        evidence_ids=["IPCC_WG2_2022_CH2"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        confidence=0.94,
        ecosystem_context="all",
        quality_metadata={"domain": "soil", "consensus_tier": 1},
    ),
    EcologicalRelationship(
        id="REL_SOIL_MOISTURE_WATERLOGGED",
        name="Soil Saturation Induces Root Anoxia Stress",
        source_metric="soil.moisture",
        operator=ConditionOperator.GREATER_THAN,
        threshold_value=85.0,
        target_metric="derived.plant_water_stress",
        target_state="anoxic_root_stress",
        relationship_type="inhibits",
        direction=RelationshipDirection.NON_LINEAR,
        ecological_mechanism=(
            "Persistent saturation displaces gas from macropores, creating anaerobic conditions that halt aerobic "
            "mitochondrial root respiration, accumulating toxic ethanol and sulfides."
        ),
        evidence_ids=["FAO_SOIL_2020"],
        evidence_strength=EvidenceStrength.STRONG,
        confidence=0.88,
        ecosystem_context="all",
        quality_metadata={"domain": "soil", "consensus_tier": 2},
    ),

    # ==========================================================================
    # SOIL PH & NUTRIENT AVAILABILITY
    # ==========================================================================
    EcologicalRelationship(
        id="REL_SOIL_PH_ACIDIC",
        name="Strong Soil Acidity Locks Nutrients and Induces Aluminum Toxicity",
        source_metric="soil.ph",
        operator=ConditionOperator.LESS_THAN,
        threshold_value=5.5,
        target_metric="derived.nutrient_availability",
        target_state="acid_restricted",
        relationship_type="inhibits",
        direction=RelationshipDirection.NON_LINEAR,
        ecological_mechanism=(
            "At pH < 5.5, phytotoxic trivalent aluminum (Al3+) solubilizes, stunting root apical elongation. "
            "Simultaneously, orthophosphates precipitate into insoluble aluminum and iron phosphate complexes, "
            "severely restricting phosphorus bio-availability."
        ),
        evidence_ids=["PENN_2019_PH_NUTRIENTS", "FAO_SOIL_2020"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        confidence=0.96,
        ecosystem_context="all",
        quality_metadata={"domain": "soil", "consensus_tier": 1},
    ),
    EcologicalRelationship(
        id="REL_SOIL_PH_ALKALINE",
        name="Alkaline Soil pH Impairs Micronutrient Solubility",
        source_metric="soil.ph",
        operator=ConditionOperator.GREATER_THAN,
        threshold_value=8.2,
        target_metric="derived.nutrient_availability",
        target_state="alkaline_restricted",
        relationship_type="inhibits",
        direction=RelationshipDirection.NON_LINEAR,
        ecological_mechanism=(
            "Alkaline carbonate equilibrium at pH > 8.2 forces precipitation of calcium carbonate and insoluble "
            "calcium phosphates, drastically reducing the solubility and uptake of iron, zinc, and manganese."
        ),
        evidence_ids=["PENN_2019_PH_NUTRIENTS"],
        evidence_strength=EvidenceStrength.STRONG,
        confidence=0.91,
        ecosystem_context="all",
        quality_metadata={"domain": "soil", "consensus_tier": 1},
    ),

    # ==========================================================================
    # CLIMATE: RAINFALL & TEMPERATURE
    # ==========================================================================
    EcologicalRelationship(
        id="REL_RAINFALL_DEFICIT",
        name="Low Annual Precipitation Restricts Landscape Water Availability",
        source_metric="climate.rainfall",
        operator=ConditionOperator.LESS_THAN,
        threshold_value=500.0,
        target_metric="derived.water_availability",
        target_state="deficit",
        relationship_type="limits",
        direction=RelationshipDirection.POSITIVE,
        ecological_mechanism=(
            "Annual precipitation below 500 mm limits groundwater recharge, reduces seasonal streamflow duration, "
            "and constrains aboveground net primary production (ANPP) to drought-adapted xerophytic flora."
        ),
        evidence_ids=["IPCC_SRCCL_2019", "IPCC_WG2_2022_CH2"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        confidence=0.93,
        ecosystem_context="all",
        quality_metadata={"domain": "climate", "consensus_tier": 1},
    ),
    EcologicalRelationship(
        id="REL_TEMPERATURE_HEAT_STRESS",
        name="High Ambient Temperature Amplifies Evaporative and Thermal Stress",
        source_metric="climate.temperature",
        operator=ConditionOperator.GREATER_THAN,
        threshold_value=32.0,
        target_metric="derived.climate_thermal_stress",
        target_state="elevated",
        relationship_type="induces",
        direction=RelationshipDirection.POSITIVE,
        ecological_mechanism=(
            "Temperatures above 32°C exponentially increase atmospheric vapor pressure deficit (VPD), accelerating "
            "transpirational draw while provoking protein denaturation and photoinhibition in non-adapted vegetation."
        ),
        evidence_ids=["IPCC_WG2_2022_CH2"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        confidence=0.92,
        ecosystem_context="all",
        quality_metadata={"domain": "climate", "consensus_tier": 1},
    ),
    EcologicalRelationship(
        id="REL_TEMPERATURE_FREEZING_STRESS",
        name="Sub-Zero Temperature Induces Freezing and Metabolic Stasis",
        source_metric="climate.temperature",
        operator=ConditionOperator.LESS_THAN,
        threshold_value=0.0,
        target_metric="derived.climate_thermal_stress",
        target_state="frost_freeze_stress",
        relationship_type="inhibits",
        direction=RelationshipDirection.POSITIVE,
        ecological_mechanism=(
            "Freezing temperatures cause extracellular ice crystallization and cellular dehydration in non-dormant tissue, "
            "limiting biological enzymatic kinetics and sap movement."
        ),
        evidence_ids=["IPCC_WG2_2022_CH2"],
        evidence_strength=EvidenceStrength.STRONG,
        confidence=0.90,
        ecosystem_context="all",
        quality_metadata={"domain": "climate", "consensus_tier": 1},
    ),

    # ==========================================================================
    # LAND USE: MONOCULTURE & SIMPLIFICATION
    # ==========================================================================
    EcologicalRelationship(
        id="REL_MONOCULTURE_HABITAT_HETEROGENEITY",
        name="Monoculture Cultivation Depresses Landscape Heterogeneity",
        source_metric="land.land_use",
        operator=ConditionOperator.EQUALS,
        threshold_value="monoculture",
        target_metric="derived.habitat_heterogeneity",
        target_state="simplified",
        relationship_type="degrades",
        direction=RelationshipDirection.NEGATIVE,
        ecological_mechanism=(
            "Single-crop agronomic management strips structural vertical tiers, removes non-crop floral borders, "
            "and creates uniform phenological cycles that eliminate spatial and microclimatic refugia."
        ),
        evidence_ids=["BENTON_2003_FARMLAND", "IPBES_GLOBAL_2019"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        confidence=0.95,
        ecosystem_context="all",
        quality_metadata={"domain": "land", "consensus_tier": 1},
    ),
    EcologicalRelationship(
        id="REL_MONOCULTURE_HABITAT_DIVERSITY",
        name="Monoculture Lowers Structural Habitat Diversity",
        source_metric="land.land_use",
        operator=ConditionOperator.EQUALS,
        threshold_value="monoculture",
        target_metric="biodiversity.habitat_diversity",
        target_state="suppressed",
        relationship_type="inhibits",
        direction=RelationshipDirection.NEGATIVE,
        ecological_mechanism=(
            "Homogenization of canopy heights, root profiles, and soil tillage regimes eradicates micro-habitats "
            "required by diverse trophic guilds, suppressing measured structural habitat diversity."
        ),
        evidence_ids=["BENTON_2003_FARMLAND", "TSCHARNTKE_2012_LANDSCAPE"],
        evidence_strength=EvidenceStrength.STRONG,
        confidence=0.92,
        ecosystem_context="all",
        quality_metadata={"domain": "land", "consensus_tier": 1},
    ),
    EcologicalRelationship(
        id="REL_AGROFORESTRY_HABITAT_HETEROGENEITY",
        name="Agroforestry Enhances Landscape Heterogeneity",
        source_metric="land.land_use",
        operator=ConditionOperator.EQUALS,
        threshold_value="agroforestry",
        target_metric="derived.habitat_heterogeneity",
        target_state="elevated",
        relationship_type="enhances",
        direction=RelationshipDirection.POSITIVE,
        ecological_mechanism=(
            "Multi-strata agroforestry integrates woody perennials with crops, providing vertical canopy stratification, "
            "perennial root architecture, and diverse leaf litter substrates."
        ),
        evidence_ids=["BENTON_2003_FARMLAND", "FAO_SOIL_2020"],
        evidence_strength=EvidenceStrength.STRONG,
        confidence=0.89,
        ecosystem_context="all",
        quality_metadata={"domain": "land", "consensus_tier": 2},
    ),
    EcologicalRelationship(
        id="REL_INTENSIVE_AG_SOC_LOSS",
        name="Intensive Agriculture Accelerates Soil Organic Carbon Loss",
        source_metric="land.land_use",
        operator=ConditionOperator.EQUALS,
        threshold_value="intensive_agriculture",
        target_metric="derived.soil_biological_activity",
        target_state="depleted",
        relationship_type="degrades",
        direction=RelationshipDirection.NEGATIVE,
        ecological_mechanism=(
            "Frequent inversion tillage aerates aggregates and exposes previously protected organic carbon to microbial oxidation, "
            "exceeding organic carbon replenishment rates and destabilizing biological activity."
        ),
        evidence_ids=["LAL_2004_CARBON", "FAO_SOIL_2020"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        confidence=0.91,
        ecosystem_context="all",
        quality_metadata={"domain": "land", "consensus_tier": 1},
    ),

    # ==========================================================================
    # HABITAT DIVERSITY → ECOLOGICAL NICHES → SPECIES RICHNESS (MULTI-STEP CHAIN)
    # ==========================================================================
    EcologicalRelationship(
        id="REL_HABITAT_DIVERSITY_NICHES",
        name="Low Habitat Structural Diversity Restricts Ecological Niches",
        source_metric="biodiversity.habitat_diversity",
        operator=ConditionOperator.LESS_THAN,
        threshold_value=40.0,
        target_metric="derived.ecological_niches",
        target_state="restricted",
        relationship_type="limits",
        direction=RelationshipDirection.POSITIVE,
        ecological_mechanism=(
            "Structural simplicity compresses the multidimensional niche space (Hutchinsonian hypervolume). "
            "Without diverse nesting substrates, varied foraging strata, and seasonal floral calendars, "
            "specialist guilds cannot maintain viable populations."
        ),
        evidence_ids=["TILMAN_2014_BIODIV", "HOOPER_2005_SYNTHESIS"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        confidence=0.93,
        ecosystem_context="all",
        quality_metadata={"domain": "biodiversity", "consensus_tier": 1},
    ),
    EcologicalRelationship(
        id="REL_HETEROGENEITY_NICHES",
        name="Simplified Habitat Heterogeneity Restricts Niche Availability",
        source_metric="derived.habitat_heterogeneity",
        operator=ConditionOperator.EQUALS,
        threshold_value="simplified",
        target_metric="derived.ecological_niches",
        target_state="restricted",
        relationship_type="limits",
        direction=RelationshipDirection.POSITIVE,
        ecological_mechanism=(
            "Landscape patch uniformity eliminates microclimatic thermal refugia, reduces temporal resource continuity, "
            "and constrains trophic diversity to competitive generalist species."
        ),
        evidence_ids=["TSCHARNTKE_2012_LANDSCAPE", "BENTON_2003_FARMLAND"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        confidence=0.94,
        ecosystem_context="all",
        quality_metadata={"domain": "biodiversity", "consensus_tier": 1},
    ),
    EcologicalRelationship(
        id="REL_NICHES_SPECIES_RICHNESS",
        name="Restricted Niche Availability Drives Species Richness Decline",
        source_metric="derived.ecological_niches",
        operator=ConditionOperator.EQUALS,
        threshold_value="restricted",
        target_metric="derived.species_survival_pressure",
        target_state="biodiversity_loss_pressure",
        relationship_type="drives",
        direction=RelationshipDirection.NEGATIVE,
        ecological_mechanism=(
            "Competitive exclusion dictates that when available niche space shrinks, interspecific competition "
            "intensifies, eliminating specialized species and driving localized species richness downward."
        ),
        evidence_ids=["TILMAN_2014_BIODIV", "IPBES_GLOBAL_2019"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        confidence=0.92,
        ecosystem_context="all",
        quality_metadata={"domain": "biodiversity", "consensus_tier": 1},
    ),
    EcologicalRelationship(
        id="REL_LOW_SPECIES_RICHNESS_VULNERABILITY",
        name="Depleted Species Richness Compromises Ecosystem Resilience",
        source_metric="biodiversity.species_richness",
        operator=ConditionOperator.LESS_THAN,
        threshold_value=30.0,
        target_metric="derived.species_survival_pressure",
        target_state="vulnerable",
        relationship_type="degrades",
        direction=RelationshipDirection.POSITIVE,
        ecological_mechanism=(
            "Loss of taxonomic diversity erodes functional redundancy across trophic levels, leaving pollination, "
            "decomposition, and pest regulation vulnerable to single-point ecological failures."
        ),
        evidence_ids=["HOOPER_2005_SYNTHESIS", "TILMAN_2014_BIODIV"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        confidence=0.90,
        ecosystem_context="all",
        quality_metadata={"domain": "biodiversity", "consensus_tier": 1},
    ),

    # ==========================================================================
    # DEFORESTATION → HABITAT LOSS → FRAGMENTATION → CONNECTIVITY
    # ==========================================================================
    EcologicalRelationship(
        id="REL_DEFORESTATION_HABITAT_LOSS",
        name="Deforestation Causes Net Native Habitat Loss",
        source_metric="human_impact.deforestation",
        operator=ConditionOperator.GREATER_THAN,
        threshold_value=10.0,
        target_metric="derived.habitat_loss",
        target_state="severe",
        relationship_type="induces",
        direction=RelationshipDirection.POSITIVE,
        ecological_mechanism=(
            "Canopy clearance directly eliminates the primary vertical biomass and foundational vegetation architecture "
            "that defines terrestrial forest biomes, displacing endemic fauna and reducing biotope carrying capacity."
        ),
        evidence_ids=["IPBES_GLOBAL_2019", "CBD_GBO5_2020"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        confidence=0.96,
        ecosystem_context="all",
        quality_metadata={"domain": "human_impact", "consensus_tier": 1},
    ),
    EcologicalRelationship(
        id="REL_DEFORESTATION_FRAGMENTATION",
        name="Deforestation Drives Landscape Habitat Fragmentation",
        source_metric="human_impact.deforestation",
        operator=ConditionOperator.GREATER_THAN,
        threshold_value=5.0,
        target_metric="derived.habitat_fragmentation",
        target_state="elevated",
        relationship_type="drives",
        direction=RelationshipDirection.POSITIVE,
        ecological_mechanism=(
            "Selective and spatial timber removal bifurcates previously continuous interior forest corridors into "
            "isolated relic patches, increasing edge effect penetration (microclimate alteration, invasive predation)."
        ),
        evidence_ids=["HADDAD_2015_FRAGMENTATION"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        confidence=0.95,
        ecosystem_context="all",
        quality_metadata={"domain": "human_impact", "consensus_tier": 1},
    ),
    EcologicalRelationship(
        id="REL_FRAGMENTATION_CONNECTIVITY",
        name="Elevated Fragmentation Impairs Landscape Connectivity",
        source_metric="derived.habitat_fragmentation",
        operator=ConditionOperator.EQUALS,
        threshold_value="elevated",
        target_metric="derived.habitat_connectivity",
        target_state="impaired",
        relationship_type="inhibits",
        direction=RelationshipDirection.NEGATIVE,
        ecological_mechanism=(
            "High patch isolation widens physical gaps between biotope patches beyond the dispersal and perceptual "
            "ranges of forest interior organisms, disrupting gene flow and rescue effects."
        ),
        evidence_ids=["HADDAD_2015_FRAGMENTATION", "CBD_GBO5_2020"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        confidence=0.94,
        ecosystem_context="all",
        quality_metadata={"domain": "biodiversity", "consensus_tier": 1},
    ),
    EcologicalRelationship(
        id="REL_CONNECTIVITY_GENETIC_PRESSURE",
        name="Impaired Connectivity Induces Population Isolation Pressure",
        source_metric="derived.habitat_connectivity",
        operator=ConditionOperator.EQUALS,
        threshold_value="impaired",
        target_metric="derived.species_survival_pressure",
        target_state="genetic_isolation",
        relationship_type="induces",
        direction=RelationshipDirection.POSITIVE,
        ecological_mechanism=(
            "Severed ecological corridors isolate small sub-populations, accelerating inbreeding depression, "
            "limiting genetic variance, and heightening vulnerability to stochastic demographic crashes."
        ),
        evidence_ids=["HADDAD_2015_FRAGMENTATION", "IPBES_GLOBAL_2019"],
        evidence_strength=EvidenceStrength.STRONG,
        confidence=0.91,
        ecosystem_context="all",
        quality_metadata={"domain": "biodiversity", "consensus_tier": 1},
    ),
    EcologicalRelationship(
        id="REL_DEFORESTATION_EROSION",
        name="Canopy Clearance Escalates Soil Erosion Susceptibility",
        source_metric="human_impact.deforestation",
        operator=ConditionOperator.GREATER_THAN,
        threshold_value=15.0,
        target_metric="derived.soil_erosion_susceptibility",
        target_state="critical",
        relationship_type="induces",
        direction=RelationshipDirection.POSITIVE,
        ecological_mechanism=(
            "Removal of multi-layered tree canopies and stabilizing root tensile networks exposes bare soil directly "
            "to kinetic raindrop splash detachment, triggering sheet and rill erosion."
        ),
        evidence_ids=["IPCC_SRCCL_2019", "UNEP_LAND_DEGRAD_2021"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        confidence=0.93,
        ecosystem_context="all",
        quality_metadata={"domain": "human_impact", "consensus_tier": 1},
    ),

    # ==========================================================================
    # HUMAN IMPACT: POLLUTION
    # ==========================================================================
    EcologicalRelationship(
        id="REL_POLLUTION_TOXICITY_STRESS",
        name="Elevated Pollution Induces Ecotoxicological Stress",
        source_metric="human_impact.pollution",
        operator=ConditionOperator.GREATER_THAN,
        threshold_value=25.0,
        target_metric="derived.environmental_toxicity_stress",
        target_state="high",
        relationship_type="induces",
        direction=RelationshipDirection.POSITIVE,
        ecological_mechanism=(
            "Elevated concentrations of synthetic xenobiotics, heavy metals, or agrochemical residues bioaccumulate, "
            "disrupting endocrine systems, generating reactive oxygen species (ROS), and impairing reproductive viability."
        ),
        evidence_ids=["UNEP_LAND_DEGRAD_2021", "IPBES_GLOBAL_2019"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        confidence=0.92,
        ecosystem_context="all",
        quality_metadata={"domain": "human_impact", "consensus_tier": 1},
    ),
    EcologicalRelationship(
        id="REL_TOXICITY_SOIL_BIOLOGY",
        name="Ecotoxicological Stress Suppresses Soil Microorganisms",
        source_metric="derived.environmental_toxicity_stress",
        operator=ConditionOperator.EQUALS,
        threshold_value="high",
        target_metric="derived.soil_biological_activity",
        target_state="inhibited",
        relationship_type="inhibits",
        direction=RelationshipDirection.NEGATIVE,
        ecological_mechanism=(
            "Toxic heavy metals and pesticide accumulation inhibit essential soil microbial enzymes (dehydrogenase, "
            "urease, phosphatase), suppressing subterranean respiration and mycorrhizal symbiosis."
        ),
        evidence_ids=["FAO_SOIL_2020"],
        evidence_strength=EvidenceStrength.STRONG,
        confidence=0.90,
        ecosystem_context="all",
        quality_metadata={"domain": "human_impact", "consensus_tier": 1},
    ),
    EcologicalRelationship(
        id="REL_POLLUTION_SPECIES_LOSS",
        name="Severe Pollution Directly Triggers Species Richness Contraction",
        source_metric="human_impact.pollution",
        operator=ConditionOperator.GREATER_THAN,
        threshold_value=50.0,
        target_metric="derived.species_survival_pressure",
        target_state="toxicity_induced_loss",
        relationship_type="drives",
        direction=RelationshipDirection.NEGATIVE,
        ecological_mechanism=(
            "Acute environmental toxicity exceeds physiological tolerance limits of sensitive bio-indicators (amphibians, "
            "epiphytic lichens, benthic invertebrates), causing localized extirpation."
        ),
        evidence_ids=["UNEP_LAND_DEGRAD_2021"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        confidence=0.91,
        ecosystem_context="all",
        quality_metadata={"domain": "human_impact", "consensus_tier": 1},
    ),

    # ==========================================================================
    # CASCADING STRESSES: WATER STRESS → SPECIES SURVIVAL
    # ==========================================================================
    EcologicalRelationship(
        id="REL_WATER_AVAILABILITY_PLANT_STRESS",
        name="Landscape Water Deficit Drives Chronic Plant Water Stress",
        source_metric="derived.water_availability",
        operator=ConditionOperator.EQUALS,
        threshold_value="deficit",
        target_metric="derived.plant_water_stress",
        target_state="chronic",
        relationship_type="induces",
        direction=RelationshipDirection.POSITIVE,
        ecological_mechanism=(
            "Prolonged hydrological precipitation deficit depletes soil water tables and subsoil moisture reservoirs, "
            "imposing protracted vegetative drought stress across the plant community."
        ),
        evidence_ids=["IPCC_WG2_2022_CH2"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        confidence=0.92,
        ecosystem_context="all",
        quality_metadata={"domain": "climate", "consensus_tier": 1},
    ),
    EcologicalRelationship(
        id="REL_WATER_RETENTION_PLANT_STRESS",
        name="Reduced Soil Water Retention Accelerates Plant Drought Stress",
        source_metric="derived.soil_water_retention",
        operator=ConditionOperator.EQUALS,
        threshold_value="reduced",
        target_metric="derived.plant_water_stress",
        target_state="accelerated",
        relationship_type="induces",
        direction=RelationshipDirection.POSITIVE,
        ecological_mechanism=(
            "Soils with depleted organic carbon and damaged aggregate structure drain and dry rapidly between rain events, "
            "triggering plant water stress even under moderate meteorological drought conditions."
        ),
        evidence_ids=["RAWLS_2003_SOIL_WATER", "LAL_2004_CARBON"],
        evidence_strength=EvidenceStrength.STRONG,
        confidence=0.89,
        ecosystem_context="all",
        quality_metadata={"domain": "soil", "consensus_tier": 2},
    ),
    EcologicalRelationship(
        id="REL_PLANT_WATER_STRESS_SURVIVAL",
        name="Hydraulic Plant Stress Induces Survival and Mortality Pressures",
        source_metric="derived.plant_water_stress",
        operator=ConditionOperator.IN_LIST,
        threshold_value=["acute", "chronic", "accelerated"],
        target_metric="derived.species_survival_pressure",
        target_state="elevated_mortality_risk",
        relationship_type="induces",
        direction=RelationshipDirection.POSITIVE,
        ecological_mechanism=(
            "Severe hydraulic failure or carbon starvation from sustained stomatal closure leads to branch dieback, "
            "elevated canopy mortality, and cascading food web resource crashes for herbivorous and pollinator fauna."
        ),
        evidence_ids=["IPCC_WG2_2022_CH2"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        confidence=0.93,
        ecosystem_context="all",
        quality_metadata={"domain": "biodiversity", "consensus_tier": 1},
    ),
    EcologicalRelationship(
        id="REL_HABITAT_LOSS_EXTIRPATION",
        name="Severe Habitat Loss Drives Extirpation Risk",
        source_metric="derived.habitat_loss",
        operator=ConditionOperator.EQUALS,
        threshold_value="severe",
        target_metric="derived.species_survival_pressure",
        target_state="extirpation_risk",
        relationship_type="drives",
        direction=RelationshipDirection.POSITIVE,
        ecological_mechanism=(
            "Species-area relationship dictates that a permanent reduction in suitable area precipitates an unavoidable "
            "extinction debt, directly shrinking population abundances below minimum viable population (MVP) sizes."
        ),
        evidence_ids=["IPBES_GLOBAL_2019", "CBD_GBO5_2020"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        confidence=0.95,
        ecosystem_context="all",
        quality_metadata={"domain": "biodiversity", "consensus_tier": 1},
    ),

    # ==========================================================================
    # LAND COVER & MICROCLIMATE
    # ==========================================================================
    EcologicalRelationship(
        id="REL_BARE_SOIL_EROSION",
        name="Bare Soil Cover Induces Acute Erosion Susceptibility",
        source_metric="land.land_cover",
        operator=ConditionOperator.EQUALS,
        threshold_value="bare_soil",
        target_metric="derived.soil_erosion_susceptibility",
        target_state="acute",
        relationship_type="induces",
        direction=RelationshipDirection.POSITIVE,
        ecological_mechanism=(
            "Without vegetative canopy interception or surface litter mulch, raindrop terminal kinetic energy strikes "
            "topsoil directly, dispersing aggregates and inducing rapid surface crusting and rill formation."
        ),
        evidence_ids=["UNEP_LAND_DEGRAD_2021", "IPCC_SRCCL_2019"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        confidence=0.96,
        ecosystem_context="all",
        quality_metadata={"domain": "land", "consensus_tier": 1},
    ),
    EcologicalRelationship(
        id="REL_CLOSED_CANOPY_CONNECTIVITY",
        name="Closed Canopy Cover Supports Functional Habitat Connectivity",
        source_metric="land.land_cover",
        operator=ConditionOperator.EQUALS,
        threshold_value="closed_canopy_forest",
        target_metric="derived.habitat_connectivity",
        target_state="high",
        relationship_type="enhances",
        direction=RelationshipDirection.POSITIVE,
        ecological_mechanism=(
            "Contiguous multi-layered tree canopy maintains buffered interior humidity, low light penetration, "
            "and continuous arboreal pathways that support unimpeded movement for canopy specialists."
        ),
        evidence_ids=["HADDAD_2015_FRAGMENTATION"],
        evidence_strength=EvidenceStrength.STRONG,
        confidence=0.91,
        ecosystem_context="all",
        quality_metadata={"domain": "land", "consensus_tier": 2},
    ),
    EcologicalRelationship(
        id="REL_DEGRADED_SCRUB_HETEROGENEITY",
        name="Degraded Scrub Reduces Landscape Heterogeneity",
        source_metric="land.land_cover",
        operator=ConditionOperator.EQUALS,
        threshold_value="degraded_scrub",
        target_metric="derived.habitat_heterogeneity",
        target_state="simplified",
        relationship_type="degrades",
        direction=RelationshipDirection.NEGATIVE,
        ecological_mechanism=(
            "Replacement of mature climax biotope with thorny or secondary scrub reduces structural strata "
            "and seasonal fruit/seed mast resources required by specialist wildlife."
        ),
        evidence_ids=["IPBES_GLOBAL_2019"],
        evidence_strength=EvidenceStrength.STRONG,
        confidence=0.88,
        ecosystem_context="all",
        quality_metadata={"domain": "land", "consensus_tier": 2},
    ),
    EcologicalRelationship(
        id="REL_BIO_ACTIVITY_NUTRIENTS",
        name="Suppressed Soil Biological Activity Inhibits Mineralization",
        source_metric="derived.soil_biological_activity",
        operator=ConditionOperator.IN_LIST,
        threshold_value=["degraded", "inhibited"],
        target_metric="derived.nutrient_availability",
        target_state="mineralization_deficit",
        relationship_type="inhibits",
        direction=RelationshipDirection.NEGATIVE,
        ecological_mechanism=(
            "Depressed microbial biomass and extracellular enzyme activities slow the depolymerization of plant proteins "
            "and organophosphates, creating inorganic nitrogen and phosphate deficits in the root zone."
        ),
        evidence_ids=["FAO_SOIL_2020"],
        evidence_strength=EvidenceStrength.STRONG,
        confidence=0.90,
        ecosystem_context="all",
        quality_metadata={"domain": "soil", "consensus_tier": 1},
    ),
]
