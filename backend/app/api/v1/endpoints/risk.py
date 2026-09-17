"""FastAPI router for Nature Risk Profile diagnostics (Phase 6)."""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from backend.app.core.logging import logger
from backend.app.knowledge.risk_engine import (
    NatureRiskProfileEngine,
    get_risk_engine,
)
from backend.app.schemas.environmental_state import EnvironmentalState
from backend.app.schemas.risk_profile import (
    NatureRiskProfile,
    RiskDimension,
    RiskLevel,
)

router = APIRouter()


@router.post(
    "/profile",
    response_model=NatureRiskProfile,
    status_code=status.HTTP_200_OK,
    summary="Diagnose Nature Risk Profile from Environmental State",
    description=(
        "Evaluates the 5 key ecological risk dimensions (water stress, habitat pressure, "
        "biodiversity pressure, climate exposure, human disturbance) using deterministic forward "
        "rules and two-stage scientific RAG. Strictly eliminates arbitrary numerical scores."
    ),
)
async def evaluate_nature_risk_profile(
    state: EnvironmentalState,
    engine: NatureRiskProfileEngine = Depends(get_risk_engine),
) -> NatureRiskProfile:
    """Diagnoses Nature Risk Profile across 5 dimensions with evidence and explainability chains."""
    try:
        profile = engine.diagnose_risk_profile(state)
        return profile
    except Exception as e:
        logger.error(f"Failed to generate Nature Risk Profile: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Nature risk profile diagnostic failed: {str(e)}",
        )


@router.get(
    "/dimensions",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="List Supported Risk Dimensions and Methodology",
    description="Returns definitions, evaluated variables, and biophysical rationale for all 5 risk dimensions.",
)
async def list_risk_dimensions() -> List[Dict[str, Any]]:
    """Returns methodology details for the 5 nature risk dimensions."""
    return [
        {
            "dimension_id": "water_stress",
            "name": "Hydrologic & Soil Water Stress",
            "evaluates": ["climate.rainfall", "soil.moisture", "climate.temperature", "soil.organic_carbon"],
            "biophysical_basis": "Precipitation shortfall, root zone moisture exhaustion, high evaporative demand (VPD), and SOC water retention collapse.",
            "levels": ["low", "medium", "high", "unknown"],
            "evidence_sources": ["IPCC AR6 WGII Chapter 2", "Rawls et al. (2003)", "Lal (2004)"],
        },
        {
            "dimension_id": "habitat_pressure",
            "name": "Habitat Degradation & Structural Simplification",
            "evaluates": ["land.land_use", "land.land_cover", "human_impact.deforestation", "biodiversity.habitat_diversity"],
            "biophysical_basis": "Monocultural landscape simplification, canopy fragmentation, edge effect proliferation, and loss of structural micro-refugia.",
            "levels": ["low", "medium", "high", "unknown"],
            "evidence_sources": ["Haddad et al. (2015)", "Benton et al. (2003)", "IPBES Global Assessment (2019)"],
        },
        {
            "dimension_id": "biodiversity_pressure",
            "name": "Biodiversity Depletion & Trophic Collapse Risk",
            "evaluates": ["biodiversity.species_richness", "biodiversity.habitat_diversity", "land.land_use", "human_impact.deforestation"],
            "biophysical_basis": "Species richness loss, trophic redundancy collapse, functional guild depletion, and pollinator/predator vulnerability.",
            "levels": ["low", "medium", "high", "unknown"],
            "evidence_sources": ["Tilman et al. (2014)", "IPBES Global Assessment (2019)", "Benton et al. (2003)"],
        },
        {
            "dimension_id": "climate_exposure",
            "name": "Climate Extremes & Thermal-Hydro Exposure",
            "evaluates": ["climate.temperature", "climate.rainfall"],
            "biophysical_basis": "Thermal extremes exceeding physiological optimum, meteorological rainfall deficits, and deluge/runoff shocks.",
            "levels": ["low", "medium", "high", "unknown"],
            "evidence_sources": ["IPCC AR6 WGII (2022)", "UNEP Adaptation Gap Report (2021)"],
        },
        {
            "dimension_id": "human_disturbance",
            "name": "Anthropogenic Disturbance & Ecotoxicity Pressure",
            "evaluates": ["human_impact.pollution", "human_impact.deforestation", "land.land_use"],
            "biophysical_basis": "Chemical ecotoxicity, pollutant bioaccumulation, extractive clearing, and physical habitat disruption.",
            "levels": ["low", "medium", "high", "unknown"],
            "evidence_sources": ["UNEP GEO-6 (2019)", "IPBES Global Assessment (2019)", "Haddad et al. (2015)"],
        },
    ]
