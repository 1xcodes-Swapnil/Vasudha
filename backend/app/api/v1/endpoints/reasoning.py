"""FastAPI endpoints for the Deterministic Ecological Reasoning Engine & Multi-Metric RAG Integration (Phases 3, 5, & 9)."""

from typing import Any, Dict
from fastapi import APIRouter, HTTPException, Path
from backend.app.schemas.environmental_state import EnvironmentalState
from backend.app.schemas.knowledge import EcologicalRelationship, ReasoningEvaluationResult
from backend.app.schemas.scientific_rag import MultiMetricAnalysisResponse
from backend.app.schemas.ecological_findings import (
    EcologicalFindingsRequest,
    EcologicalFindingsResponse,
)
from backend.app.knowledge.reasoning_engine import get_reasoning_engine
from backend.app.knowledge.multi_metric_engine import get_multi_metric_engine
from backend.app.knowledge.pipeline_service import get_findings_pipeline_service
from backend.app.knowledge.text_extractor import text_extractor

router = APIRouter()


@router.post(
    "/evaluate",
    response_model=ReasoningEvaluationResult,
    summary="Evaluate an EnvironmentalState and infer ecological pressures and causal reasoning chains",
)
def evaluate_environmental_state(state: EnvironmentalState) -> ReasoningEvaluationResult:
    """Execute deterministic ecological relationship reasoning over an EnvironmentalState.
    
    Returns:
    - Inferred ecological pressures and drivers with severity and mechanisms
    - Distinctions between Observed, Inferred, and Unknown metrics (zero vs null handled strictly)
    - Multi-metric synergistic compound stresses (e.g. drought + thermal stress)
    - Complete forward-chaining reasoning chains for explainability and inspection
    """
    engine = get_reasoning_engine()
    return engine.evaluate_state(state)


@router.post(
    "/multi-metric-analysis",
    response_model=MultiMetricAnalysisResponse,
    summary="Comprehensive Multi-Metric Ecological Reasoning with attached Scientific RAG evidence packets (Phase 5)",
)
def analyze_multi_metric_state(state: EnvironmentalState) -> MultiMetricAnalysisResponse:
    """Execute deep multi-metric ecological analysis combining 3+ environmental variables with RAG evidence.
    
    Returns:
    - Observed vs Unknown metric classification (strict zero vs null distinction)
    - Multi-metric synergistic nature pressure profiles
    - Step-by-step biophysical reasoning chains
    - 5 to 8 attached peer-reviewed & institutional evidence chunks per pressure
    - Geographic applicability and contextual limitation statements
    """
    engine = get_multi_metric_engine()
    return engine.analyze_environmental_state(state)


@router.post(
    "/ecological-findings",
    response_model=EcologicalFindingsResponse,
    summary="End-to-End Ecological Reasoning & Findings with Dataset Integration, Conflicts & RAG Evidence (Phase 9)",
)
def generate_ecological_findings(req: EcologicalFindingsRequest) -> EcologicalFindingsResponse:
    """Transforms raw text, structured state, or geographic coordinates into structured ecological findings.
    
    Pipeline Steps:
    1. Parse natural language description and extract environmental variables
    2. Resolve geographic context (region, biome/ecosystem)
    3. Query and enrich from authoritative datasets (SoilGrids, WorldClim, Copernicus, GBIF, GFW, UNEP)
    4. Audit for user vs dataset discrepancies and geographic mismatches
    5. Execute multi-metric deterministic reasoning (3+ variables)
    6. Retrieve targeted peer-reviewed and institutional evidence packets from Scientific RAG
    7. Formulate structured findings with clear observed vs dataset-derived vs unknown provenance
    """
    service = get_findings_pipeline_service()
    return service.process_request(req)


@router.post(
    "/extract-state",
    summary="Extract structured environmental state and variables from natural language text",
)
def extract_state_from_text(payload: Dict[str, str]) -> Dict[str, Any]:
    """Parse natural language query or site notes to extract structured environmental metrics."""
    text = payload.get("text", "")
    state, extracted_map = text_extractor.extract_from_text(text)
    return {
        "state": state.model_dump(),
        "extracted_variables": extracted_map,
        "variables_count": len(extracted_map),
    }


@router.get(
    "/explain/{relationship_id}",
    response_model=EcologicalRelationship,
    summary="Expose biophysical mechanism, evidence citations, and metadata for a specific ecological rule",
)
def explain_relationship(
    relationship_id: str = Path(..., description="ID of the relationship, e.g. 'REL_SOC_WATER_RETENTION_LOW'")
) -> EcologicalRelationship:
    """Explain why an ecological relationship fires, including its underlying biophysical mechanism and evidence citations."""
    engine = get_reasoning_engine()
    rel = engine.relationship_map.get(relationship_id)
    if not rel:
        raise HTTPException(
            status_code=404,
            detail=f"Ecological relationship '{relationship_id}' not found in knowledge base.",
        )
    return rel


