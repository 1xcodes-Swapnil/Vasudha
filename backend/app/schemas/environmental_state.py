"""Pydantic schemas and domain models for the Canonical Environmental State.

This module defines the core validated environmental state representing:
EnvironmentalState
├── soil
│   ├── ph
│   ├── organic_carbon
│   └── moisture
├── land
│   ├── land_use
│   └── land_cover
├── biodiversity
│   ├── species_richness
│   └── habitat_diversity
├── climate
│   ├── temperature
│   └── rainfall
├── human_impact
│   ├── pollution
│   └── deforestation
└── spatial_context
    ├── latitude
    ├── longitude
    ├── region
    └── ecosystem
"""

from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field, field_validator, model_validator, ConfigDict
import uuid
from datetime import datetime, timezone


# ==============================================================================
# SUB-STATE MODELS
# ==============================================================================

class SoilState(BaseModel):
    """Soil physical and chemical characteristics.

    Attributes:
        ph: Soil pH on standard 0-14 chemical scale (terrestrial soils typically 2.5 - 11.0).
            Null indicates unmeasured. Zero is chemically possible (extremely hyper-acidic).
        organic_carbon: Soil Organic Carbon (SOC) percentage (0.0% to 100.0%).
            Unit: percentage (wt %).
        moisture: Volumetric/gravimetric soil water content (0.0% to 100.0%).
            Unit: percentage (%). 0 represents completely desiccated soil.
    """
    model_config = ConfigDict(extra="forbid")

    ph: Optional[float] = Field(
        default=None,
        description="Soil pH (0.0 to 14.0 scale). Terrestrial soils typically range from 2.5 to 11.0. Null if unknown.",
    )
    organic_carbon: Optional[float] = Field(
        default=None,
        description="Soil Organic Carbon (SOC) concentration in percent (%) of dry mass. Range: 0.0 - 100.0%.",
    )
    moisture: Optional[float] = Field(
        default=None,
        description="Soil moisture content percentage (%). Range: 0.0 - 100.0%. 0.0 indicates completely dry soil.",
    )

    @field_validator("ph")
    @classmethod
    def validate_ph_range(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return None
        if v < 0.0 or v > 14.0:
            raise ValueError(f"Soil pH must be between 0.0 and 14.0, got {v}")
        return round(v, 2)

    @field_validator("organic_carbon", "moisture")
    @classmethod
    def validate_percentage(cls, v: Optional[float], info) -> Optional[float]:
        if v is None:
            return None
        if v < 0.0 or v > 100.0:
            raise ValueError(f"{info.field_name} must be a percentage between 0.0 and 100.0, got {v}")
        return round(v, 2)


class LandState(BaseModel):
    """Land use categorization and land cover description.

    Attributes:
        land_use: Anthropogenic utilization of land (e.g. 'agriculture', 'forestry', 'conservation', 'grazing').
        land_cover: Physical and biological cover observed (e.g. 'dense_forest', 'savanna', 'wetland', 'bare_soil').
    """
    model_config = ConfigDict(extra="forbid")

    land_use: Optional[str] = Field(
        default=None,
        description="Anthropogenic land use classification (e.g., 'cropland', 'pasture', 'agroforestry', 'conservation', 'urban').",
        max_length=128,
    )
    land_cover: Optional[str] = Field(
        default=None,
        description="Physical vegetative or substrate cover (e.g., 'broadleaf_forest', 'grassland', 'wetland', 'bare_soil').",
        max_length=128,
    )

    @field_validator("land_use", "land_cover")
    @classmethod
    def sanitize_strings(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        return v if v else None


class BiodiversityState(BaseModel):
    """Biodiversity indicators and ecological composition.

    Attributes:
        species_richness: Count of distinct species observed in sampling area.
            Unit: species count (non-negative integer). 0 indicates zero species observed.
        habitat_diversity: Structural or Shannon diversity index (0.0 to 100.0 scale).
            0.0 indicates completely homogenous / mono-habitat.
    """
    model_config = ConfigDict(extra="forbid")

    species_richness: Optional[int] = Field(
        default=None,
        description="Observed species count in surveyed ecosystem. Must be non-negative. 0 indicates zero species found.",
    )
    habitat_diversity: Optional[float] = Field(
        default=None,
        description="Habitat structural diversity or Shannon diversity score (0.0 to 100.0 scale).",
    )

    @field_validator("species_richness")
    @classmethod
    def validate_richness(cls, v: Optional[int]) -> Optional[int]:
        if v is None:
            return None
        if v < 0:
            raise ValueError(f"Species richness cannot be negative, got {v}")
        return v

    @field_validator("habitat_diversity")
    @classmethod
    def validate_diversity(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return None
        if v < 0.0 or v > 100.0:
            raise ValueError(f"Habitat diversity must be between 0.0 and 100.0, got {v}")
        return round(v, 2)


class ClimateState(BaseModel):
    """Climatic regime and meteorological baselines.

    Attributes:
        temperature: Mean annual or observed ambient temperature in Degrees Celsius (°C).
            Earth habitat range: -90.0°C to 60.0°C. 0.0 is the freezing point of water.
        rainfall: Mean annual precipitation or accumulated rainfall in millimeters (mm).
            Must be non-negative. Extreme terrestrial maximum is ~20,000 mm/year.
    """
    model_config = ConfigDict(extra="forbid")

    temperature: Optional[float] = Field(
        default=None,
        description="Ambient or mean annual temperature in Degrees Celsius (°C). Valid range: -90.0 to 60.0.",
    )
    rainfall: Optional[float] = Field(
        default=None,
        description="Mean annual precipitation in millimeters (mm/year). Non-negative, max 20,000 mm.",
    )

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return None
        if v < -90.0 or v > 60.0:
            raise ValueError(f"Temperature must be between -90.0°C and 60.0°C, got {v}")
        return round(v, 2)

    @field_validator("rainfall")
    @classmethod
    def validate_rainfall(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return None
        if v < 0.0:
            raise ValueError(f"Rainfall precipitation cannot be negative, got {v}")
        if v > 20000.0:
            raise ValueError(f"Rainfall exceeds maximum recorded terrestrial precipitation (20,000 mm), got {v}")
        return round(v, 2)


class HumanImpactState(BaseModel):
    """Human anthropogenic pressures and disturbance indicators.

    Attributes:
        pollution: Quantitative pollution index (0.0 to 100.0) or categorical severity.
            When numeric, 0.0 indicates undetectable pollution.
        deforestation: Percentage of forest loss relative to baseline (0.0% to 100.0%).
            0.0% indicates zero detected forest loss.
    """
    model_config = ConfigDict(extra="forbid")

    pollution: Optional[Union[float, str]] = Field(
        default=None,
        description="Pollution level. Can be numeric index (0.0 to 100.0) or categorical ('low', 'moderate', 'severe').",
    )
    deforestation: Optional[float] = Field(
        default=None,
        description="Deforestation rate or percentage of canopy loss (0.0% to 100.0%). 0.0 indicates zero deforestation.",
    )

    @field_validator("pollution")
    @classmethod
    def validate_pollution(cls, v: Optional[Union[float, str]]) -> Optional[Union[float, str]]:
        if v is None:
            return None
        if isinstance(v, (int, float)):
            val = float(v)
            if val < 0.0 or val > 100.0:
                raise ValueError(f"Numeric pollution index must be between 0.0 and 100.0, got {val}")
            return round(val, 2)
        if isinstance(v, str):
            v_str = v.strip()
            if not v_str:
                return None
            return v_str
        raise ValueError(f"Pollution must be a float (0-100) or string description, got {type(v)}")

    @field_validator("deforestation")
    @classmethod
    def validate_deforestation(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return None
        if v < 0.0 or v > 100.0:
            raise ValueError(f"Deforestation percentage must be between 0.0 and 100.0, got {v}")
        return round(v, 2)


class SpatialContext(BaseModel):
    """Geographic, coordinate, and ecosystem zoning context.

    Attributes:
        latitude: Geographic latitude in decimal degrees (-90.0 to +90.0).
        longitude: Geographic longitude in decimal degrees (-180.0 to +180.0).
        region: Administrative or geographic region name (e.g. 'Western Ghats', 'Amazon Basin').
        ecosystem: Ecological biome or habitat type (e.g. 'Tropical Moist Broadleaf Forest', 'Boreal Peatland').
    """
    model_config = ConfigDict(extra="forbid")

    latitude: Optional[float] = Field(
        default=None,
        description="Latitude coordinate in decimal degrees [-90.0, 90.0].",
    )
    longitude: Optional[float] = Field(
        default=None,
        description="Longitude coordinate in decimal degrees [-180.0, 180.0].",
    )
    region: Optional[str] = Field(
        default=None,
        description="Administrative or geographic locality name.",
        max_length=128,
    )
    ecosystem: Optional[str] = Field(
        default=None,
        description="Biome or ecosystem classification type.",
        max_length=128,
    )

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return None
        if v < -90.0 or v > 90.0:
            raise ValueError(f"Latitude must be between -90.0 and 90.0, got {v}")
        return round(v, 6)

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return None
        if v < -180.0 or v > 180.0:
            raise ValueError(f"Longitude must be between -180.0 and 180.0, got {v}")
        return round(v, 6)

    @field_validator("region", "ecosystem")
    @classmethod
    def sanitize_strings(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        v = v.strip()
        return v if v else None


# ==============================================================================
# CANONICAL ENVIRONMENTAL STATE MODEL
# ==============================================================================

class EnvironmentalState(BaseModel):
    """Canonical structured representation of ecological and environmental conditions.

    Hierarchy:
    EnvironmentalState
    ├── soil (ph, organic_carbon, moisture)
    ├── land (land_use, land_cover)
    ├── biodiversity (species_richness, habitat_diversity)
    ├── climate (temperature, rainfall)
    ├── human_impact (pollution, deforestation)
    └── spatial_context (latitude, longitude, region, ecosystem)
    """
    model_config = ConfigDict(extra="forbid")

    soil: SoilState = Field(default_factory=SoilState)
    land: LandState = Field(default_factory=LandState)
    biodiversity: BiodiversityState = Field(default_factory=BiodiversityState)
    climate: ClimateState = Field(default_factory=ClimateState)
    human_impact: HumanImpactState = Field(default_factory=HumanImpactState)
    spatial_context: SpatialContext = Field(default_factory=SpatialContext)

    def is_empty(self) -> bool:
        """Return True if all sub-metrics across every category are null/unspecified."""
        return (
            self.soil.ph is None and
            self.soil.organic_carbon is None and
            self.soil.moisture is None and
            self.land.land_use is None and
            self.land.land_cover is None and
            self.biodiversity.species_richness is None and
            self.biodiversity.habitat_diversity is None and
            self.climate.temperature is None and
            self.climate.rainfall is None and
            self.human_impact.pollution is None and
            self.human_impact.deforestation is None and
            self.spatial_context.latitude is None and
            self.spatial_context.longitude is None and
            self.spatial_context.region is None and
            self.spatial_context.ecosystem is None
        )

    def count_known_metrics(self) -> int:
        """Count how many non-null scientific metrics are currently defined in the state."""
        count = 0
        for category in [self.soil, self.land, self.biodiversity, self.climate, self.human_impact, self.spatial_context]:
            for _, val in category.model_dump().items():
                if val is not None:
                    count += 1
        return count

    def merge_update(self, update_data: Union["EnvironmentalState", Dict[str, Any]]) -> "EnvironmentalState":
        """Merge updates into this state with non-destructive patch semantics.

        Rules:
        1. Explicit values in update_data (including 0 or 0.0) OVERRIDE older values.
        2. Missing keys or explicit None/null in update_data do NOT erase previously known values.
        3. Returns a fresh validated EnvironmentalState instance.
        """
        if isinstance(update_data, EnvironmentalState):
            update_dict = update_data.model_dump(exclude_none=True)
        elif isinstance(update_data, dict):
            update_dict = update_data
        else:
            raise TypeError(f"Expected EnvironmentalState or dict, got {type(update_data)}")

        current_dict = self.model_dump()

        def _recursive_merge(base: dict, patch: dict) -> dict:
            merged = base.copy()
            for key, val in patch.items():
                if val is None:
                    # Missing / null values must NOT erase existing values
                    continue
                if isinstance(val, dict) and isinstance(merged.get(key), dict):
                    merged[key] = _recursive_merge(merged[key], val)
                else:
                    # Explicit value (including 0, 0.0, "", False) overrides
                    merged[key] = val
            return merged

        new_dict = _recursive_merge(current_dict, update_dict)
        return EnvironmentalState.model_validate(new_dict)


# ==============================================================================
# API REQUEST & RESPONSE SCHEMAS
# ==============================================================================

class EnvironmentalStateCreate(BaseModel):
    """Payload to initialize a new environmental profile state."""
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(default=None, description="Optional profile or observation site label.", max_length=255)
    description: Optional[str] = Field(default=None, description="Optional notes or survey narrative.")
    state: EnvironmentalState = Field(default_factory=EnvironmentalState, description="Initial environmental state.")


class EnvironmentalStateUpdate(BaseModel):
    """Payload to update an existing environmental profile state.

    Supports partial input. Missing fields or nulls preserve existing values.
    """
    model_config = ConfigDict(extra="forbid")

    name: Optional[str] = Field(default=None, description="Updated profile label.", max_length=255)
    description: Optional[str] = Field(default=None, description="Updated survey narrative.")
    soil: Optional[SoilState] = None
    land: Optional[LandState] = None
    biodiversity: Optional[BiodiversityState] = None
    climate: Optional[ClimateState] = None
    human_impact: Optional[HumanImpactState] = None
    spatial_context: Optional[SpatialContext] = None


class EnvironmentalStateResponse(BaseModel):
    """Full API representation of a persistent environmental profile."""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(description="Unique UUID identifier of the environmental profile.")
    name: Optional[str] = Field(default=None, description="Profile or site name.")
    description: Optional[str] = Field(default=None, description="Survey or observation description.")
    state: EnvironmentalState = Field(description="Canonical structured environmental state.")
    metrics_count: int = Field(description="Count of currently measured/known environmental variables.")
    created_at: datetime = Field(description="Profile creation timestamp.")
    updated_at: datetime = Field(description="Last update timestamp.")


# Backward compatibility aliases
SoilMetrics = SoilState
LandMetrics = LandState
ClimateMetrics = ClimateState
BiodiversityMetrics = BiodiversityState
HumanImpactMetrics = HumanImpactState

