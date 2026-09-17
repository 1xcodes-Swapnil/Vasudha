"""Authoritative Environmental Data Pipeline (Phase 7).

Executes the end-to-end scientific ingestion flow:
Raw Data
→ Coordinate & schema validation
→ Cleaning & type sanitization
→ Unit normalization (e.g. pH*10 to pH, dg/kg or g/kg to % SOC, Kelvin to °C, m to mm)
→ Geographic & temporal harmonization
→ Granular quality checks (Range bounds, observed zero vs missing, out of bounds)
→ Canonical EnvironmentalState representation
→ PostgreSQL / SQLite storage
"""

from typing import Dict, Any, List, Optional, Tuple, Union
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.app.schemas.dataset import (
    RawDatasetObservation,
    DataQualityCheck,
    DataQualityReport,
    VariableProvenance,
    DataQualitySeverity,
    QualityFlagType,
)
from backend.app.schemas.environmental_state import (
    EnvironmentalState,
    SoilState,
    LandState,
    BiodiversityState,
    ClimateState,
    HumanImpactState,
    SpatialContext,
)
from backend.app.models.dataset import IngestedObservationModel
from backend.app.core.logging import logger


class EnvironmentalDataPipeline:
    """End-to-end validator, unit converter, and canonical representation builder."""

    @staticmethod
    def validate_coordinates(
        latitude: float,
        longitude: float,
    ) -> List[DataQualityCheck]:
        """Validate geographic coordinates within EPSG:4326 bounds."""
        checks: List[DataQualityCheck] = []

        if not isinstance(latitude, (int, float)) or not (-90.0 <= float(latitude) <= 90.0):
            checks.append(
                DataQualityCheck(
                    metric_name="spatial_context.latitude",
                    flag_type=QualityFlagType.COORDINATE_OUT_OF_BOUNDS,
                    severity=DataQualitySeverity.ERROR,
                    message=f"Latitude {latitude} is outside valid range [-90.0, 90.0]",
                    original_value=latitude,
                )
            )
        else:
            checks.append(
                DataQualityCheck(
                    metric_name="spatial_context.latitude",
                    flag_type=QualityFlagType.RANGE_VALID,
                    severity=DataQualitySeverity.INFO,
                    message=f"Latitude {latitude} is valid",
                    original_value=latitude,
                    transformed_value=round(float(latitude), 6),
                )
            )

        if not isinstance(longitude, (int, float)) or not (-180.0 <= float(longitude) <= 180.0):
            checks.append(
                DataQualityCheck(
                    metric_name="spatial_context.longitude",
                    flag_type=QualityFlagType.COORDINATE_OUT_OF_BOUNDS,
                    severity=DataQualitySeverity.ERROR,
                    message=f"Longitude {longitude} is outside valid range [-180.0, 180.0]",
                    original_value=longitude,
                )
            )
        else:
            checks.append(
                DataQualityCheck(
                    metric_name="spatial_context.longitude",
                    flag_type=QualityFlagType.RANGE_VALID,
                    severity=DataQualitySeverity.INFO,
                    message=f"Longitude {longitude} is valid",
                    original_value=longitude,
                    transformed_value=round(float(longitude), 6),
                )
            )

        return checks

    @classmethod
    def process_raw_observation(
        cls,
        raw_obs: RawDatasetObservation,
        adapter,
        db_session: Optional[Session] = None,
        region: Optional[str] = None,
        ecosystem: Optional[str] = None,
    ) -> Tuple[EnvironmentalState, DataQualityReport, Dict[str, VariableProvenance]]:
        """Run a raw observation through the full ingestion pipeline."""
        # 1. Coordinate checks
        coord_checks = cls.validate_coordinates(raw_obs.latitude, raw_obs.longitude)

        # 2. Adapter normalization & validation
        canonical_values, adapter_checks, prov_map = adapter.normalize_and_validate(raw_obs)

        all_checks = coord_checks + adapter_checks

        # 3. Check synthetic flag
        if raw_obs.is_synthetic:
            all_checks.append(
                DataQualityCheck(
                    metric_name="all",
                    flag_type=QualityFlagType.SYNTHETIC_DATA,
                    severity=DataQualitySeverity.WARNING,
                    message="Observation marked explicitly as SYNTHETIC data fallback",
                    transformed_value="synthetic",
                )
            )

        # 4. Build canonical EnvironmentalState dict
        state_dict: Dict[str, Any] = {
            "soil": {},
            "land": {},
            "biodiversity": {},
            "climate": {},
            "human_impact": {},
            "spatial_context": {
                "latitude": round(raw_obs.latitude, 6) if -90.0 <= raw_obs.latitude <= 90.0 else None,
                "longitude": round(raw_obs.longitude, 6) if -180.0 <= raw_obs.longitude <= 180.0 else None,
                "region": region,
                "ecosystem": ecosystem,
            },
        }

        missing_vars: List[str] = []
        zero_vars: List[str] = []

        for key, val in canonical_values.items():
            domain, metric = key.split(".", 1)
            if domain in state_dict:
                state_dict[domain][metric] = val
                if val == 0 or val == 0.0:
                    zero_vars.append(key)

        # Audit expected metrics for missing values
        for var in adapter.metadata.variables:
            if var not in canonical_values or canonical_values[var] is None:
                missing_vars.append(var)

        # 5. Build validated EnvironmentalState
        canonical_state = EnvironmentalState.model_validate(state_dict)

        # 6. Aggregate Quality Report
        errors_count = sum(1 for c in all_checks if c.severity == DataQualitySeverity.ERROR)
        warnings_count = sum(1 for c in all_checks if c.severity == DataQualitySeverity.WARNING)
        passed_count = sum(1 for c in all_checks if c.severity == DataQualitySeverity.INFO)
        is_valid = errors_count == 0

        quality_report = DataQualityReport(
            total_checks=len(all_checks),
            passed_checks=passed_count,
            warnings_count=warnings_count,
            errors_count=errors_count,
            is_valid=is_valid,
            checks=all_checks,
            missing_variables=missing_vars,
            zero_variables=zero_vars,
            synthetic_count=1 if raw_obs.is_synthetic else 0,
        )

        # 7. Persist to DB if session provided
        if db_session is not None:
            try:
                obs_model = IngestedObservationModel(
                    dataset_id=adapter.dataset_id,
                    latitude=raw_obs.latitude,
                    longitude=raw_obs.longitude,
                    region=region,
                    ecosystem=ecosystem,
                    raw_payload_json=raw_obs.raw_payload or {},
                    normalized_state_json=canonical_state.model_dump(),
                    provenance_json={k: v.model_dump() for k, v in prov_map.items()},
                    quality_report_json=quality_report.model_dump(),
                    is_valid=is_valid,
                    is_synthetic=raw_obs.is_synthetic,
                )
                db_session.add(obs_model)
                db_session.commit()
                logger.info(f"Persisted ingested observation {obs_model.id} for dataset {adapter.dataset_id}")
            except Exception as exc:
                db_session.rollback()
                logger.warning(f"Failed to persist ingested observation to DB: {exc}")

        return canonical_state, quality_report, prov_map
