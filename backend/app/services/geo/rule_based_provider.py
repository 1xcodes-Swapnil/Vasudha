"""Default local rule-based geographic and ecosystem context provider.

Uses standard WWF Terrestrial Biomes and global ecological boundaries
to resolve region and ecosystem classifications without external API dependencies.
"""

from typing import Dict, Any, List, Tuple
from backend.app.services.geo.base import GeoContextProvider
from backend.app.schemas.geo import GeoContextResult


# Well-known ecological zones defined by [min_lat, max_lat, min_lon, max_lon, region, ecosystem, biome_code]
_ECO_BOUNDARIES: List[Tuple[float, float, float, float, str, str, str]] = [
    # Western Ghats (India)
    (8.0, 21.0, 72.8, 77.5, "Western Ghats", "Tropical Moist Broadleaf Forest", "TMBF_WG"),
    # Deccan Plateau (India)
    (11.0, 22.0, 74.0, 81.0, "Deccan Plateau", "Tropical Dry Deciduous Forest", "TDDF_DP"),
    # Sundarbans / Bengal Delta
    (21.5, 23.0, 88.0, 90.5, "Sundarbans Delta", "Mangrove & Coastal Estuary", "MANG_SB"),
    # Himalayas
    (26.0, 36.0, 73.0, 98.0, "Himalayan Arc", "Montane Grasslands & Shrublands", "MGS_HIM"),
    # Amazon Basin (South America)
    (-15.0, 5.0, -75.0, -48.0, "Amazon Basin", "Tropical Evergreen Rainforest", "TMBF_AMZ"),
    # Cerrado (Brazil)
    (-24.0, -3.0, -60.0, -42.0, "Cerrado Biome", "Tropical & Subtropical Savanna", "TGSS_CER"),
    # Congo Basin (Central Africa)
    (-5.0, 5.0, 11.0, 30.0, "Congo Basin", "Congolian Lowland Forest", "TMBF_COG"),
    # Serengeti / East African Savanna
    (-4.0, 1.0, 34.0, 37.0, "Serengeti Ecoregion", "Tropical Acacia Savanna & Grassland", "TGSS_SER"),
    # Fennoscandia Boreal
    (55.0, 71.0, 4.0, 32.0, "Fennoscandia", "Boreal Forest & Taiga", "BOR_FEN"),
    # Mediterranean Basin
    (30.0, 45.0, -10.0, 36.0, "Mediterranean Basin", "Mediterranean Forests, Woodlands & Scrub", "MED_BAS"),
    # Great Barrier Reef / Queensland Coastal
    (-25.0, -10.0, 142.0, 153.0, "Queensland Coastline", "Tropical Coastal & Coral Estuarine Zone", "MAR_GBR"),
    # North American Great Plains
    (30.0, 55.0, -105.0, -90.0, "Great Plains", "Temperate Grasslands & Savannas", "TGSS_GP"),
    # Pacific Northwest Temperate Rainforest
    (42.0, 60.0, -135.0, -120.0, "Pacific Northwest", "Temperate Coniferous Rainforest", "TCR_PNW"),
]


class RuleBasedGeoContextProvider(GeoContextProvider):
    """Local, offline, zero-network geographic context provider based on ecological zoning."""

    @property
    def name(self) -> str:
        return "rule_based_local"

    @property
    def description(self) -> str:
        return "Deterministic ecological zone mapping derived from WWF Biomes and geographic coordinates."

    def lookup(self, latitude: float, longitude: float) -> GeoContextResult:
        """Resolve region and ecosystem from coordinate boundaries."""
        if latitude < -90.0 or latitude > 90.0:
            raise ValueError(f"Latitude must be in range [-90.0, 90.0], got {latitude}")
        if longitude < -180.0 or longitude > 180.0:
            raise ValueError(f"Longitude must be in range [-180.0, 180.0], got {longitude}")

        # 1. Check known specific high-biodiversity regional boundary intersections
        for min_lat, max_lat, min_lon, max_lon, reg, eco, code in _ECO_BOUNDARIES:
            if min_lat <= latitude <= max_lat and min_lon <= longitude <= max_lon:
                return GeoContextResult(
                    latitude=latitude,
                    longitude=longitude,
                    region=reg,
                    ecosystem=eco,
                    biome_code=code,
                    confidence=0.92,
                    provider_name=self.name,
                    degraded=False,
                )

        # 2. General latitudinal biome fallback
        abs_lat = abs(latitude)
        if abs_lat > 66.5:
            # Polar / Tundra
            region_name = "Arctic/Antarctic Polar" if abs_lat > 75.0 else "Sub-Polar Tundra"
            eco_name = "Tundra & Permafrost Ecoregion"
            biome_code = "TUN_GEN"
        elif 50.0 <= abs_lat <= 66.5:
            # Taiga / Boreal
            region_name = f"High Latitude Zone ({'Northern' if latitude > 0 else 'Southern'})"
            eco_name = "Boreal Forest & Taiga"
            biome_code = "BOR_GEN"
        elif 35.0 <= abs_lat < 50.0:
            # Temperate zone
            region_name = f"Mid-Latitude Temperate Zone ({'North' if latitude > 0 else 'South'})"
            eco_name = "Temperate Broadleaf & Mixed Forest"
            biome_code = "TBM_GEN"
        elif 23.5 <= abs_lat < 35.0:
            # Subtropical
            region_name = f"Subtropical Zone ({'North' if latitude > 0 else 'South'})"
            eco_name = "Subtropical Steppe & Woodland"
            biome_code = "SUB_GEN"
        else:
            # Equatorial / Tropical
            region_name = "Equatorial Belt"
            eco_name = "Tropical & Subtropical Moist Broadleaf Forest"
            biome_code = "TRO_GEN"

        return GeoContextResult(
            latitude=latitude,
            longitude=longitude,
            region=region_name,
            ecosystem=eco_name,
            biome_code=biome_code,
            confidence=0.75,
            provider_name=self.name,
            degraded=False,
        )
