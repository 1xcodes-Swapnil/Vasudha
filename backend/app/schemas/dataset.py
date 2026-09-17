"""Pydantic schemas for Authoritative Environmental Datasets, Data Pipeline & Provenance (Phase 7).

Defines schemas for:
- Authoritative Dataset Metadata (Source, License, Resolution, Variables, Provenance)
- Raw Observations, Ingestion Payloads, and Unit Normalization
- Data Quality Checks (Range, Boundary, Missing vs Zero, Temporal, Outlier)
- Provenance Tracking per Variable
- Point Query & State Enrichment Responses
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, date
from enum import Enum

from backend.app.schemas.environmental_state import (
    EnvironmentalState,
    SoilState,
    LandState,
    BiodiversityState,
    ClimateState,
    HumanImpactState,
    SpatialContext,
)


class DataQualitySeverity(str, Enum):
    """Severity of a data quality flag."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class QualityFlagType(str, Enum):
    """Specific category of data quality check."""
    RANGE_VALID = "range_valid"
    RANGE_OUT_OF_BOUNDS = "range_out_of_bounds"
    UNIT_CONVERTED = "unit_converted"
    MISSING_VALUE = "missing_value"
    OBSERVED_ZERO = "observed_zero"
    COORDINATE_OUT_OF_BOUNDS = "coordinate_out_of_bounds"
    DUPLICATE_RECORD = "duplicate_record"
    TEMPORAL_OUTDATED = "temporal_outdated"
    SYNTHETIC_DATA = "synthetic_data"
    ADAPTER_DEGRADED = "adapter_degraded"


class DataQualityCheck(BaseModel):
    """Individual quality check result for an environmental metric."""
    model_config = ConfigDict(extra="forbid")

    metric_name: str = Field(description="Variable identifier, e.g. 'soil.ph', 'climate.rainfall'")
    flag_type: QualityFlagType = Field(description="Quality check classification")
    severity: DataQualitySeverity = Field(description="Severity of the flag")
    message: str = Field(description="Detailed description of check result or transformation")
    original_value: Optional[Any] = Field(default=None, description="Raw input value before cleaning/conversion")
    transformed_value: Optional[Any] = Field(default=None, description="Cleaned or converted value")
    applied_rule: Optional[str] = Field(default=None, description="Scientific rule or conversion formula applied")


class VariableProvenance(BaseModel):
    """Provenance and scientific attribution for an individual environmental variable."""
    model_config = ConfigDict(extra="forbid")

    variable_name: str = Field(description="Standardized variable path (e.g., 'soil.organic_carbon')")
    dataset_id: str = Field(description="Dataset identifier (e.g., 'soilgrids_isric', 'worldclim_v2')")
    dataset_name: str = Field(description="Authoritative dataset name")
    source_organization: str = Field(description="Publishing scientific institution")
    source_url: str = Field(description="Authoritative repository or API endpoint URL")
    license: str = Field(description="Data licensing terms (e.g., 'CC BY 4.0')")
    raw_value: Optional[Any] = Field(default=None, description="Raw value as supplied by provider")
    raw_unit: Optional[str] = Field(default=None, description="Original unit of measurement")
    canonical_value: Optional[Any] = Field(default=None, description="Normalized value in canonical schema")
    canonical_unit: str = Field(description="Canonical unit (e.g., '%', '°C', 'mm/year')")
    spatial_resolution: str = Field(description="Grid cell size or spatial resolution")
    temporal_coverage: str = Field(description="Time interval or climatological baseline period")
    retrieval_date: str = Field(description="ISO date when data was retrieved/sampled")
    is_synthetic: bool = Field(default=False, description="True if synthetic fallback was used")
    known_limitations: List[str] = Field(default_factory=list, description="Caveats and uncertainty bounds")


class DatasetMetadata(BaseModel):
    """Metadata specification for an authoritative environmental data source."""
    model_config = ConfigDict(extra="forbid")

    id: str = Field(description="Unique dataset key (e.g., 'soilgrids_isric')")
    name: str = Field(description="Full official title of dataset")
    source_organization: str = Field(description="Lead institutional author or custodian")
    source_url: str = Field(description="Direct URL to portal, documentation, or API")
    license: str = Field(description="Distribution and reuse license")
    domain: str = Field(description="Environmental domain: soil | land | biodiversity | climate | human_impact | spatial")
    variables: List[str] = Field(description="Environmental metrics supplied by this dataset")
    raw_units: Dict[str, str] = Field(description="Mapping of variable to source unit")
    canonical_units: Dict[str, str] = Field(description="Mapping of variable to canonical unit")
    geographic_coverage: str = Field(description="Spatial extent (e.g., 'Global terrestrial', 'Continental')")
    temporal_coverage: str = Field(description="Temporal window or baseline (e.g., '1970-2000 climatology', '2020-2023')")
    spatial_resolution: str = Field(description="Nominal spatial resolution (e.g., '250m', '1km (30 arc-sec)', '10m')")
    retrieval_date: str = Field(description="Snapshot or retrieval timestamp")
    provenance: str = Field(description="Origin, scientific methodology, and collection protocol")
    known_limitations: List[str] = Field(description="Known uncertainties, satellite sensor limitations, or interpolation biases")
    is_authoritative: bool = Field(default=True, description="True if vetted by international bodies (FAO, ESA, GBIF, etc.)")


class RawDatasetObservation(BaseModel):
    """Raw un-normalized data record submitted from external API or raster sampler."""
    model_config = ConfigDict(extra="allow")

    dataset_id: str = Field(description="Target dataset identifier")
    latitude: float = Field(description="Latitude coordinate [-90.0, 90.0]")
    longitude: float = Field(description="Longitude coordinate [-180.0, 180.0]")
    timestamp: Optional[str] = Field(default=None, description="Observation or extraction timestamp")
    raw_payload: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary raw response key-value map")
    is_synthetic: bool = Field(default=False, description="Flag explicitly marking synthetic/demo data")


class DataQualityReport(BaseModel):
    """Aggregated data quality report across the dataset ingestion pipeline."""
    model_config = ConfigDict(extra="forbid")

    total_checks: int = Field(default=0, description="Total number of quality rules evaluated")
    passed_checks: int = Field(default=0, description="Checks passed with no issues")
    warnings_count: int = Field(default=0, description="Non-fatal warnings (e.g. Unit conversion, high elevation)")
    errors_count: int = Field(default=0, description="Fatal validation errors (e.g. Impossible pH, invalid coords)")
    is_valid: bool = Field(default=True, description="True if no fatal errors were detected")
    checks: List[DataQualityCheck] = Field(default_factory=list, description="List of granular quality checks")
    missing_variables: List[str] = Field(default_factory=list, description="Variables with no observed data (None)")
    zero_variables: List[str] = Field(default_factory=list, description="Variables with observed zero values (valid zero)")
    synthetic_count: int = Field(default=0, description="Number of variables filled with synthetic data")


class PointQueryResult(BaseModel):
    """Full response from querying authoritative environmental datasets for a geographic point."""
    model_config = ConfigDict(extra="forbid")

    latitude: float = Field(description="Target latitude coordinate")
    longitude: float = Field(description="Target longitude coordinate")
    canonical_state: EnvironmentalState = Field(description="Merged, validated canonical EnvironmentalState")
    provenance_records: Dict[str, VariableProvenance] = Field(
        default_factory=dict,
        description="Per-metric provenance map linking each variable to its authoritative dataset source",
    )
    quality_report: DataQualityReport = Field(description="Quality audit and conversion log")
    datasets_queried: List[str] = Field(description="List of dataset IDs evaluated in this query")
    is_fully_authoritative: bool = Field(description="True if all populated variables originate from authoritative sources")
    has_synthetic_data: bool = Field(default=False, description="True if any metric is marked synthetic")


class StateEnrichmentRequest(BaseModel):
    """Payload to enrich an existing EnvironmentalState using authoritative datasets."""
    model_config = ConfigDict(extra="forbid")

    state: EnvironmentalState = Field(description="Initial environmental state (may have user-defined values or coordinates)")
    latitude: Optional[float] = Field(default=None, description="Optional override latitude")
    longitude: Optional[float] = Field(default=None, description="Optional override longitude")
    overwrite_existing: bool = Field(
        default=False,
        description="If True, overwrite user values with dataset values. If False (default), only fill missing/null fields.",
    )
    allow_synthetic_fallback: bool = Field(
        default=False,
        description="Allow synthetic fallback if external datasets are unreachable or coordinates out of regional bounds.",
    )


class StateEnrichmentResponse(BaseModel):
    """Result of enriching an EnvironmentalState with authoritative dataset records."""
    model_config = ConfigDict(extra="forbid")

    enriched_state: EnvironmentalState = Field(description="Resulting EnvironmentalState after enrichment")
    metrics_added_count: int = Field(description="Count of missing metrics newly populated from datasets")
    metrics_preserved_count: int = Field(description="Count of preexisting metrics retained")
    provenance_records: Dict[str, VariableProvenance] = Field(description="Provenance for all populated variables")
    quality_report: DataQualityReport = Field(description="Quality check audit")
