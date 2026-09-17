"""Ecological plausibility, multi-metric reasoning, and temporal freshness guardrails."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.app.schemas.environmental_state import EnvironmentalState
from backend.app.guardrails.models import (
    GuardrailAction,
    GuardrailResult,
    GuardrailSeverity,
)


class EnvironmentalGuardrails:
    """Validates ecological plausibility, variable co-occurrences, and data freshness."""

    @classmethod
    def evaluate_multi_metric_sufficiency(
        cls,
        state: EnvironmentalState,
        intent: str = "biodiversity_recommendation",
    ) -> GuardrailResult:
        """Verify that substantive ecological reasoning is backed by at least 3 environmental variables."""
        known_metrics: List[str] = []

        if state.soil.ph is not None:
            known_metrics.append("soil.ph")
        if state.soil.organic_carbon is not None:
            known_metrics.append("soil.organic_carbon")
        if state.soil.moisture is not None:
            known_metrics.append("soil.moisture")
        if state.climate.rainfall is not None:
            known_metrics.append("climate.rainfall")
        if state.climate.temperature is not None:
            known_metrics.append("climate.temperature")
        if state.land.land_use is not None:
            known_metrics.append("land.land_use")
        if state.land.land_cover is not None:
            known_metrics.append("land.land_cover")
        if state.biodiversity.species_richness is not None:
            known_metrics.append("biodiversity.species_richness")
        if state.biodiversity.habitat_diversity is not None:
            known_metrics.append("biodiversity.habitat_diversity")
        if state.human_impact.pollution is not None:
            known_metrics.append("human_impact.pollution")
        if state.human_impact.deforestation is not None:
            known_metrics.append("human_impact.deforestation")

        metric_count = len(known_metrics)

        if metric_count < 3:
            missing_suggestions = []
            if state.land.land_use is None:
                missing_suggestions.append("land use (e.g. cropland, pasture, forest)")
            if state.climate.rainfall is None:
                missing_suggestions.append("annual rainfall or moisture regime (mm/year)")
            if state.soil.organic_carbon is None and state.soil.ph is None:
                missing_suggestions.append("soil parameters (such as pH or organic carbon %)")
            if state.biodiversity.habitat_diversity is None and state.biodiversity.species_richness is None:
                missing_suggestions.append("baseline biodiversity or habitat status")

            clarification_msg = (
                f"Only {metric_count} environmental variable(s) provided ({', '.join(known_metrics) if known_metrics else 'none'}). "
                f"Substantive biodiversity reasoning requires at least 3 variables to avoid generic, ungrounded advice. "
                f"Please specify your {', '.join(missing_suggestions[:3])}."
            )

            return GuardrailResult(
                passed=False,
                severity=GuardrailSeverity.WARNING,
                code="ENV_INSUFFICIENT_MULTI_METRIC_DATA",
                message=clarification_msg,
                details={
                    "known_metrics_count": metric_count,
                    "known_metrics": known_metrics,
                    "required_minimum": 3,
                    "suggested_additions": missing_suggestions,
                },
                action=GuardrailAction.REQUEST_CLARIFICATION,
            )

        return GuardrailResult(
            passed=True,
            severity=GuardrailSeverity.INFO,
            code="ENV_MULTI_METRIC_SUFFICIENT",
            message=f"Sufficient multi-metric baseline established ({metric_count} environmental variables available).",
            details={"known_metrics_count": metric_count, "known_metrics": known_metrics},
            action=GuardrailAction.ALLOW,
        )

    @classmethod
    def check_ecological_plausibility(cls, state: EnvironmentalState) -> List[GuardrailResult]:
        """Check for biophysical contradictions or impossible environmental co-occurrences."""
        results: List[GuardrailResult] = []

        # 1. High precipitation (>2000 mm) but desiccated soil moisture (< 5%) without sandy/desert context
        if state.climate.rainfall is not None and state.soil.moisture is not None:
            if state.climate.rainfall > 2000.0 and state.soil.moisture < 5.0:
                results.append(GuardrailResult(
                    passed=False,
                    severity=GuardrailSeverity.WARNING,
                    code="ENV_PLAUSIBILITY_RAIN_MOISTURE_MISMATCH",
                    message=(
                        f"Plausibility conflict: Extremely high rainfall ({state.climate.rainfall} mm/yr) "
                        f"paired with desiccated soil moisture ({state.soil.moisture}%). "
                        "May indicate hyper-draining sand, steep runoff, or measurement timing discrepancy."
                    ),
                    details={"rainfall": state.climate.rainfall, "moisture": state.soil.moisture},
                    action=GuardrailAction.ALLOW_WITH_WARNING,
                ))

        # 2. Mangrove / wetland ecosystem with arid rainfall (< 150 mm) and no water body cover
        eco = state.spatial_context.ecosystem.lower() if state.spatial_context and state.spatial_context.ecosystem else ""
        if "mangrove" in eco or "wetland" in eco or "peatland" in eco:
            if state.climate.rainfall is not None and state.climate.rainfall < 150.0:
                if state.soil.moisture is not None and state.soil.moisture < 15.0:
                    results.append(GuardrailResult(
                        passed=False,
                        severity=GuardrailSeverity.WARNING,
                        code="ENV_PLAUSIBILITY_WETLAND_ARID_MISMATCH",
                        message=(
                            f"Ecosystem is classified as '{eco}' but rainfall is semi-arid ({state.climate.rainfall} mm) "
                            f"and soil moisture is low ({state.soil.moisture}%)."
                        ),
                        details={"ecosystem": eco, "rainfall": state.climate.rainfall},
                        action=GuardrailAction.ALLOW_WITH_WARNING,
                    ))

        # 3. Dense forest cover with 0 recorded species richness
        if state.land.land_cover and "forest" in state.land.land_cover.lower():
            if state.biodiversity.species_richness == 0:
                results.append(GuardrailResult(
                    passed=False,
                    severity=GuardrailSeverity.WARNING,
                    code="ENV_PLAUSIBILITY_FOREST_ZERO_SPECIES",
                    message="Forest land cover is reported with observed 0 species richness. Please confirm if this is true monoculture or unmeasured sampling.",
                    details={"land_cover": state.land.land_cover, "species_richness": 0},
                    action=GuardrailAction.ALLOW_WITH_WARNING,
                ))

        return results

    @classmethod
    def evaluate_temporal_freshness(
        cls,
        observation_timestamps: Dict[str, str],
        max_freshness_years: float = 3.0,
    ) -> List[GuardrailResult]:
        """Evaluate observation dates to distinguish current from historical/stale records."""
        results: List[GuardrailResult] = []
        now = datetime.now(timezone.utc)

        for metric_name, ts_str in observation_timestamps.items():
            try:
                # Parse ISO timestamp
                obs_time = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                age_days = (now - obs_time).days
                age_years = age_days / 365.25

                if age_years > max_freshness_years:
                    results.append(GuardrailResult(
                        passed=True,
                        severity=GuardrailSeverity.WARNING,
                        code="ENV_TEMPORAL_OBSERVATION_STALE",
                        message=(
                            f"Observation for '{metric_name}' is {age_years:.1f} years old ({ts_str[:10]}). "
                            "Treating as historical baseline rather than current condition."
                        ),
                        details={"metric": metric_name, "age_years": round(age_years, 2), "recorded_at": ts_str},
                        action=GuardrailAction.ALLOW_WITH_WARNING,
                    ))
            except Exception:
                continue

        return results
