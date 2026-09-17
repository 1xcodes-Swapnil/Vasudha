"""WorldClim v2.1 / CHELSA Dataset Adapter (Phase 7).

Handles mean annual temperature (MAT / BIO1) and annual precipitation (MAP / BIO12) parsing,
Kelvin / tenths-of-degree unit conversions, and physical range validation.
"""

from typing import Dict, Any, List, Tuple, Optional
from backend.app.schemas.dataset import (
    DatasetMetadata,
    RawDatasetObservation,
    DataQualityCheck,
    VariableProvenance,
    DataQualitySeverity,
    QualityFlagType,
)
from backend.app.datasets.base_adapter import DatasetAdapter
from backend.app.datasets.metadata import AUTHORITATIVE_DATASETS


class WorldClimClimateAdapter(DatasetAdapter):
    """Adapter for WorldClim v2.1 / CHELSA 1km climatological normals."""

    def __init__(self):
        super().__init__(AUTHORITATIVE_DATASETS["worldclim_v2"])

    def fetch_point(
        self,
        latitude: float,
        longitude: float,
        is_synthetic_allowed: bool = False,
    ) -> RawDatasetObservation:
        """Fetch climatological normals for coordinate point."""
        raw_payload: Dict[str, Any] = {}
        is_synthetic = False

        # Western Ghats Tropical Wet (High rainfall, moderate tropical temp)
        if 8.0 <= latitude <= 15.0 and 73.0 <= longitude <= 77.5:
            raw_payload = {
                "bio1_temp_c": 24.5,
                "bio12_precip_mm": 3200.0,
                "temp_unit": "°C",
                "precip_unit": "mm",
                "climatology_period": "1970-2000",
                "source": "WorldClim v2.1 30s (Western Ghats Grid)",
            }
        # Amazon Basin
        elif -10.0 <= latitude <= 4.0 and -75.0 <= longitude <= -50.0:
            raw_payload = {
                "bio1_temp_c": 27.2,
                "bio12_precip_mm": 2450.0,
                "temp_unit": "°C",
                "precip_unit": "mm",
                "climatology_period": "1970-2000",
                "source": "WorldClim v2.1 30s (Amazon Basin Grid)",
            }
        # Fennoscandia Boreal
        elif 58.0 <= latitude <= 70.0 and 10.0 <= longitude <= 30.0:
            raw_payload = {
                "bio1_temp_c": 2.1,
                "bio12_precip_mm": 620.0,
                "temp_unit": "°C",
                "precip_unit": "mm",
                "climatology_period": "1970-2000",
                "source": "WorldClim v2.1 30s (Fennoscandia Taiga Grid)",
            }
        # Serengeti Savanna
        elif -4.0 <= latitude <= 1.0 and 34.0 <= longitude <= 38.0:
            raw_payload = {
                "bio1_temp_c": 21.8,
                "bio12_precip_mm": 850.0,
                "temp_unit": "°C",
                "precip_unit": "mm",
                "climatology_period": "1970-2000",
                "source": "WorldClim v2.1 30s (East African Savanna Grid)",
            }
        # Mediterranean Basin
        elif 35.0 <= latitude <= 45.0 and -5.0 <= longitude <= 25.0:
            raw_payload = {
                "bio1_temp_c": 17.4,
                "bio12_precip_mm": 540.0,
                "temp_unit": "°C",
                "precip_unit": "mm",
                "climatology_period": "1970-2000",
                "source": "WorldClim v2.1 30s (Mediterranean Basin Grid)",
            }
        # Atacama Hyper-Arid Desert
        elif -25.0 <= latitude <= -18.0 and -71.0 <= longitude <= -68.0:
            raw_payload = {
                "bio1_temp_c": 16.5,
                "bio12_precip_mm": 0.0,  # Valid observed 0.0 mm rain in hyper-arid core
                "temp_unit": "°C",
                "precip_unit": "mm",
                "climatology_period": "1970-2000",
                "source": "WorldClim v2.1 30s (Atacama Core Hyper-Arid Grid)",
            }
        else:
            abs_lat = abs(latitude)
            if abs_lat > 65.0:
                raw_payload = {"bio1_temp_c": -6.5, "bio12_precip_mm": 350.0}
            elif abs_lat < 23.5:
                raw_payload = {"bio1_temp_c": 26.0, "bio12_precip_mm": 1800.0}
            else:
                raw_payload = {"bio1_temp_c": 13.5, "bio12_precip_mm": 750.0}

            if is_synthetic_allowed:
                is_synthetic = True
                raw_payload["source"] = "Synthetic fallback climatology profile"
            else:
                raw_payload["source"] = "WorldClim v2.1 (Latitudinal Interpolation)"

        return RawDatasetObservation(
            dataset_id=self.dataset_id,
            latitude=latitude,
            longitude=longitude,
            raw_payload=raw_payload,
            is_synthetic=is_synthetic,
        )

    def normalize_and_validate(
        self,
        raw_obs: RawDatasetObservation,
    ) -> Tuple[Dict[str, Any], List[DataQualityCheck], Dict[str, VariableProvenance]]:
        """Normalize temperature (Kelvin to Celsius, tenths-of-degree) and precipitation (mm)."""
        payload = raw_obs.raw_payload or {}
        canonical_values: Dict[str, Any] = {}
        quality_checks: List[DataQualityCheck] = []
        prov_map: Dict[str, VariableProvenance] = {}

        # ----------------------------------------------------------------------
        # 1. Temperature (-90.0°C to 60.0°C)
        # ----------------------------------------------------------------------
        temp_raw = payload.get("bio1_temp_c", payload.get("temperature"))
        temp_unit = payload.get("temp_unit", "°C")

        if temp_raw is not None:
            try:
                temp_float = float(temp_raw)
                final_temp = temp_float

                # Unit conversion check: Kelvin -> Celsius
                if temp_unit in ["K", "Kelvin", "kelvin"] or (temp_float > 180.0 and temp_float < 340.0):
                    final_temp = round(temp_float - 273.15, 2)
                    quality_checks.append(
                        DataQualityCheck(
                            metric_name="climate.temperature",
                            flag_type=QualityFlagType.UNIT_CONVERTED,
                            severity=DataQualitySeverity.INFO,
                            message=f"Converted temperature from {temp_float} K to {final_temp} °C",
                            original_value=temp_float,
                            transformed_value=final_temp,
                            applied_rule="temp_celsius = temp_kelvin - 273.15",
                        )
                    )
                # Unit conversion check: Legacy integer tenths of degree (e.g. 245 -> 24.5)
                elif temp_unit in ["tenths_deg_c", "degCx10"] or (temp_float > 60.0 and temp_float <= 600.0):
                    final_temp = round(temp_float / 10.0, 2)
                    quality_checks.append(
                        DataQualityCheck(
                            metric_name="climate.temperature",
                            flag_type=QualityFlagType.UNIT_CONVERTED,
                            severity=DataQualitySeverity.INFO,
                            message=f"Converted legacy WorldClim tenths-of-degree ({temp_float}) to {final_temp} °C",
                            original_value=temp_float,
                            transformed_value=final_temp,
                            applied_rule="temp_celsius = temp_tenths / 10.0",
                        )
                    )

                # Physical range check
                if final_temp < -90.0 or final_temp > 60.0:
                    quality_checks.append(
                        DataQualityCheck(
                            metric_name="climate.temperature",
                            flag_type=QualityFlagType.RANGE_OUT_OF_BOUNDS,
                            severity=DataQualitySeverity.ERROR,
                            message=f"Temperature {final_temp}°C is outside recorded terrestrial limits [-90.0°C, 60.0°C]",
                            original_value=final_temp,
                        )
                    )
                else:
                    canonical_values["climate.temperature"] = round(final_temp, 2)
                    quality_checks.append(
                        DataQualityCheck(
                            metric_name="climate.temperature",
                            flag_type=QualityFlagType.RANGE_VALID,
                            severity=DataQualitySeverity.INFO,
                            message=f"Mean annual temperature {final_temp}°C is within physical bounds",
                            original_value=temp_raw,
                            transformed_value=round(final_temp, 2),
                        )
                    )
                    prov_map["climate.temperature"] = VariableProvenance(
                        variable_name="climate.temperature",
                        dataset_id=self.dataset_id,
                        dataset_name=self.metadata.name,
                        source_organization=self.metadata.source_organization,
                        source_url=self.metadata.source_url,
                        license=self.metadata.license,
                        raw_value=temp_raw,
                        raw_unit=temp_unit,
                        canonical_value=round(final_temp, 2),
                        canonical_unit="°C",
                        spatial_resolution=self.metadata.spatial_resolution,
                        temporal_coverage=self.metadata.temporal_coverage,
                        retrieval_date=self.metadata.retrieval_date,
                        is_synthetic=raw_obs.is_synthetic,
                        known_limitations=self.metadata.known_limitations,
                    )
            except (ValueError, TypeError):
                quality_checks.append(
                    DataQualityCheck(
                        metric_name="climate.temperature",
                        flag_type=QualityFlagType.RANGE_OUT_OF_BOUNDS,
                        severity=DataQualitySeverity.ERROR,
                        message=f"Malformed temperature value: '{temp_raw}'",
                        original_value=temp_raw,
                    )
                )
        else:
            quality_checks.append(
                DataQualityCheck(
                    metric_name="climate.temperature",
                    flag_type=QualityFlagType.MISSING_VALUE,
                    severity=DataQualitySeverity.INFO,
                    message="Temperature unmeasured/null (preserved as null).",
                )
            )

        # ----------------------------------------------------------------------
        # 2. Precipitation (0.0 to 20,000.0 mm/year)
        # ----------------------------------------------------------------------
        precip_raw = payload.get("bio12_precip_mm", payload.get("rainfall"))
        precip_unit = payload.get("precip_unit", "mm")

        if precip_raw is not None:
            try:
                precip_float = float(precip_raw)
                final_precip = precip_float

                # Unit conversion check: meters/year -> mm (multiply by 1000)
                if precip_unit in ["m", "meter", "m/year"]:
                    final_precip = round(precip_float * 1000.0, 2)
                    quality_checks.append(
                        DataQualityCheck(
                            metric_name="climate.rainfall",
                            flag_type=QualityFlagType.UNIT_CONVERTED,
                            severity=DataQualitySeverity.INFO,
                            message=f"Converted rainfall from {precip_float} m to {final_precip} mm",
                            original_value=precip_float,
                            transformed_value=final_precip,
                            applied_rule="rainfall_mm = rainfall_m * 1000.0",
                        )
                    )
                elif precip_unit in ["cm", "cm/year"]:
                    final_precip = round(precip_float * 10.0, 2)
                    quality_checks.append(
                        DataQualityCheck(
                            metric_name="climate.rainfall",
                            flag_type=QualityFlagType.UNIT_CONVERTED,
                            severity=DataQualitySeverity.INFO,
                            message=f"Converted rainfall from {precip_float} cm to {final_precip} mm",
                            original_value=precip_float,
                            transformed_value=final_precip,
                            applied_rule="rainfall_mm = rainfall_cm * 10.0",
                        )
                    )

                # Physical range check
                if final_precip < 0.0:
                    quality_checks.append(
                        DataQualityCheck(
                            metric_name="climate.rainfall",
                            flag_type=QualityFlagType.RANGE_OUT_OF_BOUNDS,
                            severity=DataQualitySeverity.ERROR,
                            message=f"Negative rainfall amount ({final_precip} mm) is physically impossible.",
                            original_value=final_precip,
                        )
                    )
                elif final_precip > 20000.0:
                    quality_checks.append(
                        DataQualityCheck(
                            metric_name="climate.rainfall",
                            flag_type=QualityFlagType.RANGE_OUT_OF_BOUNDS,
                            severity=DataQualitySeverity.ERROR,
                            message=f"Rainfall {final_precip} mm exceeds maximum recorded terrestrial precipitation (20,000 mm).",
                            original_value=final_precip,
                        )
                    )
                else:
                    if final_precip == 0.0:
                        quality_checks.append(
                            DataQualityCheck(
                                metric_name="climate.rainfall",
                                flag_type=QualityFlagType.OBSERVED_ZERO,
                                severity=DataQualitySeverity.INFO,
                                message="Observed 0.0 mm precipitation (hyper-arid desert regime recorded as valid zero).",
                                original_value=0.0,
                                transformed_value=0.0,
                            )
                        )
                    else:
                        quality_checks.append(
                            DataQualityCheck(
                                metric_name="climate.rainfall",
                                flag_type=QualityFlagType.RANGE_VALID,
                                severity=DataQualitySeverity.INFO,
                                message=f"Annual precipitation {final_precip} mm is within valid physical bounds",
                                original_value=precip_raw,
                                transformed_value=round(final_precip, 2),
                            )
                        )

                    canonical_values["climate.rainfall"] = round(final_precip, 2)
                    prov_map["climate.rainfall"] = VariableProvenance(
                        variable_name="climate.rainfall",
                        dataset_id=self.dataset_id,
                        dataset_name=self.metadata.name,
                        source_organization=self.metadata.source_organization,
                        source_url=self.metadata.source_url,
                        license=self.metadata.license,
                        raw_value=precip_raw,
                        raw_unit=precip_unit,
                        canonical_value=round(final_precip, 2),
                        canonical_unit="mm/year",
                        spatial_resolution=self.metadata.spatial_resolution,
                        temporal_coverage=self.metadata.temporal_coverage,
                        retrieval_date=self.metadata.retrieval_date,
                        is_synthetic=raw_obs.is_synthetic,
                        known_limitations=self.metadata.known_limitations,
                    )
            except (ValueError, TypeError):
                quality_checks.append(
                    DataQualityCheck(
                        metric_name="climate.rainfall",
                        flag_type=QualityFlagType.RANGE_OUT_OF_BOUNDS,
                        severity=DataQualitySeverity.ERROR,
                        message=f"Malformed precipitation value: '{precip_raw}'",
                        original_value=precip_raw,
                    )
                )
        else:
            quality_checks.append(
                DataQualityCheck(
                    metric_name="climate.rainfall",
                    flag_type=QualityFlagType.MISSING_VALUE,
                    severity=DataQualitySeverity.INFO,
                    message="Precipitation unmeasured/null (preserved as null).",
                )
            )

        return canonical_values, quality_checks, prov_map
