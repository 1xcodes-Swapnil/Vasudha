"""API Endpoints for Ecological Interventions and Recommendation Engine (Phase 10)."""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status

from backend.app.schemas.intervention import (
    InterventionDefinition,
    InterventionEngineRequest,
    RecommendationSetResponse,
)
from backend.app.knowledge.intervention_engine import get_intervention_engine

router = APIRouter()


@router.post(
    "/recommend",
    response_model=RecommendationSetResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Ranked Ecological Recommendations",
    description="Transforms observed environmental state and multi-metric ecological findings into context-specific, biophysically suitable, evidence-backed interventions.",
)
def generate_recommendations(request: InterventionEngineRequest) -> RecommendationSetResponse:
    """Generate prioritized, evidence-grounded ecological recommendations."""
    engine = get_intervention_engine()
    try:
        return engine.generate_recommendations(request)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error evaluating intervention recommendations: {str(e)}",
        )


@router.get(
    "/catalogue",
    response_model=List[InterventionDefinition],
    status_code=status.HTTP_200_OK,
    summary="List Canonical Intervention Catalogue",
    description="Retrieve all curated canonical ecological interventions in the Knowledge Base with biophysical rules, mechanisms, and evidence IDs.",
)
def list_catalogue() -> List[InterventionDefinition]:
    """List all available canonical ecological interventions."""
    engine = get_intervention_engine()
    return engine.list_interventions()


@router.get(
    "/{intervention_id}",
    response_model=InterventionDefinition,
    status_code=status.HTTP_200_OK,
    summary="Get Specific Intervention Definition",
    description="Retrieve complete scientific details, biophysical envelopes, trade-offs, and evidence citations for a specific intervention ID.",
)
def get_intervention_by_id(intervention_id: str) -> InterventionDefinition:
    """Retrieve detailed intervention definition by unique ID."""
    engine = get_intervention_engine()
    intervention = engine.get_intervention(intervention_id)
    if not intervention:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Intervention with ID '{intervention_id}' not found in canonical catalogue.",
        )
    return intervention
