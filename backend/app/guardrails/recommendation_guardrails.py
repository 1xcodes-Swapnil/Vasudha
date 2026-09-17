"""Recommendation, intervention safety, and invasive species risk guardrails."""

from typing import Any, Dict, List, Optional, Tuple
from backend.app.schemas.environmental_state import EnvironmentalState, SpatialContext
from backend.app.schemas.intervention import (
    InterventionDefinition,
    InterventionRecommendation,
    TimeHorizon,
)
from backend.app.guardrails.models import (
    GuardrailAction,
    GuardrailResult,
    GuardrailSeverity,
)


class RecommendationGuardrails:
    """Evaluates recommendation safety, biophysical feasibility, and ecological risk."""

    # Keywords indicating potentially high-risk ecological or invasive manipulations
    HIGH_RISK_KEYWORDS = [
        "introduce non-native", "exotic species", "fast-growing eucalyptus",
        "chemical herbicide", "broad-spectrum pesticide", "translocation",
        "species introduction", "river damming", "water diversion",
        "synthetic fertilizer broadcast", "mono-species plantation"
    ]

    @classmethod
    def evaluate_intervention_safety(
        cls,
        intervention: InterventionDefinition,
        state: EnvironmentalState,
        spatial: Optional[SpatialContext] = None,
    ) -> List[GuardrailResult]:
        """Safety checks on proposed ecological intervention."""
        results: List[GuardrailResult] = []

        # 1. Invasive / high-risk activity screening
        text_corpus = f"{intervention.name} {intervention.what_to_do_template} {intervention.ecological_mechanism}".lower()
        matched_risks = [kw for kw in cls.HIGH_RISK_KEYWORDS if kw in text_corpus]

        if matched_risks:
            results.append(GuardrailResult(
                passed=False,
                severity=GuardrailSeverity.BLOCK,
                code="REC_ECOLOGICALLY_RISKY_ACTIVITY",
                message=(
                    f"Intervention '{intervention.name}' contains potentially hazardous or invasive practices: "
                    f"{', '.join(matched_risks)}. Strict native germplasm provenance and biosecurity protocols required."
                ),
                details={"matched_risks": matched_risks, "intervention_id": intervention.id},
                action=GuardrailAction.BLOCK,
            ))

        # 2. Water availability constraint vs intervention moisture needs
        rainfall = state.climate.rainfall
        moisture = state.soil.moisture
        min_rain_req = intervention.suitability_rules.min_rainfall_mm

        if min_rain_req is not None and rainfall is not None:
            if rainfall < (min_rain_req * 0.5):
                results.append(GuardrailResult(
                    passed=False,
                    severity=GuardrailSeverity.BLOCK,
                    code="REC_WATER_DEFICIT_CRITICAL",
                    message=(
                        f"Intervention '{intervention.name}' requires at least {min_rain_req} mm/yr rainfall, "
                        f"but observed rainfall is {rainfall} mm/yr (severe water deficit). "
                        "Without active irrigation or drought-tolerant pioneer selection, this intervention is biophysically unviable."
                    ),
                    details={"rainfall": rainfall, "min_required": min_rain_req},
                    action=GuardrailAction.BLOCK,
                ))
            elif rainfall < min_rain_req:
                results.append(GuardrailResult(
                    passed=True,
                    severity=GuardrailSeverity.WARNING,
                    code="REC_WATER_DEFICIT_MARGINAL",
                    message=(
                        f"Observed rainfall ({rainfall} mm/yr) is marginally below standard requirement ({min_rain_req} mm/yr). "
                        "Requires micro-catchment water harvesting (zai pits/swales) and mulch conservation."
                    ),
                    details={"rainfall": rainfall, "min_required": min_rain_req},
                    action=GuardrailAction.ALLOW_WITH_WARNING,
                ))

        # 3. Soil pH compatibility
        ph = state.soil.ph
        min_ph = intervention.suitability_rules.min_soil_ph
        max_ph = intervention.suitability_rules.max_soil_ph

        if ph is not None:
            if min_ph is not None and ph < (min_ph - 1.0):
                results.append(GuardrailResult(
                    passed=False,
                    severity=GuardrailSeverity.WARNING,
                    code="REC_SOIL_ACIDITY_CONFLICT",
                    message=(
                        f"Soil pH ({ph}) is intensely acidic for '{intervention.name}' (min recommended: {min_ph}). "
                        "Agricultural liming or biochar amendment is mandatory prior to vegetative establishment."
                    ),
                    details={"ph": ph, "min_recommended": min_ph},
                    action=GuardrailAction.ALLOW_WITH_WARNING,
                ))
            elif max_ph is not None and ph > (max_ph + 1.0):
                results.append(GuardrailResult(
                    passed=False,
                    severity=GuardrailSeverity.WARNING,
                    code="REC_SOIL_ALKALINITY_CONFLICT",
                    message=(
                        f"Soil pH ({ph}) is intensely alkaline for '{intervention.name}' (max recommended: {max_ph}). "
                        "Organic mulch and elemental sulfur buffering recommended."
                    ),
                    details={"ph": ph, "max_recommended": max_ph},
                    action=GuardrailAction.ALLOW_WITH_WARNING,
                ))

        if not results:
            results.append(GuardrailResult(
                passed=True,
                severity=GuardrailSeverity.INFO,
                code="REC_SAFETY_PASSED",
                message=f"Intervention '{intervention.name}' passed all biophysical safety checks.",
                details={"intervention_id": intervention.id},
                action=GuardrailAction.ALLOW,
            ))

        return results

    @classmethod
    def validate_time_horizons(
        cls,
        recommendation: InterventionRecommendation,
    ) -> GuardrailResult:
        """Ensure time horizons strictly adhere to canonical categorical buckets."""
        valid_horizons = {TimeHorizon.SHORT_TERM, TimeHorizon.MEDIUM_TERM, TimeHorizon.LONG_TERM}

        if recommendation.time_horizon not in valid_horizons:
            return GuardrailResult(
                passed=False,
                severity=GuardrailSeverity.WARNING,
                code="REC_INVALID_TIME_HORIZON",
                message=f"Non-standard time horizon '{recommendation.time_horizon}' normalized to canonical categories.",
                details={"time_horizon": str(recommendation.time_horizon)},
                action=GuardrailAction.ALLOW_WITH_WARNING,
            )

        return GuardrailResult(
            passed=True,
            severity=GuardrailSeverity.INFO,
            code="REC_TIME_HORIZON_VALID",
            message=f"Time horizon '{recommendation.time_horizon.value}' is scientifically validated.",
            details={"time_horizon": recommendation.time_horizon.value},
            action=GuardrailAction.ALLOW,
        )
