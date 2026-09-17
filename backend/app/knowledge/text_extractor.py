"""Deterministic and semantic extraction of environmental variables from natural language text (Phase 9)."""

import re
from typing import Any, Dict, Optional, Tuple
from backend.app.schemas.environmental_state import (
    EnvironmentalState,
    SoilState,
    LandState,
    BiodiversityState,
    ClimateState,
    HumanImpactState,
    SpatialContext,
)
from backend.app.core.logging import logger


class EnvironmentalTextExtractor:
    """Extracts structured environmental parameters from free-form natural language text."""

    # Precompiled regex patterns for accurate, deterministic parameter extraction
    _PATTERNS = {
        # Soil domain
        "soil.ph": [
            re.compile(r"(?:soil\s*)?ph\s*(?:is|=|:|\bof\b)?\s*([0-9]+(?:\.[0-9]+)?)", re.IGNORECASE),
            re.compile(r"([0-9]+(?:\.[0-9]+)?)\s*ph\b", re.IGNORECASE),
        ],
        "soil.organic_carbon": [
            re.compile(r"(?:soil\s*organic\s*carbon|soc|organic\s*carbon|soil\s*carbon)\s*(?:is|=|:|\bof\b)?\s*([0-9]+(?:\.[0-9]+)?)\s*%", re.IGNORECASE),
            re.compile(r"([0-9]+(?:\.[0-9]+)?)\s*%\s*(?:soc|soil\s*organic\s*carbon|organic\s*carbon)", re.IGNORECASE),
            re.compile(r"(?:soil\s*organic\s*carbon|soc)\s*(?:is|=|:|\bof\b)?\s*([0-9]+(?:\.[0-9]+)?)", re.IGNORECASE),
        ],
        "soil.moisture": [
            re.compile(r"(?:soil\s*moisture|moisture\s*content|moisture)\s*(?:is|=|:|\bof\b)?\s*([0-9]+(?:\.[0-9]+)?)\s*%", re.IGNORECASE),
            re.compile(r"([0-9]+(?:\.[0-9]+)?)\s*%\s*(?:soil\s*moisture|moisture)", re.IGNORECASE),
            re.compile(r"(?:soil\s*moisture)\s*(?:is|=|:|\bof\b)?\s*([0-9]+(?:\.[0-9]+)?)", re.IGNORECASE),
        ],
        # Climate domain
        "climate.temperature": [
            re.compile(r"(?:ambient\s*temperature|mean\s*temperature|temp|temperature)\s*(?:is|=|:|\bof\b)?\s*([+-]?[0-9]+(?:\.[0-9]+)?)\s*(?:°\s*c|c\b|deg\s*c|degrees\s*c)", re.IGNORECASE),
            re.compile(r"([+-]?[0-9]+(?:\.[0-9]+)?)\s*(?:°\s*c|deg\s*c|degrees\s*celsius|degrees\s*c)\b", re.IGNORECASE),
            re.compile(r"(?:temperature|temp)\s*(?:is|=|:|\bof\b)?\s*([+-]?[0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE),
        ],
        "climate.rainfall": [
            re.compile(r"(?:annual\s*rainfall|mean\s*annual\s*precipitation|precipitation|rainfall)\s*(?:is|=|:|\bof\b)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:mm\/yr|mm\/year|mm\b)", re.IGNORECASE),
            re.compile(r"([0-9]+(?:\.[0-9]+)?)\s*(?:mm\s*annual\s*rainfall|mm\s*rainfall|mm\s*precipitation|mm\b)", re.IGNORECASE),
            re.compile(r"(?:rainfall|precipitation)\s*(?:is|=|:|\bof\b)?\s*([0-9]+(?:\.[0-9]+)?)\b", re.IGNORECASE),
        ],
        # Biodiversity domain
        "biodiversity.species_richness": [
            re.compile(r"(?:species\s*richness|species\s*count|richness)\s*(?:is|=|:|\bof\b)?\s*([0-9]+)\s*(?:species|taxa|\bcount\b)?", re.IGNORECASE),
            re.compile(r"([0-9]+)\s*(?:species\s*observed|species\s*recorded|species\s*present)", re.IGNORECASE),
        ],
        "biodiversity.habitat_diversity": [
            re.compile(r"(?:habitat\s*diversity|habitat\s*heterogeneity|structural\s*diversity)\s*(?:is|=|:|\bof\b)?\s*([0-9]+(?:\.[0-9]+)?)\s*%", re.IGNORECASE),
            re.compile(r"([0-9]+(?:\.[0-9]+)?)\s*%\s*(?:habitat\s*diversity|habitat\s*heterogeneity)", re.IGNORECASE),
            re.compile(r"(?:habitat\s*diversity)\s*(?:is|=|:|\bof\b)?\s*([0-9]+(?:\.[0-9]+)?)", re.IGNORECASE),
        ],
        # Human impact domain
        "human_impact.deforestation": [
            re.compile(r"(?:deforestation\s*rate|deforestation|forest\s*loss|canopy\s*loss)\s*(?:is|=|:|\bof\b)?\s*([0-9]+(?:\.[0-9]+)?)\s*%", re.IGNORECASE),
            re.compile(r"([0-9]+(?:\.[0-9]+)?)\s*%\s*(?:deforestation|forest\s*loss|canopy\s*cover\s*loss)", re.IGNORECASE),
            re.compile(r"(?:deforestation)\s*(?:is|=|:|\bof\b)?\s*([0-9]+(?:\.[0-9]+)?)", re.IGNORECASE),
        ],
        "human_impact.pollution": [
            re.compile(r"(?:pollution\s*index|chemical\s*pollution|pollution\s*level|pollution)\s*(?:is|=|:|\bof\b)?\s*([0-9]+(?:\.[0-9]+)?)\s*(?:%|\bindex\b)?", re.IGNORECASE),
            re.compile(r"([0-9]+(?:\.[0-9]+)?)\s*(?:%\s*pollution|pollution\s*score)", re.IGNORECASE),
        ],
        # Coordinates
        "spatial.coordinates": [
            re.compile(r"(?:lat|latitude)\s*(?:is|=|:)?\s*([+-]?[0-9]+(?:\.[0-9]+)?)\s*(?:,|and|\s+)\s*(?:lon|long|longitude)\s*(?:is|=|:)?\s*([+-]?[0-9]+(?:\.[0-9]+)?)", re.IGNORECASE),
            re.compile(r"\(\s*([+-]?[0-9]+(?:\.[0-9]+)?)\s*,\s*([+-]?[0-9]+(?:\.[0-9]+)?)\s*\)"),
        ],
    }

    # Canonical dictionary mappings for categorical variables
    _LAND_USE_KEYWORDS = {
        "monoculture": "monoculture",
        "intensive agriculture": "intensive_agriculture",
        "intensive farming": "intensive_agriculture",
        "agroforestry": "agroforestry",
        "crop field": "cropland",
        "cropland": "cropland",
        "pasture": "pasture",
        "grazing": "pasture",
        "conservation": "conservation",
        "protected area": "conservation",
        "urban": "urban",
        "forestry": "forestry",
        "plantation": "plantation",
    }

    _LAND_COVER_KEYWORDS = {
        "dense forest": "dense_forest",
        "broadleaf forest": "broadleaf_forest",
        "tropical forest": "broadleaf_forest",
        "rainforest": "broadleaf_forest",
        "savanna": "savanna",
        "grassland": "grassland",
        "wetland": "wetland",
        "peatland": "wetland",
        "bare soil": "bare_soil",
        "barren": "bare_soil",
        "sparse vegetation": "sparse_vegetation",
        "shrubland": "shrubland",
    }

    _ECOSYSTEM_KEYWORDS = {
        "tropical rainforest": "tropical_forest",
        "tropical forest": "tropical_forest",
        "rainforest": "tropical_forest",
        "savanna": "savanna",
        "grassland": "grassland",
        "boreal forest": "boreal_forest",
        "taiga": "boreal_forest",
        "peatland": "peatland",
        "wetland": "wetland",
        "semi arid": "semi_arid",
        "semi-arid": "semi_arid",
        "arid": "arid",
        "desert": "desert",
        "mediterranean": "mediterranean",
        "montane": "montane_forest",
        "temperate forest": "temperate_forest",
    }

    _REGION_KEYWORDS = {
        "western ghats": "Western Ghats",
        "amazon": "Amazon Basin",
        "amazon basin": "Amazon Basin",
        "serengeti": "Serengeti",
        "fennoscandia": "Fennoscandia",
        "scandinavia": "Fennoscandia",
        "mediterranean basin": "Mediterranean Basin",
        "atacama": "Atacama Desert",
        "congo": "Congo Basin",
        "congo basin": "Congo Basin",
        "borneo": "Borneo",
    }

    def extract_from_text(self, text: str) -> Tuple[EnvironmentalState, Dict[str, Any]]:
        """Parse natural language text and return a partially populated EnvironmentalState with raw extracted map."""
        extracted: Dict[str, Any] = {}
        if not text or not text.strip():
            return EnvironmentalState(), extracted

        clean_text = text.strip()

        # 1. Extract numeric metrics via regex
        # Soil pH
        for pat in self._PATTERNS["soil.ph"]:
            m = pat.search(clean_text)
            if m:
                val = float(m.group(1))
                if 0.0 <= val <= 14.0:
                    extracted["soil.ph"] = val
                    break

        # Soil Organic Carbon
        for pat in self._PATTERNS["soil.organic_carbon"]:
            m = pat.search(clean_text)
            if m:
                val = float(m.group(1))
                if 0.0 <= val <= 100.0:
                    extracted["soil.organic_carbon"] = val
                    break

        # Soil Moisture
        for pat in self._PATTERNS["soil.moisture"]:
            m = pat.search(clean_text)
            if m:
                val = float(m.group(1))
                if 0.0 <= val <= 100.0:
                    extracted["soil.moisture"] = val
                    break

        # Climate Temperature
        for pat in self._PATTERNS["climate.temperature"]:
            m = pat.search(clean_text)
            if m:
                val = float(m.group(1))
                if -80.0 <= val <= 70.0:
                    extracted["climate.temperature"] = val
                    break

        # Climate Rainfall
        for pat in self._PATTERNS["climate.rainfall"]:
            m = pat.search(clean_text)
            if m:
                val = float(m.group(1))
                if 0.0 <= val <= 15000.0:
                    extracted["climate.rainfall"] = val
                    break

        # Species Richness
        for pat in self._PATTERNS["biodiversity.species_richness"]:
            m = pat.search(clean_text)
            if m:
                val = int(m.group(1))
                if val >= 0:
                    extracted["biodiversity.species_richness"] = val
                    break

        # Habitat Diversity
        for pat in self._PATTERNS["biodiversity.habitat_diversity"]:
            m = pat.search(clean_text)
            if m:
                val = float(m.group(1))
                if 0.0 <= val <= 100.0:
                    extracted["biodiversity.habitat_diversity"] = val
                    break

        # Deforestation
        for pat in self._PATTERNS["human_impact.deforestation"]:
            m = pat.search(clean_text)
            if m:
                val = float(m.group(1))
                if 0.0 <= val <= 100.0:
                    extracted["human_impact.deforestation"] = val
                    break

        # Pollution
        for pat in self._PATTERNS["human_impact.pollution"]:
            m = pat.search(clean_text)
            if m:
                val = float(m.group(1))
                if 0.0 <= val <= 100.0:
                    extracted["human_impact.pollution"] = val
                    break

        # Coordinates
        for pat in self._PATTERNS["spatial.coordinates"]:
            m = pat.search(clean_text)
            if m:
                lat = float(m.group(1))
                lon = float(m.group(2))
                if -90.0 <= lat <= 90.0 and -180.0 <= lon <= 180.0:
                    extracted["spatial_context.latitude"] = lat
                    extracted["spatial_context.longitude"] = lon
                    break

        # 2. Extract Categorical Metrics via Keyword Mapping
        lower_text = clean_text.lower()

        # Land use
        for kw, cat in self._LAND_USE_KEYWORDS.items():
            if re.search(rf"\b{re.escape(kw)}\b", lower_text):
                extracted["land.land_use"] = cat
                break

        # Land cover
        for kw, cat in self._LAND_COVER_KEYWORDS.items():
            if re.search(rf"\b{re.escape(kw)}\b", lower_text):
                extracted["land.land_cover"] = cat
                break

        # Ecosystem
        for kw, eco in self._ECOSYSTEM_KEYWORDS.items():
            if re.search(rf"\b{re.escape(kw)}\b", lower_text):
                extracted["spatial_context.ecosystem"] = eco
                break

        # Region
        for kw, reg in self._REGION_KEYWORDS.items():
            if re.search(rf"\b{re.escape(kw)}\b", lower_text):
                extracted["spatial_context.region"] = reg
                break

        # 3. Construct canonical EnvironmentalState
        soil = SoilState(
            ph=extracted.get("soil.ph"),
            organic_carbon=extracted.get("soil.organic_carbon"),
            moisture=extracted.get("soil.moisture"),
        )
        land = LandState(
            land_use=extracted.get("land.land_use"),
            land_cover=extracted.get("land.land_cover"),
        )
        biodiv = BiodiversityState(
            species_richness=extracted.get("biodiversity.species_richness"),
            habitat_diversity=extracted.get("biodiversity.habitat_diversity"),
        )
        climate = ClimateState(
            temperature=extracted.get("climate.temperature"),
            rainfall=extracted.get("climate.rainfall"),
        )
        human = HumanImpactState(
            pollution=extracted.get("human_impact.pollution"),
            deforestation=extracted.get("human_impact.deforestation"),
        )
        spatial = SpatialContext(
            latitude=extracted.get("spatial_context.latitude"),
            longitude=extracted.get("spatial_context.longitude"),
            region=extracted.get("spatial_context.region"),
            ecosystem=extracted.get("spatial_context.ecosystem"),
        )

        state = EnvironmentalState(
            soil=soil,
            land=land,
            biodiversity=biodiv,
            climate=climate,
            human_impact=human,
            spatial_context=spatial,
        )

        logger.info(f"Extracted {len(extracted)} environmental variables from text query.")
        return state, extracted


# Global singleton instance
text_extractor = EnvironmentalTextExtractor()
