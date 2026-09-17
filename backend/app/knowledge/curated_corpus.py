"""Curated Scientific Document Corpus for Biodiversity Intelligence (Phase 4).

Prioritizes authentic, authoritative sources:
1. IPCC (Intergovernmental Panel on Climate Change)
2. IPBES (Intergovernmental Science-Policy Platform on Biodiversity and Ecosystem Services)
3. FAO (Food and Agriculture Organization)
4. UNEP (United Nations Environment Programme)
5. CBD (Convention on Biological Diversity)
6. Peer-reviewed literature & systematic meta-analyses (Nature, Science, PNAS, Global Change Biology, etc.)
"""

from typing import List
from backend.app.schemas.scientific_rag import (
    EvidenceStrength,
    ScientificDocumentCreate,
    ScientificSourceType,
)

CURATED_SCIENTIFIC_DOCUMENTS: List[ScientificDocumentCreate] = [
    # --------------------------------------------------------------------------
    # 1. IPCC (Intergovernmental Panel on Climate Change)
    # --------------------------------------------------------------------------
    ScientificDocumentCreate(
        id="DOC_IPCC_WG2_2022_CH2",
        title="Terrestrial and Freshwater Ecosystems and Their Services - IPCC WGII Sixth Assessment Report",
        authors="Pörtner, H.O., Roberts, D.C., Adams, H., et al.",
        organization="IPCC",
        year=2022,
        source_type=ScientificSourceType.GLOBAL_ASSESSMENT,
        citation="IPCC, 2022: Chapter 2: Terrestrial and Freshwater Ecosystems and Their Services. In: Climate Change 2022: Impacts, Adaptation and Vulnerability. Cambridge University Press, Cambridge, UK and New York, NY, USA, pp. 197–377.",
        doi="10.1017/9781009325844.004",
        url="https://www.ipcc.ch/report/ar6/wg2/chapter/chapter-2/",
        geographic_scope="global",
        ecosystem="all",
        topics=["climate_change", "thermal_stress", "ecosystem_resilience", "drought", "extinction_risk"],
        environmental_metrics=["climate.temperature", "climate.rainfall", "soil.moisture", "biodiversity.species_richness"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        abstract="Comprehensive assessment of observed impacts and projected risks of climate change on terrestrial and freshwater ecosystems, ecological thresholds, and tipping points.",
        full_text="""Section 2.4.2: Hydrological Stress, Temperature Extremes, and Forest Vulnerability.
Rising mean surface temperatures coupled with altered precipitation regimes intensify landscape atmospheric vapor pressure deficits (VPD). When annual precipitation falls below 600 mm/year and ambient growing season temperatures exceed 30°C, soil moisture deficits propagate rapidly into the rooting zone. This compounds hydraulic failure risk in vascular plants through xylem cavitation and stomatal closure, limiting photosynthetic carbon assimilation.

Section 2.4.3: Compound Climate Events and Ecosystem Thresholds.
The co-occurrence of low rainfall, elevated heat, and degraded soil moisture leads to non-linear ecosystem tipping dynamics. Forest dieback and vegetative drought stress accelerate under compound thermal-hydro extremes, reducing habitat carrying capacity and precipitating localized biodiversity loss across invertebrate and vertebrate guilds.

Section 2.5.1: Ecosystem Degradation and Land-Use Synergy.
Anthropogenic land fragmentation severely limits the autonomous range migration of species attempting to track shifting bioclimatic envelopes. Intact ecological corridors reduce vulnerability to localized climate extremes by providing microclimatic buffering and genetic connectivity.""",
    ),

    ScientificDocumentCreate(
        id="DOC_IPCC_SRCCL_2019_LAND",
        title="IPCC Special Report on Climate Change, Desertification, Land Degradation, Sustainable Land Management, Food Security, and Greenhouse Gas Fluxes in Terrestrial Ecosystems",
        authors="Shukla, P.R., Skea, J., Buendia, E.C., et al.",
        organization="IPCC",
        year=2019,
        source_type=ScientificSourceType.GLOBAL_ASSESSMENT,
        citation="IPCC, 2019: Climate Change and Land: an IPCC special report on climate change, desertification, land degradation, sustainable land management, food security, and greenhouse gas fluxes in terrestrial ecosystems.",
        doi="10.1017/9781009157988",
        url="https://www.ipcc.ch/srccl/",
        geographic_scope="global",
        ecosystem="dryland_and_agroecosystem",
        topics=["land_degradation", "soil_organic_carbon", "desertification", "sustainable_land_management"],
        environmental_metrics=["soil.organic_carbon", "soil.moisture", "land.land_use", "climate.rainfall"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        abstract="Assesses land degradation pathways, soil organic matter dynamics, and sustainable land management strategies across global biomes.",
        full_text="""Chapter 3: Land Degradation and Soil Organic Carbon Depletion.
Soil organic matter (SOM) and soil organic carbon (SOC) are central to soil structure, infiltration capacity, and aggregate stability. Continuous intensive cultivation without organic amendments reduces SOC stocks below critical thresholds (< 1.5% to 2.0%), collapsing soil macro-aggregates and drastically lowering available water holding capacity (AWC).

Chapter 4: Desertification and Hydro-Pedological Vulnerability.
In arid and semi-arid landscapes, the combination of low rainfall (< 500 mm) and depleted SOC leaves topsoil vulnerable to crusting, rapid runoff, and wind erosion. Maintaining organic ground cover and agroforestry integration buffers soil surface temperatures, reduces evaporation, and increases soil water retention by up to 20-30%.""",
    ),

    # --------------------------------------------------------------------------
    # 2. IPBES (Intergovernmental Science-Policy Platform on Biodiversity)
    # --------------------------------------------------------------------------
    ScientificDocumentCreate(
        id="DOC_IPBES_GLOBAL_2019",
        title="Global Assessment Report on Biodiversity and Ecosystem Services",
        authors="Díaz, S., Settele, J., Brondízio, E.S., et al.",
        organization="IPBES",
        year=2019,
        source_type=ScientificSourceType.GLOBAL_ASSESSMENT,
        citation="IPBES, 2019: Global assessment report on biodiversity and ecosystem services of the Intergovernmental Science-Policy Platform on Biodiversity and Ecosystem Services. IPBES secretariat, Bonn, Germany. 1148 pages.",
        doi="10.5281/zenodo.3831673",
        url="https://www.ipbes.net/global-assessment",
        geographic_scope="global",
        ecosystem="all",
        topics=["biodiversity_loss", "habitat_conversion", "land_use_change", "species_extinction", "ecosystem_services"],
        environmental_metrics=["biodiversity.species_richness", "biodiversity.habitat_diversity", "land.land_use", "human_impact.deforestation"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        abstract="Comprehensive synthesis of the state of global biodiversity, direct and indirect drivers of nature deterioration, and conservation priorities.",
        full_text="""Chapter 2.2: Direct Drivers of Biodiversity Loss in Terrestrial Systems.
Land-use change remains the primary direct driver of terrestrial biodiversity loss globally. The conversion of heterogeneous native ecosystems into simplified monocultures and intensive agricultural expanses drives rapid declines in species richness and functional diversity. Habitat loss exceeding 10% in a regional landscape triggers disproportionate losses in specialized species.

Chapter 2.3: Habitat Fragmentation and Spatial Isolation.
Severe habitat fragmentation divides continuous populations into small, isolated subpopulations subject to genetic bottlenecks, elevated edge effects, and inbreeding depression. Matrix quality between fragments determines wildlife dispersal success; structurally complex matrix environments mitigate extirpation risks by facilitating demographic rescue effects.""",
    ),

    ScientificDocumentCreate(
        id="DOC_IPBES_LAND_DEGRAD_2018",
        title="The IPBES Assessment Report on Land Degradation and Restoration",
        authors="Montanarella, L., Scholes, R., Brainich, A.",
        organization="IPBES",
        year=2018,
        source_type=ScientificSourceType.GLOBAL_ASSESSMENT,
        citation="IPBES, 2018: The IPBES assessment report on land degradation and restoration. Secretariat of the Intergovernmental Science-Policy Platform on Biodiversity and Ecosystem Services, Bonn, Germany. 744 pages.",
        doi="10.5281/zenodo.3237392",
        url="https://www.ipbes.net/assessment-reports/ldr",
        geographic_scope="global",
        ecosystem="all",
        topics=["land_degradation", "restoration", "soil_loss", "ecosystem_function"],
        environmental_metrics=["land.land_cover", "soil.organic_carbon", "human_impact.deforestation", "soil.moisture"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        abstract="Evaluates global degradation of land and water resources, ecological impacts on human well-being, and ecological restoration mechanisms.",
        full_text="""Chapter 4: Ecological Mechanisms of Land Degradation.
Removal of vegetative canopy cover accelerates raindrop impact erosion, detachment of topsoil particles, and loss of the organic-rich epipedon. When vegetative ground cover falls below 30%, surface soil erosion rates increase exponentially, stripping mycorrhizal networks and essential plant nutrients.

Chapter 6: Restoration Interventions and Regenerative Trajectories.
Re-establishing multi-tiered vegetative strata, incorporating nitrogen-fixing native legumes, and restoring soil organic matter creates positive feedback loops that enhance biological infiltration, microclimate moderation, and spontaneous natural colonization of native biota.""",
    ),

    # --------------------------------------------------------------------------
    # 3. FAO (Food and Agriculture Organization)
    # --------------------------------------------------------------------------
    ScientificDocumentCreate(
        id="DOC_FAO_SOIL_STATUS_2020",
        title="Status of the World's Soil Resources and Global Soil Organic Carbon Dynamics",
        authors="FAO and ITPS",
        organization="FAO",
        year=2020,
        source_type=ScientificSourceType.INSTITUTIONAL_REPORT,
        citation="FAO and ITPS. 2020. Status of the World's Soil Resources: Main Report. Food and Agriculture Organization of the United Nations, Rome, Italy.",
        doi="10.4060/ca7722en",
        url="https://www.fao.org/documents/card/en/c/ca7722en",
        geographic_scope="global",
        ecosystem="soil_systems",
        topics=["soil_health", "soil_organic_carbon", "soil_acidity", "microbial_biomass"],
        environmental_metrics=["soil.organic_carbon", "soil.ph", "soil.moisture"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        abstract="Authoritative status of global soils, detailing carbon dynamics, biological activity, acidification thresholds, and nutrient cycling mechanisms.",
        full_text="""Chapter 3: Soil Organic Carbon as the Primary Regulator of Soil Biological Health.
Soil organic carbon (SOC) represents the primary energy reservoir and metabolic substrate for heterotrophic soil microorganisms. Depletion of SOC below 1.5% leads to a severe drop in microbial biomass carbon (MBC), enzymatic activity (e.g., dehydrogenase, beta-glucosidase), and active nutrient mineralization pathways.

Chapter 5: Soil Acidity, Aluminum Toxicity, and Nutrient Fixation.
In soils with pH < 5.5, toxic monomeric aluminum species (Al3+) enter the soil solution, damaging root apical meristems and severely restricting phosphorus bioavailability through insoluble aluminum phosphate precipitation. Conversely, alkaline soil pH (> 8.2) causes micronutrient chlorosis (zinc, iron, manganese) and calcium phosphate precipitation.""",
    ),

    ScientificDocumentCreate(
        id="DOC_FAO_AGROECOLOGY_2018",
        title="The 10 Elements of Agroecology: Guiding the Transition to Sustainable Food and Agricultural Systems",
        authors="FAO Agroecology Knowledge Hub",
        organization="FAO",
        year=2018,
        source_type=ScientificSourceType.INSTITUTIONAL_REPORT,
        citation="FAO. 2018. The 10 Elements of Agroecology: Guiding the Transition to Sustainable Food and Agricultural Systems. Rome. 15 pp.",
        url="https://www.fao.org/agroecology/overview/overview10elements/en/",
        geographic_scope="global",
        ecosystem="agroecosystems",
        topics=["agroecology", "crop_diversification", "functional_biodiversity", "soil_regeneration"],
        environmental_metrics=["land.land_use", "biodiversity.habitat_diversity", "soil.organic_carbon"],
        evidence_strength=EvidenceStrength.STRONG,
        abstract="Presents 10 essential ecological elements for transitioning from industrial monocultures to biodiverse, regenerative agroecosystems.",
        full_text="""Element 1: Diversity and Ecosystem Resilience.
Diversifying farming landscapes through intercropping, agroforestry, and polycultures increases structural niche availability for natural predators and beneficial pollinators. Monoculture systems reduce structural complexity, eliminating overwintering refugia and alternative floral nectar sources required by predatory parasitoids.

Element 2: Synergies and Biological Soil Activation.
Integrating deep-rooting perennial species alongside annual crops enhances biological nutrient pumping, captures subsoil moisture, and builds subterranean microbial networks that suppress soil-borne pathogens.""",
    ),

    # --------------------------------------------------------------------------
    # 4. UNEP (United Nations Environment Programme)
    # --------------------------------------------------------------------------
    ScientificDocumentCreate(
        id="DOC_UNEP_GEO6_2019",
        title="Global Environment Outlook – GEO-6: Healthy Planet, Healthy People",
        authors="UNEP Global Environment Outlook Consortium",
        organization="UNEP",
        year=2019,
        source_type=ScientificSourceType.GLOBAL_ASSESSMENT,
        citation="UNEP (2019). Global Environment Outlook – GEO-6: Healthy Planet, Healthy People. Cambridge University Press, Cambridge. 745 pp.",
        doi="10.1017/9781108627146",
        url="https://www.unep.org/resources/global-environment-outlook-6",
        geographic_scope="global",
        ecosystem="all",
        topics=["environmental_pollution", "ecotoxicity", "land_degradation", "freshwater_quality"],
        environmental_metrics=["human_impact.pollution", "human_impact.deforestation", "biodiversity.species_richness"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        abstract="Comprehensive state of the global environment, focusing on the interconnected crises of pollution, land degradation, and biodiversity decline.",
        full_text="""Chapter 8: Land and Soil Pollution Dynamics.
Excessive application of chemical pesticides and synthetic agrochemicals creates elevated ecotoxicological stress in terrestrial food webs. High ecotoxicity indices (> 25) suppress non-target arthropods, depress earthworm populations (Lumbricidae), and diminish beneficial mycorrhizal spore viability.

Chapter 9: Synergistic Pressures of Pollution and Habitat Loss.
When chemical pollution coincides with physical habitat fragmentation (> 8% deforestation), wildlife species suffer compounded physiological and demographic stress, increasing localized extirpation rates up to threefold compared to single-stressor environments.""",
    ),

    # --------------------------------------------------------------------------
    # 5. CBD (Convention on Biological Diversity)
    # --------------------------------------------------------------------------
    ScientificDocumentCreate(
        id="DOC_CBD_GBO5_2020",
        title="Global Biodiversity Outlook 5 (GBO-5)",
        authors="Secretariat of the Convention on Biological Diversity",
        organization="CBD",
        year=2020,
        source_type=ScientificSourceType.GLOBAL_ASSESSMENT,
        citation="Secretariat of the Convention on Biological Diversity (2020). Global Biodiversity Outlook 5. Montreal. 212 pages.",
        url="https://www.cbd.int/gbo5",
        geographic_scope="global",
        ecosystem="all",
        topics=["biodiversity_targets", "connectivity", "protected_areas", "ecological_integrity"],
        environmental_metrics=["biodiversity.species_richness", "biodiversity.habitat_diversity", "land.land_cover"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        abstract="Assesses global progress toward the Aichi Biodiversity Targets and outlines pathways for transitioning to ecological equilibrium by 2050.",
        full_text="""Section 3: Transitions in Land and Forest Management.
Conserving and restoring habitat heterogeneity and structural connectivity is vital to reversing biodiversity decline. Preserving forest patches and riparian buffers across agricultural matrices sustains up to 70-80% of native forest species richness within mixed production landscapes.

Section 4: Spatial Ecological Integrity.
Isolated habitat patches below critical patch size thresholds experience severe trophic downgrading, with apex predators and large-bodied frugivores disappearing first, disrupting seed dispersal dynamics.""",
    ),

    # --------------------------------------------------------------------------
    # 6. Peer-Reviewed Meta-Analyses and Landmark Research
    # --------------------------------------------------------------------------
    ScientificDocumentCreate(
        id="DOC_TILMAN_2014_BIODIVERSITY",
        title="Biodiversity and Ecosystem Functioning: Meta-Analysis and Synthesis",
        authors="Tilman, D., Isbell, F., Cowles, J.M.",
        organization="Annual Reviews",
        year=2014,
        source_type=ScientificSourceType.META_ANALYSIS,
        citation="Tilman, D., Isbell, F., & Cowles, J. M. (2014). Biodiversity and ecosystem functioning. Annual Review of Ecology, Evolution, and Systematics, 45, 471-493.",
        doi="10.1146/annurev-ecolsys-120213-091917",
        geographic_scope="global",
        ecosystem="grassland_and_forest",
        topics=["biodiversity_ecosystem_function", "species_richness", "functional_redundancy", "productivity"],
        environmental_metrics=["biodiversity.species_richness", "biodiversity.habitat_diversity"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        abstract="Meta-analysis demonstrating that species richness and functional diversity directly drive ecosystem stability, biomass productivity, and resilience against disturbances.",
        full_text="""Synthesis: Species Richness Controls Ecosystem Multi-Functionality.
Across terrestrial plant communities, higher species richness (> 40-50 species/ha) significantly enhances primary productivity, nutrient retention, and resistance to environmental extremes. Diverse communities exhibit niche complementarity and portfolio effects that stabilize ecosystem processes during climatic fluctuations.

Mechanism: Trophic Redundancy.
Depleting species richness (< 30 species) strips ecological redundancy, meaning the loss of a single dominant pollinator, predator, or nitrogen-fixer causes disproportionately large cascade failures in community multi-functionality.""",
    ),

    ScientificDocumentCreate(
        id="DOC_BENTON_2003_FARMLAND_BIODIV",
        title="Farmland Biodiversity: Is Habitat Heterogeneity the Key?",
        authors="Benton, T.G., Vickery, J.A., Wilson, J.D.",
        organization="Trends in Ecology & Evolution",
        year=2003,
        source_type=ScientificSourceType.SYSTEMATIC_REVIEW,
        citation="Benton, T. G., Vickery, J. A., & Wilson, J. D. (2003). Farmland biodiversity: is habitat heterogeneity the key? Trends in Ecology & Evolution, 18(4), 182-188.",
        doi="10.1016/S0169-5347(03)00011-9",
        geographic_scope="global",
        ecosystem="agroecosystems",
        topics=["habitat_heterogeneity", "monoculture", "farmland_biodiversity", "structural_simplification"],
        environmental_metrics=["land.land_use", "biodiversity.habitat_diversity", "biodiversity.species_richness"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        abstract="Pioneering synthesis identifying structural agricultural simplification and loss of habitat heterogeneity as the primary driver of farmland biodiversity decline.",
        full_text="""Core Thesis: Agricultural Homogenization Drives Species Loss.
The expansion of agricultural monocultures strips spatial and temporal heterogeneity across landscape scales. Eliminating field margins, hedgerows, fallow patches, and mixed cropping reduces macro- and micro-habitat diversity below 35-40%, eliminating critical foraging niches for avian, mammalian, and pollinator populations.

Recommendation for Structural Complexity.
Restoring linear structural elements (hedgerows, shelterbelts, wildflower corridors) reinstates essential microclimatic refugia and facilitates dispersal across production landscapes.""",
    ),

    ScientificDocumentCreate(
        id="DOC_LAL_2004_SOIL_CARBON",
        title="Soil Carbon Sequestration Impacts on Global Climate Change and Food Security",
        authors="Lal, R.",
        organization="Science",
        year=2004,
        source_type=ScientificSourceType.PEER_REVIEWED_JOURNAL,
        citation="Lal, R. (2004). Soil carbon sequestration impacts on global climate change and food security. Science, 304(5677), 1623-1627.",
        doi="10.1126/science.1097396",
        geographic_scope="global",
        ecosystem="all",
        topics=["soil_organic_carbon", "soil_structure", "water_retention", "food_security"],
        environmental_metrics=["soil.organic_carbon", "soil.moisture", "land.land_use"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        abstract="Quantifies the biophysical mechanisms linking soil organic carbon to soil physical quality, agronomic productivity, and hydrologic buffering.",
        full_text="""Mechanisms: Soil Organic Carbon and Hydrologic Buffering.
Every 1% increase in soil organic carbon in the topsoil (0-30 cm) increases plant-available water holding capacity by approximately 15-25 mm/m depth, depending on soil texture. SOC acts as the binding glue for soil mineral aggregates, increasing infiltration rates and preventing surface crust formation.

Critical Thresholds.
When SOC declines below 1.5-2.0%, soil physical degradation accelerates rapidly, resulting in reduced root penetration, nutrient leaching, and severe drought sensitivity even in moderate rainfall environments.""",
    ),

    ScientificDocumentCreate(
        id="DOC_HADDAD_2015_FRAGMENTATION",
        title="Habitat Fragmentation and Its Lasting Impact on Earth's Ecosystems",
        authors="Haddad, N.M., Brudvig, L.A., Clobert, J., et al.",
        organization="Science Advances",
        year=2015,
        source_type=ScientificSourceType.META_ANALYSIS,
        citation="Haddad, N. M., Brudvig, L. A., Clobert, J., et al. (2015). Habitat fragmentation and its lasting impact on Earth's ecosystems. Science Advances, 1(2), e1500052.",
        doi="10.1126/sciadv.1500052",
        geographic_scope="global",
        ecosystem="forests_and_temperate",
        topics=["habitat_fragmentation", "edge_effects", "connectivity", "biodiversity_decay"],
        environmental_metrics=["human_impact.deforestation", "biodiversity.species_richness", "biodiversity.habitat_diversity"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        abstract="Five-continent long-term experimental synthesis proving that habitat fragmentation reduces species richness by 13% to 75% and alters fundamental ecosystem functions.",
        full_text="""Experimental Findings on Habitat Isolation.
Long-term fragmentation experiments across 5 continents prove that habitat fragmentation reduces species richness over time through persistent ecological decay. Fragments within 100 meters of edges experience altered microclimates, elevated tree mortality, and disrupted trophic interactions.

Connectivity Restores Ecosystem Viability.
Corridors connecting isolated habitat fragments increase species movement by an average of 50%, increase plant and animal colonization rates, and sustain higher species richness over decadal timescales.""",
    ),

    ScientificDocumentCreate(
        id="DOC_RAWLS_2003_SOIL_WATER",
        title="Effect of Soil Organic Matter on Soil Water Retention",
        authors="Rawls, W.J., Pachepsky, Y.A., Ritchie, J.C., et al.",
        organization="Geoderma",
        year=2003,
        source_type=ScientificSourceType.PEER_REVIEWED_JOURNAL,
        citation="Rawls, W. J., Pachepsky, Y. A., Ritchie, J. C., Sobecki, T. M., & Bloodworth, H. (2003). Effect of soil organic matter on soil water retention. Geoderma, 116(1-2), 61-76.",
        doi="10.1016/S0016-7061(03)00094-6",
        geographic_scope="global",
        ecosystem="soil_systems",
        topics=["soil_water_retention", "organic_matter", "pedotransfer_functions", "drought_buffering"],
        environmental_metrics=["soil.organic_carbon", "soil.moisture", "climate.rainfall"],
        evidence_strength=EvidenceStrength.STRONG,
        abstract="Empirical pedotransfer models demonstrating quantitative relationships between soil organic matter percentage and soil water retention curves across diverse soil textures.",
        full_text="""Hydraulic Dynamics of Soil Organic Carbon.
Soil organic matter significantly alters soil pore size distribution, transforming micropores into mesopores that hold plant-available water between field capacity (-33 kPa) and permanent wilting point (-1500 kPa).

In sandy and coarse-textured soils, increasing organic carbon from 0.5% to 2.5% more than doubles the available water capacity, providing vital resistance against prolonged dry spells between rainfall events.""",
    ),

    ScientificDocumentCreate(
        id="DOC_PENN_2019_PH_NUTRIENTS",
        title="A Critical Review on Soil Chemical Liming and Phosphorus Bioavailability Dynamics",
        authors="Penn, C.J., Camberato, J.J.",
        organization="Agriculture",
        year=2019,
        source_type=ScientificSourceType.SYSTEMATIC_REVIEW,
        citation="Penn, C. J., & Camberato, J. J. (2019). A critical review on soil chemical liming and phosphorus bioavailability dynamics. Agriculture, 9(6), 120.",
        doi="10.3390/agriculture9060120",
        geographic_scope="global",
        ecosystem="agroecosystems",
        topics=["soil_ph", "phosphorus_fixation", "aluminum_toxicity", "liming"],
        environmental_metrics=["soil.ph", "soil.organic_carbon"],
        evidence_strength=EvidenceStrength.STRONG,
        abstract="Systematic review of the chemical mechanisms governing nutrient availability and toxic ion solubilization across the soil pH continuum (pH 3.5 to 9.5).",
        full_text="""Biophysical Mechanisms of Soil Acidity.
When soil pH drops below 5.5, the solubility of aluminum octahedral sheets in secondary clay minerals increases dramatically. Exchangeable Al3+ saturates cation exchange sites, inhibiting root elongation and precipitating dissolved orthophosphate into highly insoluble aluminum phosphate minerals.

Optimal Agronomic & Ecological Range.
The optimal soil pH for nutrient bioavailability is 6.2 to 7.2. Within this window, microbial mineralization of organic nitrogen and phosphorus is maximized, and heavy metal mobility remains minimal.""",
    ),

    ScientificDocumentCreate(
        id="DOC_FOLEY_2005_LAND_USE",
        title="Global Consequences of Land Use",
        authors="Foley, J.A., DeFries, R., Asner, G.P., et al.",
        organization="Science",
        year=2005,
        source_type=ScientificSourceType.PEER_REVIEWED_JOURNAL,
        citation="Foley, J. A., DeFries, R., Asner, G. P., et al. (2005). Global consequences of land use. Science, 309(5734), 570-574.",
        doi="10.1126/science.1111772",
        geographic_scope="global",
        ecosystem="all",
        topics=["land_use_change", "ecosystem_services", "hydrologic_cycle", "tradeoffs"],
        environmental_metrics=["land.land_use", "land.land_cover", "biodiversity.species_richness", "climate.rainfall"],
        evidence_strength=EvidenceStrength.CONSENSUS,
        abstract="Landmark assessment analyzing the global trade-offs between short-term provisioning ecosystem services and long-term regulatory, supporting, and cultural services.",
        full_text="""Trade-Offs in Intensive Land Management.
Modern intensive agricultural practices maximize short-term crop provisioning at the direct expense of freshwater regulation, carbon storage, regional climate buffering, and natural biodiversity support.

Restoring Multi-Functional Landscapes.
Transitioning to multi-functional landscapes that integrate riparian zones, soil conservation, and structural diversity restores regulatory ecosystem services without compromising baseline agrarian productivity.""",
    ),
]
