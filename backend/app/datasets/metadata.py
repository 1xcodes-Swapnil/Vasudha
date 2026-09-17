"""Authoritative Environmental Dataset Registry & Metadata (Phase 7).

Defines authoritative metadata for international environmental datasets:
- SoilGrids (ISRIC): Soil pH, SOC, Moisture
- Copernicus / ESA WorldCover: Land Use and Land Cover
- GBIF: Species Richness, Habitat Diversity
- WorldClim / CHELSA: Mean Annual Temperature, Annual Precipitation
- Global Forest Watch (GFW / Hansen et al.): Deforestation / Tree Cover Loss
- UNEP / WHO / SEDAC: Environmental Pollution Index
"""

from typing import Dict
from backend.app.schemas.dataset import DatasetMetadata


AUTHORITATIVE_DATASETS: Dict[str, DatasetMetadata] = {
    "soilgrids_isric": DatasetMetadata(
        id="soilgrids_isric",
        name="SoilGrids 250m Global Gridded Soil Information",
        source_organization="ISRIC - World Soil Information",
        source_url="https://soilgrids.org",
        license="CC BY 4.0",
        domain="soil",
        variables=["soil.ph", "soil.organic_carbon", "soil.moisture"],
        raw_units={
            "soil.ph": "pH x 10 (in H2O)",
            "soil.organic_carbon": "dg/kg (decigrams per kilogram) or g/kg",
            "soil.moisture": "volumetric water fraction (%) at -33 kPa",
        },
        canonical_units={
            "soil.ph": "pH scale (0.0 - 14.0)",
            "soil.organic_carbon": "% (wt % of dry mass)",
            "soil.moisture": "% (volumetric moisture content)",
        },
        geographic_coverage="Global terrestrial excluding permanently frozen / inland water bodies",
        temporal_coverage="Baseline 1950-2020 harmonized soil profile compilations (WoSIS)",
        spatial_resolution="250m (approx. 0.00208 decimal degrees)",
        retrieval_date="2026-03-01",
        provenance="Machine-learning predictions based on 240,000 global soil profiles from WoSIS and environmental covariates (MODIS, SRTM, WorldClim).",
        known_limitations=[
            "High spatial interpolation uncertainty in sparsely sampled arid, peatland, and tropical interior regions.",
            "pH predictions represent 0-5cm and 5-15cm soil depth layers; subsoil chemistry may vary.",
            "Organic carbon in deep histosols (>1m depth) may be underestimated by surface soil models.",
        ],
        is_authoritative=True,
    ),
    "copernicus_worldcover": DatasetMetadata(
        id="copernicus_worldcover",
        name="ESA WorldCover 10m / Copernicus Land Monitoring Service",
        source_organization="European Space Agency (ESA) & Copernicus",
        source_url="https://worldcover2021.esa.int",
        license="CC BY 4.0",
        domain="land",
        variables=["land.land_use", "land.land_cover"],
        raw_units={
            "land.land_use": "Categorical Anthropogenic Land Use",
            "land.land_cover": "Categorical Discrete LULC Class (10m pixels)",
        },
        canonical_units={
            "land.land_use": "Standard Land Use taxonomy ('cropland', 'pasture', 'agroforestry', 'conservation', 'urban')",
            "land.land_cover": "Standard Land Cover taxonomy ('dense_forest', 'savanna', 'grassland', 'wetland', 'bare_soil')",
        },
        geographic_coverage="Global terrestrial land surface",
        temporal_coverage="2020-2023 annual Sentinel-1 and Sentinel-2 satellite observations",
        spatial_resolution="10m optical/radar composite",
        retrieval_date="2026-03-01",
        provenance="Random forest and deep learning classification of Sentinel-1 radar and Sentinel-2 optical time series calibrated with international ground-truth datasets.",
        known_limitations=[
            "Persistent cloud cover in equatorial regions may cause seasonal misclassification between shrubland and tree cover.",
            "Sub-pixel urban vegetation and smallholder agroforestry patches (<10m) may be classified as pure cropland.",
        ],
        is_authoritative=True,
    ),
    "gbif_occurrence": DatasetMetadata(
        id="gbif_occurrence",
        name="GBIF Global Biodiversity Occurrence & Taxon Grid Index",
        source_organization="Global Biodiversity Information Facility (GBIF) Secretariat",
        source_url="https://www.gbif.org",
        license="CC0 / CC BY 4.0",
        domain="biodiversity",
        variables=["biodiversity.species_richness", "biodiversity.habitat_diversity"],
        raw_units={
            "biodiversity.species_richness": "Sampled taxon/species count within grid radius",
            "biodiversity.habitat_diversity": "Shannon diversity / structural diversity score (0.0 - 100.0)",
        },
        canonical_units={
            "biodiversity.species_richness": "Species count (integer >= 0)",
            "biodiversity.habitat_diversity": "Diversity index (0.0 - 100.0 scale)",
        },
        geographic_coverage="Global terrestrial and marine biodiversity occurrences",
        temporal_coverage="1900-2026 curated specimen and observation records",
        spatial_resolution="Aggregated 1km to 10km regional sampling grid",
        retrieval_date="2026-03-01",
        provenance="Harmonized specimen museum records, citizen science (iNaturalist, eBird), and ecological survey transects with taxonomic Darwin Core verification.",
        known_limitations=[
            "Geographic sampling bias towards accessible roads, protected areas, and developed regions (Wallacean and Darwinian shortfalls).",
            "Species counts in remote biomes represent sampled occurrences, not exhaustive community censuses.",
        ],
        is_authoritative=True,
    ),
    "worldclim_v2": DatasetMetadata(
        id="worldclim_v2",
        name="WorldClim v2.1 Global High-Resolution Climatology",
        source_organization="WorldClim / University of California, Davis / CHELSA",
        source_url="https://www.worldclim.org",
        license="CC BY-SA 4.0",
        domain="climate",
        variables=["climate.temperature", "climate.rainfall"],
        raw_units={
            "climate.temperature": "BIO1 Annual Mean Temperature in °C",
            "climate.rainfall": "BIO12 Annual Precipitation in mm/year",
        },
        canonical_units={
            "climate.temperature": "Degrees Celsius (°C)",
            "climate.rainfall": "Millimeters per year (mm/year)",
        },
        geographic_coverage="Global terrestrial land surfaces excluding Antarctica",
        temporal_coverage="1970-2000 30-year climatological normal baseline",
        spatial_resolution="30 arc-seconds (~1 km at the equator)",
        retrieval_date="2026-03-01",
        provenance="Thin-plate spline interpolation of weather station records (GHCN, WMO) using elevation, satellite covariates (SRTM, MODIS LST), and distance to coast.",
        known_limitations=[
            "Represents long-term climatological normals rather than real-time daily weather anomalies.",
            "High-elevation mountainous precipitation gradients exhibit interpolation smoothing in areas with low station density.",
        ],
        is_authoritative=True,
    ),
    "global_forest_watch": DatasetMetadata(
        id="global_forest_watch",
        name="Global Forest Watch / Hansen Global Forest Change v1.10",
        source_organization="University of Maryland (GLAD) & World Resources Institute (WRI)",
        source_url="https://www.globalforestwatch.org",
        license="CC BY 4.0",
        domain="human_impact",
        variables=["human_impact.deforestation"],
        raw_units={
            "human_impact.deforestation": "Cumulative forest canopy cover loss (% relative to year 2000 baseline)",
        },
        canonical_units={
            "human_impact.deforestation": "% of forest loss (0.0% - 100.0%)",
        },
        geographic_coverage="Global terrestrial forest biomes (canopy closure > 5m)",
        temporal_coverage="2000-2024 annual time series",
        spatial_resolution="30m Landsat / Sentinel multi-spectral resolution",
        retrieval_date="2026-03-01",
        provenance="Time-series analysis of Landsat and Sentinel-2 satellite imagery detecting stand-replacement disturbance and canopy loss.",
        known_limitations=[
            "Cannot distinguish between commercial timber harvesting, rotational plantation forestry, wildfire, and permanent agricultural conversion without contextual land-use layers.",
            "0.0% deforestation denotes zero detected stand-replacement canopy loss, not necessarily zero selective logging.",
        ],
        is_authoritative=True,
    ),
    "unep_sedac_pollution": DatasetMetadata(
        id="unep_sedac_pollution",
        name="UNEP Global Environment Monitoring & SEDAC Environmental Pollution Baseline",
        source_organization="United Nations Environment Programme (UNEP) & NASA SEDAC / WHO",
        source_url="https://sedac.ciesin.columbia.edu",
        license="CC BY 4.0",
        domain="human_impact",
        variables=["human_impact.pollution"],
        raw_units={
            "human_impact.pollution": "Harmonized Ambient Pollution Index (0 - 100) based on annual PM2.5 and nitrogen oxide exposure",
        },
        canonical_units={
            "human_impact.pollution": "Numeric pollution index (0.0 - 100.0) or categorical descriptor",
        },
        geographic_coverage="Global terrestrial surface",
        temporal_coverage="2015-2024 satellite-derived annual aerosol optical depth & ground station calibration",
        spatial_resolution="0.01 to 0.1 decimal degrees (~1km to ~10km)",
        retrieval_date="2026-03-01",
        provenance="Atmospheric chemistry models (GEOS-Chem) integrating satellite MODIS/MISR/VIIRS aerosol optical depth with surface air quality monitoring networks.",
        known_limitations=[
            "Desert dust events and seasonal biomass burning can elevate optical depth readings in semi-arid and savanna ecosystems.",
            "Water and soil ecotoxicity are approximated through combined industrial runoff and agrochemical proximity proxies.",
        ],
        is_authoritative=True,
    ),
}
