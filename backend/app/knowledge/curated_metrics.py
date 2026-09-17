"""Curated environmental metric definitions for the Ecological Knowledge Base (Phase 3)."""

from typing import List
from backend.app.schemas.knowledge import EnvironmentalMetricDefinition, MetricDomain

CURATED_METRICS: List[EnvironmentalMetricDefinition] = [
    # --------------------------------------------------------------------------
    # Soil Domain
    # --------------------------------------------------------------------------
    EnvironmentalMetricDefinition(
        id="soil.ph",
        name="Soil pH",
        domain=MetricDomain.SOIL,
        unit="pH",
        metric_type="numeric",
        description="Negative logarithm of hydrogen ion activity; controls soil chemical speciation, nutrient solubility, and microbial activity.",
        min_value=0.0,
        max_value=14.0,
    ),
    EnvironmentalMetricDefinition(
        id="soil.organic_carbon",
        name="Soil Organic Carbon",
        domain=MetricDomain.SOIL,
        unit="%",
        metric_type="numeric",
        description="Mass percentage of organic carbon in dry soil; fundamental determinant of soil aggregate stability, cation exchange capacity, and biological habitat.",
        min_value=0.0,
        max_value=100.0,
    ),
    EnvironmentalMetricDefinition(
        id="soil.moisture",
        name="Soil Volumetric Moisture",
        domain=MetricDomain.SOIL,
        unit="%",
        metric_type="numeric",
        description="Ratio of water volume to total soil volume; primary driver of plant hydraulic conductivity, root respiration, and microbial metabolism.",
        min_value=0.0,
        max_value=100.0,
    ),

    # --------------------------------------------------------------------------
    # Land Domain
    # --------------------------------------------------------------------------
    EnvironmentalMetricDefinition(
        id="land.land_use",
        name="Land Use Regime",
        domain=MetricDomain.LAND,
        unit=None,
        metric_type="categorical",
        description="Socio-economic utilization of the terrestrial surface, e.g. intensive monoculture, agroforestry, conservation forest, grazed rangeland.",
        categories=["monoculture", "intensive_agriculture", "agroforestry", "conservation_forest", "grazing_rangeland", "urban_industrial", "fallow"],
    ),
    EnvironmentalMetricDefinition(
        id="land.land_cover",
        name="Land Cover Classification",
        domain=MetricDomain.LAND,
        unit=None,
        metric_type="categorical",
        description="Physical and biological cover of the Earth's surface, e.g. closed canopy forest, open savanna, shrubland, cropland.",
        categories=["closed_canopy_forest", "open_forest", "savanna_grassland", "wetland_peatland", "cropland", "bare_soil", "degraded_scrub"],
    ),

    # --------------------------------------------------------------------------
    # Biodiversity Domain
    # --------------------------------------------------------------------------
    EnvironmentalMetricDefinition(
        id="biodiversity.species_richness",
        name="Species Richness",
        domain=MetricDomain.BIODIVERSITY,
        unit="species_count",
        metric_type="numeric",
        description="Total count of distinct taxonomic species observed or surveyed within the standardized sample unit.",
        min_value=0.0,
        max_value=10000.0,
    ),
    EnvironmentalMetricDefinition(
        id="biodiversity.habitat_diversity",
        name="Habitat Structural Diversity Index",
        domain=MetricDomain.BIODIVERSITY,
        unit="index (0-100)",
        metric_type="numeric",
        description="Composite structural heterogeneity score quantifying vertical stratification, microtopography, and floral composition variance.",
        min_value=0.0,
        max_value=100.0,
    ),

    # --------------------------------------------------------------------------
    # Climate Domain
    # --------------------------------------------------------------------------
    EnvironmentalMetricDefinition(
        id="climate.temperature",
        name="Mean Ambient Temperature",
        domain=MetricDomain.CLIMATE,
        unit="°C",
        metric_type="numeric",
        description="Mean surface air temperature; controls metabolic kinetics, vapor pressure deficit, and physiological thermal boundaries.",
        min_value=-60.0,
        max_value=60.0,
    ),
    EnvironmentalMetricDefinition(
        id="climate.rainfall",
        name="Mean Annual Precipitation",
        domain=MetricDomain.CLIMATE,
        unit="mm/yr",
        metric_type="numeric",
        description="Total annual meteorological liquid and solid water equivalent precipitation.",
        min_value=0.0,
        max_value=15000.0,
    ),

    # --------------------------------------------------------------------------
    # Human Impact Domain
    # --------------------------------------------------------------------------
    EnvironmentalMetricDefinition(
        id="human_impact.pollution",
        name="Pollution & Contaminant Index",
        domain=MetricDomain.HUMAN_IMPACT,
        unit="index (0-100)",
        metric_type="numeric",
        description="Integrated index of chemical, heavy metal, agrochemical, and particulate loading in soil, water, and atmospheric matrices.",
        min_value=0.0,
        max_value=100.0,
    ),
    EnvironmentalMetricDefinition(
        id="human_impact.deforestation",
        name="Deforestation & Canopy Loss Rate",
        domain=MetricDomain.HUMAN_IMPACT,
        unit="%/decade",
        metric_type="numeric",
        description="Percentage of native primary or secondary woody canopy cover cleared, severely degraded, or converted over a decadal baseline.",
        min_value=0.0,
        max_value=100.0,
    ),

    # --------------------------------------------------------------------------
    # Derived / Intermediate Ecological State Metrics
    # --------------------------------------------------------------------------
    EnvironmentalMetricDefinition(
        id="derived.soil_biological_activity",
        name="Soil Biological Activity",
        domain=MetricDomain.ECOLOGICAL_STATE,
        unit="state",
        metric_type="state_flag",
        description="Rate of microbial biomass turnover, enzyme secretion, and subterranean nutrient mineralization.",
    ),
    EnvironmentalMetricDefinition(
        id="derived.soil_water_retention",
        name="Soil Water Retention Capacity",
        domain=MetricDomain.ECOLOGICAL_STATE,
        unit="state",
        metric_type="state_flag",
        description="Ability of soil pore architecture to store plant-available capillary water between field capacity and wilting point.",
    ),
    EnvironmentalMetricDefinition(
        id="derived.plant_water_stress",
        name="Plant Hydraulic Water Stress",
        domain=MetricDomain.ECOLOGICAL_STATE,
        unit="state",
        metric_type="state_flag",
        description="Physiological strain resulting from soil water potential dropping below root osmotic uptake threshold.",
    ),
    EnvironmentalMetricDefinition(
        id="derived.water_availability",
        name="Landscape Water Availability",
        domain=MetricDomain.ECOLOGICAL_STATE,
        unit="state",
        metric_type="state_flag",
        description="Integrated hydrological water balance available for surface runoff, infiltration, and vegetation transpiration.",
    ),
    EnvironmentalMetricDefinition(
        id="derived.climate_thermal_stress",
        name="Thermal & Evaporative Climate Stress",
        domain=MetricDomain.ECOLOGICAL_STATE,
        unit="state",
        metric_type="state_flag",
        description="High atmospheric vapor pressure deficit and thermal load driving cellular stress and stomatal closure.",
    ),
    EnvironmentalMetricDefinition(
        id="derived.habitat_heterogeneity",
        name="Spatial Habitat Heterogeneity",
        domain=MetricDomain.ECOLOGICAL_STATE,
        unit="state",
        metric_type="state_flag",
        description="Spatial patch mosaic complexity and structural variety across the landscape.",
    ),
    EnvironmentalMetricDefinition(
        id="derived.ecological_niches",
        name="Ecological Niche Availability",
        domain=MetricDomain.ECOLOGICAL_STATE,
        unit="state",
        metric_type="state_flag",
        description="Dimensional multidimensional resource space available for specialized and generalist species.",
    ),
    EnvironmentalMetricDefinition(
        id="derived.habitat_loss",
        name="Net Habitat Loss",
        domain=MetricDomain.ECOLOGICAL_STATE,
        unit="state",
        metric_type="state_flag",
        description="Reduction in total physical spatial extent of suitable native biotope.",
    ),
    EnvironmentalMetricDefinition(
        id="derived.habitat_fragmentation",
        name="Landscape Fragmentation",
        domain=MetricDomain.ECOLOGICAL_STATE,
        unit="state",
        metric_type="state_flag",
        description="Breakup of continuous habitat into smaller, isolated patches with increased edge-to-interior ratios.",
    ),
    EnvironmentalMetricDefinition(
        id="derived.habitat_connectivity",
        name="Structural & Functional Connectivity",
        domain=MetricDomain.ECOLOGICAL_STATE,
        unit="state",
        metric_type="state_flag",
        description="Degree to which the landscape facilitates or impedes gene flow, dispersal, and wildlife movement.",
    ),
    EnvironmentalMetricDefinition(
        id="derived.nutrient_availability",
        name="Bioavailable Soil Nutrients",
        domain=MetricDomain.ECOLOGICAL_STATE,
        unit="state",
        metric_type="state_flag",
        description="Soluble fraction of essential macronutrients (N, P, K) and micronutrients available for plant root uptake.",
    ),
    EnvironmentalMetricDefinition(
        id="derived.environmental_toxicity_stress",
        name="Ecotoxicological Stress",
        domain=MetricDomain.ECOLOGICAL_STATE,
        unit="state",
        metric_type="state_flag",
        description="Inhibition of enzymatic, reproductive, and physiological functions by synthetic or heavy metal pollutants.",
    ),
    EnvironmentalMetricDefinition(
        id="derived.species_survival_pressure",
        name="Species Survival & Population Pressure",
        domain=MetricDomain.ECOLOGICAL_STATE,
        unit="state",
        metric_type="state_flag",
        description="Cumulative pressure on demographic recruitment, foraging efficiency, and reproductive fitness.",
    ),
    EnvironmentalMetricDefinition(
        id="derived.soil_erosion_susceptibility",
        name="Soil Erosion Susceptibility",
        domain=MetricDomain.ECOLOGICAL_STATE,
        unit="state",
        metric_type="state_flag",
        description="Vulnerability of unprotected topsoil to kinetic detachment by raindrop impact and overland sheet wash.",
    ),
]
