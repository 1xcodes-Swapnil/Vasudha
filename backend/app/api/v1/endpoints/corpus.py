"""FastAPI endpoints for Scientific Corpus, Ingestion, and Semantic RAG Retrieval (Phase 4)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.knowledge.rag_service import get_rag_service
from backend.app.schemas.scientific_rag import (
    EvidenceChunkPacket,
    EvidencePacketResponse,
    ScientificChunk,
    ScientificDocument,
    ScientificDocumentCreate,
    ScientificSearchQuery,
    ScientificSourceType,
)

router = APIRouter()


@router.get(
    "/documents",
    response_model=List[ScientificDocument],
    summary="List all ingested scientific publications with metadata and filters",
)
def list_documents(
    organization: Optional[str] = Query(None, description="Filter by publisher/institution (IPCC, IPBES, FAO, UNEP, CBD, etc.)"),
    source_type: Optional[ScientificSourceType] = Query(None, description="Filter by source classification"),
    metric: Optional[str] = Query(None, description="Filter by analyzed environmental metric"),
) -> List[ScientificDocument]:
    """Retrieve indexed scientific publications and their peer-review metadata."""
    rag_service = get_rag_service()
    return rag_service.list_documents(
        organization=organization,
        source_type=source_type,
        metric=metric,
    )


@router.get(
    "/documents/{document_id}",
    response_model=ScientificDocument,
    summary="Retrieve a single scientific document by ID",
)
def get_document(
    document_id: str = Path(..., description="Document ID, e.g. 'DOC_IPCC_WG2_2022_CH2'"),
) -> ScientificDocument:
    """Retrieve full metadata for a specific scientific publication."""
    rag_service = get_rag_service()
    doc = rag_service.get_document(document_id)
    if not doc:
        raise HTTPException(
            status_code=404,
            detail=f"Scientific document '{document_id}' not found in knowledge store.",
        )
    return doc


@router.get(
    "/documents/{document_id}/chunks",
    response_model=List[ScientificChunk],
    summary="Retrieve all text chunks and section headers for a scientific document",
)
def get_document_chunks(
    document_id: str = Path(..., description="Document ID, e.g. 'DOC_IPCC_WG2_2022_CH2'"),
) -> List[ScientificChunk]:
    """Retrieve passages/chunks belonging to a scientific document."""
    rag_service = get_rag_service()
    chunks = rag_service.get_document_chunks(document_id)
    if not chunks:
        raise HTTPException(
            status_code=404,
            detail=f"No chunks found for scientific document '{document_id}'.",
        )
    return chunks


@router.post(
    "/documents",
    response_model=ScientificDocument,
    status_code=201,
    summary="Ingest, chunk, embed, and index a new scientific document into the corpus",
)
def ingest_document(
    document: ScientificDocumentCreate,
    db: Session = Depends(get_db),
) -> ScientificDocument:
    """Ingest a peer-reviewed or institutional study with automated chunking and vector embedding."""
    rag_service = get_rag_service()
    try:
        return rag_service.ingest_document(document, db=db, persist_db=True)
    except ValueError as val_err:
        raise HTTPException(status_code=422, detail=str(val_err))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to ingest document: {exc}")


@router.post(
    "/search",
    response_model=EvidencePacketResponse,
    summary="Two-stage semantic vector & metadata search over scientific corpus",
)
def search_evidence(
    search_query: ScientificSearchQuery,
) -> EvidencePacketResponse:
    """Perform semantic vector retrieval with composite reranking across scientific literature.
    
    Returns:
    - 5 to 8 compact, high-relevance evidence chunks
    - Exact author, citation, year, and DOI source traceability
    - Ecosystem and geographic applicability evaluation
    - Explicit 'insufficient_evidence' flag if quality threshold is not met
    """
    rag_service = get_rag_service()
    return rag_service.search_evidence(search_query)


@router.post(
    "/evidence-packet",
    response_model=EvidencePacketResponse,
    summary="Retrieve a compact structured evidence packet for specific environmental indicators",
)
def get_evidence_packet(
    search_query: ScientificSearchQuery,
) -> EvidencePacketResponse:
    """Convenience alias for retrieving structured evidence packets for ecological reasoning."""
    rag_service = get_rag_service()
    return rag_service.search_evidence(search_query)
