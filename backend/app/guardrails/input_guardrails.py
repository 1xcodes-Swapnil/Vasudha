"""Input validation guardrails for raw and structured environmental parameters."""

from typing import Any, Dict, List, Optional, Tuple
from backend.app.schemas.environmental_state import EnvironmentalState
from backend.app.guardrails.models import (
    GuardrailAction,
    GuardrailResult,
    GuardrailSeverity,
)


class InputGuardrails:
    """Validates structured and unstructured input payloads against physical and biophysical boundaries."""

    # Recognized valid land-use and land-cover categories
    VALID_LAND_USES = {
        "cropland", "agriculture", "pasture", "grazing", "agroforestry",
        "forest", "degraded_forest", "plantation", "conservation", "protected_area",
        "wetland", "urban", "peri_urban", "industrial", "mining", "bare_land",
        "fallow", "rangeland", "shrubland"
    }

    VALID_LAND_COVERS = {
        "dense_forest", "open_forest", "broadleaf_forest", "coniferous_forest",
        "savanna", "grassland", "wetland", "mangrove", "peatland",
        "shrubland", "cropland", "bare_soil", "sand_dune", "urban_built", "water_body"
    }

    @classmethod
    def validate_raw_input_dict(cls, data: Dict[str, Any]) -> List[GuardrailResult]:
        """Validate arbitrary dictionary of input values before parsing."""
        results: List[GuardrailResult] = []

        # 1. Soil pH
        if "ph" in data and data["ph"] is not None:
            try:
                ph_val = float(data["ph"])
                if ph_val < 0.0 or ph_val > 14.0:
                    results.append(GuardrailResult(
                        passed=False,
                        severity=GuardrailSeverity.BLOCK,
                        code="INPUT_SOIL_PH_OUT_OF_BOUNDS",
                        message=f"Soil pH {ph_val} is physically impossible (must be 0.0–14.0).",
                        details={"field": "soil.ph", "value": ph_val},
                        action=GuardrailAction.BLOCK,
                    ))
                elif ph_val < 2.5 or ph_val > 10.5:
                    results.append(GuardrailResult(
                        passed=True,
                        severity=GuardrailSeverity.WARNING,
                        code="INPUT_SOIL_PH_EXTREME",
                        message=f"Soil pH {ph_val} is extreme for terrestrial vegetation (normal 3.5–9.0).",
                        details={"field": "soil.ph", "value": ph_val},
                        action=GuardrailAction.ALLOW_WITH_WARNING,
                    ))
            except (ValueError, TypeError):
                results.append(GuardrailResult(
                    passed=False,
                    severity=GuardrailSeverity.BLOCK,
                    code="INPUT_SOIL_PH_MALFORMED",
                    message="Soil pH must be a valid numerical value.",
                    details={"field": "soil.ph", "value": data["ph"]},
                    action=GuardrailAction.BLOCK,
                ))

        # 2. Soil Organic Carbon
        if "organic_carbon" in data and data["organic_carbon"] is not None:
            try:
                soc = float(data["organic_carbon"])
                if soc < 0.0:
                    results.append(GuardrailResult(
                        passed=False,
                        severity=GuardrailSeverity.BLOCK,
                        code="INPUT_SOC_NEGATIVE",
                        message=f"Soil organic carbon percentage cannot be negative ({soc}%).",
                        details={"field": "soil.organic_carbon", "value": soc},
                        action=GuardrailAction.BLOCK,
                    ))
                elif soc > 100.0:
                    results.append(GuardrailResult(
                        passed=False,
                        severity=GuardrailSeverity.BLOCK,
                        code="INPUT_SOC_EXCEEDS_100",
                        message=f"Soil organic carbon percentage cannot exceed 100% ({soc}%).",
                        details={"field": "soil.organic_carbon", "value": soc},
                        action=GuardrailAction.BLOCK,
                    ))
            except (ValueError, TypeError):
                results.append(GuardrailResult(
                    passed=False,
                    severity=GuardrailSeverity.BLOCK,
                    code="INPUT_SOC_MALFORMED",
                    message="Soil organic carbon must be a valid numerical percentage.",
                    details={"field": "soil.organic_carbon", "value": data["organic_carbon"]},
                    action=GuardrailAction.BLOCK,
                ))

        # 3. Soil Moisture
        if "moisture" in data and data["moisture"] is not None:
            try:
                moist = float(data["moisture"])
                if moist < 0.0 or moist > 100.0:
                    results.append(GuardrailResult(
                        passed=False,
                        severity=GuardrailSeverity.BLOCK,
                        code="INPUT_SOIL_MOISTURE_OUT_OF_BOUNDS",
                        message=f"Soil moisture must be between 0.0% and 100.0% (got {moist}%).",
                        details={"field": "soil.moisture", "value": moist},
                        action=GuardrailAction.BLOCK,
                    ))
            except (ValueError, TypeError):
                results.append(GuardrailResult(
                    passed=False,
                    severity=GuardrailSeverity.BLOCK,
                    code="INPUT_SOIL_MOISTURE_MALFORMED",
                    message="Soil moisture must be a valid numerical value.",
                    details={"field": "soil.moisture", "value": data["moisture"]},
                    action=GuardrailAction.BLOCK,
                ))

        # 4. Climate Rainfall
        if "rainfall" in data and data["rainfall"] is not None:
            try:
                rf = float(data["rainfall"])
                if rf < 0.0:
                    results.append(GuardrailResult(
                        passed=False,
                        severity=GuardrailSeverity.BLOCK,
                        code="INPUT_RAINFALL_NEGATIVE",
                        message=f"Annual precipitation cannot be negative ({rf} mm).",
                        details={"field": "climate.rainfall", "value": rf},
                        action=GuardrailAction.BLOCK,
                    ))
                elif rf > 20000.0:
                    results.append(GuardrailResult(
                        passed=False,
                        severity=GuardrailSeverity.BLOCK,
                        code="INPUT_RAINFALL_EXCEEDS_PHYSICAL_LIMIT",
                        message=f"Precipitation {rf} mm exceeds Earth's maximum terrestrial recorded rainfall (20,000 mm).",
                        details={"field": "climate.rainfall", "value": rf},
                        action=GuardrailAction.BLOCK,
                    ))
            except (ValueError, TypeError):
                results.append(GuardrailResult(
                    passed=False,
                    severity=GuardrailSeverity.BLOCK,
                    code="INPUT_RAINFALL_MALFORMED",
                    message="Rainfall must be a non-negative numerical value in millimeters.",
                    details={"field": "climate.rainfall", "value": data["rainfall"]},
                    action=GuardrailAction.BLOCK,
                ))

        # 5. Climate Temperature
        if "temperature" in data and data["temperature"] is not None:
            try:
                temp = float(data["temperature"])
                if temp < -90.0 or temp > 60.0:
                    results.append(GuardrailResult(
                        passed=False,
                        severity=GuardrailSeverity.BLOCK,
                        code="INPUT_TEMPERATURE_PHYSICALLY_IMPLAUSIBLE",
                        message=f"Temperature {temp}°C is outside recorded planetary terrestrial range (-90°C to 60°C).",
                        details={"field": "climate.temperature", "value": temp},
                        action=GuardrailAction.BLOCK,
                    ))
            except (ValueError, TypeError):
                results.append(GuardrailResult(
                    passed=False,
                    severity=GuardrailSeverity.BLOCK,
                    code="INPUT_TEMPERATURE_MALFORMED",
                    message="Temperature must be a numerical value in degrees Celsius.",
                    details={"field": "climate.temperature", "value": data["temperature"]},
                    action=GuardrailAction.BLOCK,
                ))

        # 6. Biodiversity Species Richness
        if "species_richness" in data and data["species_richness"] is not None:
            try:
                sr = int(data["species_richness"])
                if sr < 0:
                    results.append(GuardrailResult(
                        passed=False,
                        severity=GuardrailSeverity.BLOCK,
                        code="INPUT_SPECIES_RICHNESS_NEGATIVE",
                        message=f"Species richness cannot be negative ({sr}).",
                        details={"field": "biodiversity.species_richness", "value": sr},
                        action=GuardrailAction.BLOCK,
                    ))
            except (ValueError, TypeError):
                results.append(GuardrailResult(
                    passed=False,
                    severity=GuardrailSeverity.BLOCK,
                    code="INPUT_SPECIES_RICHNESS_MALFORMED",
                    message="Species richness must be an integer count.",
                    details={"field": "biodiversity.species_richness", "value": data["species_richness"]},
                    action=GuardrailAction.BLOCK,
                ))

        # 7. Coordinates
        if "latitude" in data and data["latitude"] is not None:
            try:
                lat = float(data["latitude"])
                if lat < -90.0 or lat > 90.0:
                    results.append(GuardrailResult(
                        passed=False,
                        severity=GuardrailSeverity.BLOCK,
                        code="INPUT_LATITUDE_OUT_OF_BOUNDS",
                        message=f"Latitude {lat} is invalid (must be between -90.0 and +90.0).",
                        details={"field": "spatial.latitude", "value": lat},
                        action=GuardrailAction.BLOCK,
                    ))
            except (ValueError, TypeError):
                results.append(GuardrailResult(
                    passed=False,
                    severity=GuardrailSeverity.BLOCK,
                    code="INPUT_LATITUDE_MALFORMED",
                    message="Latitude must be a valid float.",
                    details={"field": "spatial.latitude", "value": data["latitude"]},
                    action=GuardrailAction.BLOCK,
                ))

        if "longitude" in data and data["longitude"] is not None:
            try:
                lon = float(data["longitude"])
                if lon < -180.0 or lon > 180.0:
                    results.append(GuardrailResult(
                        passed=False,
                        severity=GuardrailSeverity.BLOCK,
                        code="INPUT_LONGITUDE_OUT_OF_BOUNDS",
                        message=f"Longitude {lon} is invalid (must be between -180.0 and +180.0).",
                        details={"field": "spatial.longitude", "value": lon},
                        action=GuardrailAction.BLOCK,
                    ))
            except (ValueError, TypeError):
                results.append(GuardrailResult(
                    passed=False,
                    severity=GuardrailSeverity.BLOCK,
                    code="INPUT_LONGITUDE_MALFORMED",
                    message="Longitude must be a valid float.",
                    details={"field": "spatial.longitude", "value": data["longitude"]},
                    action=GuardrailAction.BLOCK,
                ))

        return results

    @classmethod
    def validate_canonical_state(cls, state: EnvironmentalState) -> List[GuardrailResult]:
        """Validate an already instantiated EnvironmentalState."""
        results: List[GuardrailResult] = []

        # Check unknown vs zero semantics: ensure None is preserved and not converted to 0
        state_dict = state.model_dump()
        for domain, metrics in state_dict.items():
            if isinstance(metrics, dict):
                for metric_name, val in metrics.items():
                    # If value is 0.0, ensure it is an explicit 0 and documented
                    if val == 0.0 or val == 0:
                        results.append(GuardrailResult(
                            passed=True,
                            severity=GuardrailSeverity.INFO,
                            code=f"INPUT_OBSERVED_ZERO_{domain.upper()}_{metric_name.upper()}",
                            message=f"Metric {domain}.{metric_name} is an observed zero (distinct from unknown/null).",
                            details={"metric": f"{domain}.{metric_name}", "value": 0},
                            action=GuardrailAction.ALLOW,
                        ))

        return results

    @classmethod
    def detect_observation_conflicts(
        cls,
        source_a_name: str,
        source_a_values: Dict[str, Any],
        source_b_name: str,
        source_b_values: Dict[str, Any],
        threshold_percentage: float = 0.35,
    ) -> List[GuardrailResult]:
        """Compare two sources of observations (e.g., user input vs satellite/SoilGrids dataset)."""
        results: List[GuardrailResult] = []

        common_keys = set(source_a_values.keys()).intersection(set(source_b_values.keys()))
        for key in common_keys:
            val_a = source_a_values.get(key)
            val_b = source_b_values.get(key)
            if val_a is not None and val_b is not None:
                if isinstance(val_a, (int, float)) and isinstance(val_b, (int, float)):
                    if max(abs(val_a), abs(val_b)) > 0:
                        diff = abs(val_a - val_b) / max(abs(val_a), abs(val_b))
                        if diff > threshold_percentage:
                            results.append(GuardrailResult(
                                passed=False,
                                severity=GuardrailSeverity.WARNING,
                                code="INPUT_OBSERVATION_CONFLICT",
                                message=(
                                    f"Conflict detected for '{key}': {source_a_name} reports {val_a}, "
                                    f"while {source_b_name} reports {val_b} (discrepancy {diff*100:.1f}%)."
                                ),
                                details={
                                    "variable": key,
                                    "source_a": {"name": source_a_name, "value": val_a},
                                    "source_b": {"name": source_b_name, "value": val_b},
                                    "relative_difference": round(diff, 4),
                                },
                                action=GuardrailAction.REQUEST_CLARIFICATION if diff > 0.60 else GuardrailAction.ALLOW_WITH_WARNING,
                            ))
                elif isinstance(val_a, str) and isinstance(val_b, str):
                    if val_a.strip().lower() != val_b.strip().lower():
                        results.append(GuardrailResult(
                            passed=False,
                            severity=GuardrailSeverity.WARNING,
                            code="INPUT_CATEGORICAL_CONFLICT",
                            message=(
                                f"Categorical mismatch for '{key}': {source_a_name} reports '{val_a}', "
                                f"while {source_b_name} reports '{val_b}'."
                            ),
                            details={
                                "variable": key,
                                "source_a": {"name": source_a_name, "value": val_a},
                                "source_b": {"name": source_b_name, "value": val_b},
                            },
                            action=GuardrailAction.ALLOW_WITH_WARNING,
                        ))

        return results
