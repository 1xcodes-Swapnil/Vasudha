"""Pydantic schemas for Geographic Context (Phase 2)."""

from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from backend.app.schemas.environmental_state import SpatialContext, EnvironmentalState


class GeoLookupRequest(BaseModel):
    """Request payload for geographic context lookup by coordinates."""
    model_config = ConfigDict(extra="forbid")

    latitude: float = Field(
        ...,
        description="Latitude coordinate in decimal degrees [-90.0, 90.0].",
    )
    longitude: float = Field(
        ...,
        description="Longitude coordinate in decimal degrees [-180.0, 180.0].",
    )

    @field_validator("latitude")
    @classmethod
    def validate_latitude(cls, v: float) -> float:
        if v < -90.0 or v > 90.0:
            raise ValueError(f"Latitude must be between -90.0 and 90.0 decimal degrees, got {v}")
        return round(v, 6)

    @field_validator("longitude")
    @classmethod
    def validate_longitude(cls, v: float) -> float:
        if v < -180.0 or v > 180.0:
            raise ValueError(f"Longitude must be between -180.0 and 180.0 decimal degrees, got {v}")
        return round(v, 6)


class GeoContextResult(BaseModel):
    """Result of geographic context resolution."""
    model_config = ConfigDict(extra="forbid")

    latitude: float = Field(..., description="Latitude coordinate.")
    longitude: float = Field(..., description="Longitude coordinate.")
    region: Optional[str] = Field(default=None, description="Identified region or locality name.")
    ecosystem: Optional[str] = Field(default=None, description="Identified biome or ecosystem classification.")
    biome_code: Optional[str] = Field(default=None, description="Standard biome classification code if known.")
    elevation_estimate_m: Optional[float] = Field(default=None, description="Approximate elevation in meters.")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score of geospatial assignment.")
    provider_name: str = Field(default="unknown", description="Name of the GeoContextProvider used.")
    degraded: bool = Field(default=False, description="True if provider failed or returned incomplete fallback.")

    def to_spatial_context(self) -> SpatialContext:
        """Convert result into canonical SpatialContext."""
        return SpatialContext(
            latitude=self.latitude,
            longitude=self.longitude,
            region=self.region,
            ecosystem=self.ecosystem,
        )


class GeoStateSyncRequest(BaseModel):
    """Request to update or clear the spatial context inside an EnvironmentalState."""
    model_config = ConfigDict(extra="forbid")

    state: EnvironmentalState = Field(..., description="Existing environmental state to be updated.")
    latitude: Optional[float] = Field(default=None, description="New latitude or None.")
    longitude: Optional[float] = Field(default=None, description="New longitude or None.")
    region: Optional[str] = Field(default=None, description="New region name or None.")
    ecosystem: Optional[str] = Field(default=None, description="New ecosystem or None.")
    auto_enrich: bool = Field(default=True, description="Whether to auto-resolve region/ecosystem if coordinates provided.")
    clear_location: bool = Field(default=False, description="If True, clears spatial coordinates and context.")

    @field_validator("latitude")
    @classmethod
    def validate_lat(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return None
        if v < -90.0 or v > 90.0:
            raise ValueError(f"Latitude must be between -90.0 and 90.0, got {v}")
        return round(v, 6)

    @field_validator("longitude")
    @classmethod
    def validate_lon(cls, v: Optional[float]) -> Optional[float]:
        if v is None:
            return None
        if v < -180.0 or v > 180.0:
            raise ValueError(f"Longitude must be between -180.0 and 180.0, got {v}")
        return round(v, 6)


class GeoStateSyncResponse(BaseModel):
    """Response containing updated EnvironmentalState with spatial context modified."""
    model_config = ConfigDict(extra="forbid")

    state: EnvironmentalState = Field(..., description="Updated canonical EnvironmentalState.")
    spatial_context: SpatialContext = Field(..., description="The synchronized spatial context.")
    metrics_count: int = Field(..., description="Total non-null ecological metrics.")
    enrichment_status: str = Field(default="ok", description="Status of geographic enrichment.")
    provider: str = Field(default="rule_based", description="Provider used for spatial resolution.")


class GeoProviderInfo(BaseModel):
    """Metadata describing a registered GeoContextProvider."""
    model_config = ConfigDict(extra="forbid")

    name: str
    description: str
    is_active: bool
    requires_api_key: bool
    status: str
    capabilities: Dict[str, Any] = Field(default_factory=dict)
