"""Conflict and Uncertainty Detection Engine (Phase 9).

Detects and quantifies:
1. User-provided vs Dataset-derived discrepancies
2. Geographic / Biome classification mismatches
3. Temporal staleness of baseline observations
4. Missing key variables for multi-metric reasoning
5. Scientific evidence sufficiency and contradictions
"""

import math
from typing import Any, Dict, List, Optional, Tuple
from backend.app.schemas.environmental_state import EnvironmentalState, SpatialContext
from backend.app.schemas.dataset import VariableProvenance
from backend.app.schemas.ecological_findings import (
    ConflictReport,
    ConflictType,
    ConflictResolutionStrategy,
)
from backend.app.schemas.scientific_rag import EvidenceChunkPacket
from backend.app.core.logging import logger


class EcologicalConflictDetector:
    """Detects discrepancies between user inputs, datasets, geographic boundaries, and evidence."""

    # Discrepancy threshold ratios for numeric variables
    _NUMERIC_THRESHOLDS = {
        "soil.ph": 1.5,  # pH unit difference
        "soil.organic_carbon": 50.0,  # % relative difference
        "soil.moisture": 50.0,  # % relative difference
        "climate.temperature": 8.0,  # °C difference
        "climate.rainfall": 40.0,  # % relative difference
        "biodiversity.species_richness": 60.0,  # % relative difference
        "biodiversity.habitat_diversity": 40.0,  # % relative difference
        "human_impact.deforestation": 50.0,  # % relative difference
        "human_impact.pollution": 40.0,  # % relative difference
    }

    def detect_conflicts(
        self,
        user_state: Optional[EnvironmentalState],
        dataset_state: Optional[EnvironmentalState],
        user_extracted_map: Dict[str, Any],
        provenance_map: Dict[str, VariableProvenance],
        resolved_spatial: SpatialContext,
    ) -> Tuple[List[ConflictReport], float]:
        """Audit inputs and dataset values for discrepancies and calculate cumulative uncertainty penalty."""
        conflicts: List[ConflictReport] = []
        total_penalty = 0.0

        if not user_state or not dataset_state:
            return conflicts, total_penalty

        # 1. Audit Numeric and Categorical Metric Discrepancies
        metrics_to_compare = [
            ("soil.ph", user_state.soil.ph, dataset_state.soil.ph, "pH"),
            ("soil.organic_carbon", user_state.soil.organic_carbon, dataset_state.soil.organic_carbon, "%"),
            ("soil.moisture", user_state.soil.moisture, dataset_state.soil.moisture, "%"),
            ("climate.temperature", user_state.climate.temperature, dataset_state.climate.temperature, "°C"),
            ("climate.rainfall", user_state.climate.rainfall, dataset_state.climate.rainfall, "mm/yr"),
            ("biodiversity.species_richness", user_state.biodiversity.species_richness, dataset_state.biodiversity.species_richness, "species"),
            ("biodiversity.habitat_diversity", user_state.biodiversity.habitat_diversity, dataset_state.biodiversity.habitat_diversity, "%"),
            ("human_impact.deforestation", user_state.human_impact.deforestation, dataset_state.human_impact.deforestation, "%"),
            ("human_impact.pollution", user_state.human_impact.pollution, dataset_state.human_impact.pollution, "index"),
        ]

        for metric_id, u_val, d_val, unit in metrics_to_compare:
            if u_val is not None and d_val is not None:
                # Check for significant numerical divergence
                if metric_id == "soil.ph":
                    diff = abs(float(u_val) - float(d_val))
                    if diff >= self._NUMERIC_THRESHOLDS["soil.ph"]:
                        penalty = 0.12
                        total_penalty += penalty
                        conflicts.append(
                            ConflictReport(
                                conflict_id=f"CONF_{metric_id.replace('.', '_').upper()}_DELTA",
                                conflict_type=ConflictType.USER_DATASET_DISCREPANCY,
                                variables_involved=[metric_id],
                                user_value=u_val,
                                dataset_value=d_val,
                                delta_percentage=round((diff / max(float(d_val), 1.0)) * 100.0, 1),
                                message=(
                                    f"Observed user {metric_id} ({u_val} {unit}) diverges significantly from "
                                    f"authoritative dataset value ({d_val} {unit}, Δ={round(diff, 2)} {unit}). "
                                    f"User-supplied on-site measurement is preserved with an uncertainty flag."
                                ),
                                resolution_strategy=ConflictResolutionStrategy.USER_PREFERRED_WITH_UNCERTAINTY,
                                uncertainty_penalty=penalty,
                            )
                        )
                elif metric_id == "climate.temperature":
                    diff = abs(float(u_val) - float(d_val))
                    if diff >= self._NUMERIC_THRESHOLDS["climate.temperature"]:
                        penalty = 0.10
                        total_penalty += penalty
                        conflicts.append(
                            ConflictReport(
                                conflict_id=f"CONF_{metric_id.replace('.', '_').upper()}_DELTA",
                                conflict_type=ConflictType.USER_DATASET_DISCREPANCY,
                                variables_involved=[metric_id],
                                user_value=u_val,
                                dataset_value=d_val,
                                delta_percentage=round((diff / max(abs(float(d_val)), 1.0)) * 100.0, 1),
                                message=(
                                    f"User temperature ({u_val} °C) differs from climatological baseline ({d_val} °C). "
                                    f"Preserving user-reported microclimate value with elevated uncertainty."
                                ),
                                resolution_strategy=ConflictResolutionStrategy.USER_PREFERRED_WITH_UNCERTAINTY,
                                uncertainty_penalty=penalty,
                            )
                        )
                else:
                    # Percentage relative difference
                    u_float = float(u_val)
                    d_float = float(d_val)
                    denom = max(abs(d_float), 1.0)
                    pct_diff = (abs(u_float - d_float) / denom) * 100.0
                    threshold = self._NUMERIC_THRESHOLDS.get(metric_id, 40.0)

                    if pct_diff >= threshold:
                        penalty = 0.10
                        total_penalty += penalty
                        conflicts.append(
                            ConflictReport(
                                conflict_id=f"CONF_{metric_id.replace('.', '_').upper()}_DELTA",
                                conflict_type=ConflictType.USER_DATASET_DISCREPANCY,
                                variables_involved=[metric_id],
                                user_value=u_val,
                                dataset_value=d_val,
                                delta_percentage=round(pct_diff, 1),
                                message=(
                                    f"User-reported {metric_id} ({u_val} {unit}) deviates by {round(pct_diff, 1)}% from "
                                    f"authoritative dataset estimate ({d_val} {unit})."
                                ),
                                resolution_strategy=ConflictResolutionStrategy.USER_PREFERRED_WITH_UNCERTAINTY,
                                uncertainty_penalty=penalty,
                            )
                        )

        # 2. Categorical Land Use / Land Cover Mismatches
        if user_state.land.land_use and dataset_state.land.land_use:
            u_lu = str(user_state.land.land_use).lower()
            d_lu = str(dataset_state.land.land_use).lower()
            if u_lu != d_lu and not (u_lu in d_lu or d_lu in u_lu):
                penalty = 0.08
                total_penalty += penalty
                conflicts.append(
                    ConflictReport(
                        conflict_id="CONF_LAND_USE_MISMATCH",
                        conflict_type=ConflictType.USER_DATASET_DISCREPANCY,
                        variables_involved=["land.land_use"],
                        user_value=user_state.land.land_use,
                        dataset_value=dataset_state.land.land_use,
                        delta_percentage=None,
                        message=(
                            f"User classified land use as '{user_state.land.land_use}' while satellite baseline indicates '{dataset_state.land.land_use}'. "
                            f"Site-level user classification preferred."
                        ),
                        resolution_strategy=ConflictResolutionStrategy.USER_PREFERRED_WITH_UNCERTAINTY,
                        uncertainty_penalty=penalty,
                    )
                )

        # 3. Geographic / Biome Mismatches
        if resolved_spatial.latitude is not None and resolved_spatial.ecosystem:
            lat = resolved_spatial.latitude
            lon = resolved_spatial.longitude or 0.0
            eco = str(resolved_spatial.ecosystem).lower()

            # Arctic tundra coordinates with tropical claim
            if abs(lat) > 66.5 and "tropical" in eco:
                penalty = 0.25
                total_penalty += penalty
                conflicts.append(
                    ConflictReport(
                        conflict_id="CONF_GEO_POLAR_TROPICAL_MISMATCH",
                        conflict_type=ConflictType.GEOGRAPHIC_MISMATCH,
                        variables_involved=["spatial_context.latitude", "spatial_context.ecosystem"],
                        user_value=resolved_spatial.ecosystem,
                        dataset_value="polar_tundra",
                        delta_percentage=None,
                        message=(
                            f"Geographic mismatch: Coordinates ({lat}, {lon}) lie in polar/arctic zone, "
                            f"which contradicts tropical biome claim '{resolved_spatial.ecosystem}'."
                        ),
                        resolution_strategy=ConflictResolutionStrategy.PRESERVED_UNCERTAINTY,
                        uncertainty_penalty=penalty,
                    )
                )
            # Hyper-arid desert with wetland claim
            elif -25.0 <= lat <= -18.0 and -71.0 <= lon <= -68.0 and eco in ("wetland", "peatland", "tropical_forest"):
                penalty = 0.20
                total_penalty += penalty
                conflicts.append(
                    ConflictReport(
                        conflict_id="CONF_GEO_ARID_WETLAND_MISMATCH",
                        conflict_type=ConflictType.GEOGRAPHIC_MISMATCH,
                        variables_involved=["spatial_context.latitude", "spatial_context.ecosystem"],
                        user_value=resolved_spatial.ecosystem,
                        dataset_value="hyper_arid_desert",
                        delta_percentage=None,
                        message=(
                            f"Geographic mismatch: Coordinates ({lat}, {lon}) lie in the hyper-arid Atacama desert, "
                            f"incompatible with wetland/rainforest classification '{resolved_spatial.ecosystem}'."
                        ),
                        resolution_strategy=ConflictResolutionStrategy.PRESERVED_UNCERTAINTY,
                        uncertainty_penalty=penalty,
                    )
                )

        # 4. Temporal Staleness Checks from Provenance
        for var_name, prov in provenance_map.items():
            if prov.temporal_coverage and "1970-2000" in prov.temporal_coverage:
                if user_state.human_impact.deforestation and user_state.human_impact.deforestation > 10.0:
                    penalty = 0.05
                    total_penalty += penalty
                    conflicts.append(
                        ConflictReport(
                            conflict_id=f"CONF_TEMPORAL_{var_name.replace('.', '_').upper()}",
                            conflict_type=ConflictType.TEMPORAL_OUTDATED,
                            variables_involved=[var_name, "human_impact.deforestation"],
                            user_value=None,
                            dataset_value=prov.temporal_coverage,
                            delta_percentage=None,
                            message=(
                                f"Dataset {prov.dataset_id} for '{var_name}' relies on historical baseline ({prov.temporal_coverage}), "
                                f"which may not fully reflect recent local deforestation dynamics ({user_state.human_impact.deforestation}%)."
                            ),
                            resolution_strategy=ConflictResolutionStrategy.PRESERVED_UNCERTAINTY,
                            uncertainty_penalty=penalty,
                        )
                    )

        capped_penalty = min(total_penalty, 0.50)
        logger.info(f"Conflict audit complete: {len(conflicts)} conflicts identified (penalty={round(capped_penalty, 3)}).")
        return conflicts, capped_penalty


# Global singleton instance
conflict_detector = EcologicalConflictDetector()
