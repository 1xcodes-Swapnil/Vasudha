"""FastAPI endpoints for querying the Ecological Knowledge Base (Phase 3)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.schemas.knowledge import (
    EcologicalRelationship,
    EnvironmentalMetricDefinition,
    EvidenceMetadata,
)
from backend.app.knowledge.repository import KnowledgeRepository

router = APIRouter()


@router.get(
    "/metrics",
    response_model=List[EnvironmentalMetricDefinition],
    summary="List all supported environmental metrics and derived state definitions",
)
def list_metrics(
    domain: Optional[str] = Query(None, description="Optional domain filter: soil, land, biodiversity, climate, human_impact, ecological_state"),
    db: Session = Depends(get_db),
) -> List[EnvironmentalMetricDefinition]:
    """Retrieve curated environmental and ecological state metric definitions."""
    return KnowledgeRepository.get_all_metrics(db=db, domain=domain)


@router.get(
    "/relationships",
    response_model=List[EcologicalRelationship],
    summary="List structured ecological relationships",
)
def list_relationships(
    source_metric: Optional[str] = Query(None, description="Filter by source metric, e.g. 'soil.organic_carbon'"),
    target_metric: Optional[str] = Query(None, description="Filter by target metric, e.g. 'derived.plant_water_stress'"),
    ecosystem: Optional[str] = Query(None, description="Filter by ecosystem applicability"),
    db: Session = Depends(get_db),
) -> List[EcologicalRelationship]:
    """Retrieve deterministic ecological relationships with biophysical mechanisms and evidence IDs."""
    return KnowledgeRepository.get_all_relationships(
        db=db,
        source_metric=source_metric,
        target_metric=target_metric,
        ecosystem=ecosystem,
    )


@router.get(
    "/evidence",
    response_model=List[EvidenceMetadata],
    summary="List peer-reviewed and institutional evidence sources",
)
def list_evidence(
    institution: Optional[str] = Query(None, description="Filter by institution, e.g. FAO, IPCC, IPBES, UNEP"),
    db: Session = Depends(get_db),
) -> List[EvidenceMetadata]:
    """Retrieve official evidence citations, DOIs, and literature metadata."""
    return KnowledgeRepository.get_all_evidence(db=db, institution=institution)


@router.post(
    "/seed",
    summary="Seed the database with curated metrics, evidence, and relationships",
)
def seed_knowledge_base(db: Session = Depends(get_db)):
    """Synchronize the database tables with the curated ecological knowledge base."""
    return KnowledgeRepository.seed_knowledge_base(db=db)
