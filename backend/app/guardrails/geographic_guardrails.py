"""Geographic and ecosystem transferability guardrails."""

from typing import Any, Dict, List, Optional, Tuple
from backend.app.schemas.environmental_state import SpatialContext
from backend.app.guardrails.models import (
    GeographicRelevanceGrade,
    GuardrailAction,
    GuardrailResult,
    GuardrailSeverity,
)


class GeographicGuardrails:
    """Evaluates spatial relevance and prevents ungrounded cross-ecosystem extrapolation."""

    @classmethod
    def evaluate_spatial_transferability(
        cls,
        user_spatial: Optional[SpatialContext],
        target_ecosystem: Optional[str],
        evidence_geographic_scope: Optional[str] = None,
    ) -> Tuple[GeographicRelevanceGrade, GuardrailResult]:
        """Grade geographic alignment between site context and scientific evidence/intervention scope."""
        if not user_spatial or not user_spatial.ecosystem:
            return GeographicRelevanceGrade.MEDIUM, GuardrailResult(
                passed=True,
                severity=GuardrailSeverity.INFO,
                code="GEO_CONTEXT_UNSPECIFIED",
                message="Specific site ecosystem is unspecified; evaluating using generalized regional biome models.",
                details={"target_ecosystem": target_ecosystem, "evidence_scope": evidence_geographic_scope},
                action=GuardrailAction.ALLOW,
            )

        user_eco = user_spatial.ecosystem.lower()
        target_eco = (target_ecosystem or "").lower()
        evidence_scope = (evidence_geographic_scope or "").lower()

        # Check for direct or strong match
        if (target_eco and target_eco in user_eco) or (target_eco and user_eco in target_eco):
            return GeographicRelevanceGrade.HIGH, GuardrailResult(
                passed=True,
                severity=GuardrailSeverity.INFO,
                code="GEO_ECOSYSTEM_STRONG_MATCH",
                message=f"High spatial transferability: Site ecosystem '{user_spatial.ecosystem}' matches target '{target_ecosystem}'.",
                details={"user_ecosystem": user_spatial.ecosystem, "target_ecosystem": target_ecosystem},
                action=GuardrailAction.ALLOW,
            )

        # Check for major biome conflict (e.g. Boreal/Tundra vs Tropical Rainforest)
        tropical_tokens = ["tropical", "rainforest", "equatorial", "mangrove", "humid tropics"]
        arid_tokens = ["arid", "desert", "semi-arid", "steppe", "chaparral"]
        boreal_tokens = ["boreal", "taiga", "tundra", "arctic", "subarctic"]

        is_user_tropical = any(t in user_eco for t in tropical_tokens)
        is_user_arid = any(t in user_eco for t in arid_tokens)
        is_user_boreal = any(t in user_eco for t in boreal_tokens)

        is_target_tropical = any(t in target_eco for t in tropical_tokens)
        is_target_arid = any(t in target_eco for t in arid_tokens)
        is_target_boreal = any(t in target_eco for t in boreal_tokens)

        mismatch = (
            (is_user_tropical and (is_target_boreal or is_target_arid)) or
            (is_user_boreal and (is_target_tropical or is_target_arid)) or
            (is_user_arid and (is_target_tropical or is_target_boreal))
        )

        if mismatch:
            return GeographicRelevanceGrade.LOW_MISMATCH, GuardrailResult(
                passed=False,
                severity=GuardrailSeverity.WARNING,
                code="GEO_ECOSYSTEM_MAJOR_MISMATCH",
                message=(
                    f"Geographic mismatch: Site ecosystem '{user_spatial.ecosystem}' differs significantly "
                    f"from evidence/intervention context '{target_ecosystem or evidence_geographic_scope}'. "
                    "Confidence is downgraded; local field trials and native provenance adaptation required."
                ),
                details={
                    "user_ecosystem": user_spatial.ecosystem,
                    "target_ecosystem": target_ecosystem,
                    "evidence_scope": evidence_geographic_scope,
                },
                action=GuardrailAction.ALLOW_WITH_WARNING,
            )

        return GeographicRelevanceGrade.MEDIUM, GuardrailResult(
            passed=True,
            severity=GuardrailSeverity.INFO,
            code="GEO_ECOSYSTEM_MODERATE_TRANSFERABILITY",
            message="Moderate spatial transferability across compatible temperate/transitional biomes.",
            details={"user_ecosystem": user_spatial.ecosystem, "target_ecosystem": target_ecosystem},
            action=GuardrailAction.ALLOW,
        )
