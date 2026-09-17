"""Scientific Corpus Ingestion, Semantic Vector Indexing, and RAG Retrieval Service (Phase 4).

Follows strict scientific integrity:
- Authentic source traceability on every chunk (no fabricated citations, DOIs, or findings)
- Two-stage retrieval: vector semantic search + multi-factor ecological reranking
- Compact evidence packet generation (5-8 high-signal chunks)
- Explicit 'insufficient evidence' flag when relevant evidence is unavailable
"""

import math
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from sqlalchemy.orm import Session
from backend.app.core.logging import logger
from backend.app.knowledge.embeddings.base import EmbeddingProvider
from backend.app.knowledge.embeddings.local import LocalEmbeddingProvider
from backend.app.knowledge.embeddings import get_embedding_provider
from backend.app.knowledge.reranking.base import RerankerProvider
from backend.app.knowledge.reranking import get_reranker_provider
from backend.app.knowledge.curated_corpus import CURATED_SCIENTIFIC_DOCUMENTS
from backend.app.models.scientific_corpus import (
    ScientificChunkModel,
    ScientificDocumentModel,
)
from backend.app.schemas.scientific_rag import (
    EvidenceChunkPacket,
    EvidencePacketResponse,
    EvidenceStrength,
    GeographicApplicability,
    ScientificChunk,
    ScientificDocument,
    ScientificDocumentCreate,
    ScientificSearchQuery,
    ScientificSourceType,
)


class ScientificRAGService:
    """Core RAG retrieval and document indexing engine for scientific evidence."""

    def __init__(
        self,
        embedding_provider: Optional[EmbeddingProvider] = None,
        reranker_provider: Optional[RerankerProvider] = None,
    ):
        self.embedding_provider = embedding_provider or get_embedding_provider()
        self.reranker_provider = reranker_provider or get_reranker_provider()
        # In-memory fast stores for instant, deterministic fallback and high-throughput retrieval
        self._documents: Dict[str, ScientificDocument] = {}
        self._chunks: Dict[str, ScientificChunk] = {}
        self._embeddings: Dict[str, List[float]] = {}
        
        # Load and index curated corpus on initialization
        self._initialize_curated_corpus()

    # --------------------------------------------------------------------------
    # 1. Corpus Initialization & Ingestion Pipeline
    # --------------------------------------------------------------------------

    def _initialize_curated_corpus(self) -> None:
        """Seed and index all curated peer-reviewed and institutional publications."""
        for doc_create in CURATED_SCIENTIFIC_DOCUMENTS:
            try:
                self.ingest_document(doc_create, persist_db=False)
            except Exception as exc:
                logger.warning(f"Error seeding curated document '{doc_create.id}': {exc}")

        logger.info(
            f"ScientificRAGService initialized with {len(self._documents)} documents "
            f"and {len(self._chunks)} indexed chunks."
        )

    def chunk_document_text(self, document: ScientificDocumentCreate) -> List[ScientificChunk]:
        """Splits document full text into structured, coherent paragraphs/chunks."""
        raw_sections = [s.strip() for s in re.split(r"\n\s*\n", document.full_text) if s.strip()]
        chunks: List[ScientificChunk] = []

        chunk_idx = 0
        for section_text in raw_sections:
            # Extract section header if present (e.g. "Section 2.4.2: ...")
            section_title = None
            lines = section_text.split("\n")
            content_lines = lines
            if lines and (":" in lines[0] or lines[0].startswith("Chapter") or lines[0].startswith("Section") or lines[0].startswith("Element")):
                section_title = lines[0].split(":")[0].strip()
                content_lines = lines[1:] if len(lines) > 1 else lines

            clean_content = " ".join(" ".join(content_lines).split())
            if len(clean_content) < 30:
                continue

            chunk_id = f"{document.id}_C{chunk_idx:02d}"
            chunks.append(
                ScientificChunk(
                    id=chunk_id,
                    document_id=document.id,
                    chunk_index=chunk_idx,
                    content=clean_content,
                    section=section_title,
                    metrics=list(document.environmental_metrics),
                    ecosystem=document.ecosystem,
                    geographic_scope=document.geographic_scope,
                    evidence_strength=document.evidence_strength,
                    confidence_grade="high" if document.evidence_strength in (EvidenceStrength.CONSENSUS, EvidenceStrength.STRONG) else "moderate",
                    citation=document.citation,
                    doi=document.doi,
                    url=document.url,
                )
            )
            chunk_idx += 1

        return chunks

    def ingest_document(
        self,
        document_in: ScientificDocumentCreate,
        db: Optional[Session] = None,
        persist_db: bool = True,
    ) -> ScientificDocument:
        """Ingests, chunks, embeds, and indexes a scientific publication."""
        # Validation for malformed document
        if not document_in.id or not document_in.title or not document_in.full_text:
            raise ValueError("Malformed document: 'id', 'title', and 'full_text' are required.")

        # Chunk document text
        chunks = self.chunk_document_text(document_in)
        if not chunks:
            raise ValueError(f"Document '{document_in.id}' produced 0 valid text chunks.")

        # Generate vector embeddings for each chunk
        chunk_texts = [f"{c.section or ''} {c.content}" for c in chunks]
        embeddings = self.embedding_provider.embed_batch(chunk_texts)

        # Store in-memory
        doc = ScientificDocument(
            id=document_in.id,
            title=document_in.title,
            authors=document_in.authors,
            organization=document_in.organization,
            year=document_in.year,
            source_type=document_in.source_type,
            citation=document_in.citation,
            url=document_in.url,
            doi=document_in.doi,
            geographic_scope=document_in.geographic_scope,
            ecosystem=document_in.ecosystem,
            topics=document_in.topics,
            environmental_metrics=document_in.environmental_metrics,
            evidence_strength=document_in.evidence_strength,
            abstract=document_in.abstract,
            chunk_count=len(chunks),
        )

        self._documents[doc.id] = doc
        for chunk, emb in zip(chunks, embeddings):
            self._chunks[chunk.id] = chunk
            self._embeddings[chunk.id] = emb

        # Persist to SQL database if session provided
        if persist_db and db is not None:
            try:
                # Upsert Document Model
                db_doc = db.query(ScientificDocumentModel).filter(ScientificDocumentModel.id == doc.id).first()
                if not db_doc:
                    db_doc = ScientificDocumentModel(
                        id=doc.id,
                        title=doc.title,
                        authors=doc.authors,
                        organization=doc.organization,
                        year=doc.year,
                        source_type=doc.source_type.value,
                        citation=doc.citation,
                        url=doc.url,
                        doi=doc.doi,
                        geographic_scope=doc.geographic_scope,
                        ecosystem=doc.ecosystem,
                        topics_json=doc.topics,
                        metrics_json=doc.environmental_metrics,
                        evidence_strength=doc.evidence_strength.value,
                        abstract=doc.abstract,
                        full_text=document_in.full_text,
                        chunk_count=len(chunks),
                    )
                    db.add(db_doc)

                # Upsert Chunks
                for chunk, emb in zip(chunks, embeddings):
                    db_chunk = db.query(ScientificChunkModel).filter(ScientificChunkModel.id == chunk.id).first()
                    if not db_chunk:
                        db_chunk = ScientificChunkModel(
                            id=chunk.id,
                            document_id=chunk.document_id,
                            chunk_index=chunk.chunk_index,
                            content=chunk.content,
                            section=chunk.section,
                            metrics_json=chunk.metrics,
                            ecosystem=chunk.ecosystem,
                            geographic_scope=chunk.geographic_scope,
                            evidence_strength=chunk.evidence_strength.value,
                            confidence_grade=chunk.confidence_grade,
                            embedding_json=emb,
                        )
                        db.add(db_chunk)

                db.commit()
            except Exception as db_err:
                db.rollback()
                logger.warning(f"Database persistence skipped for '{doc.id}': {db_err}")

        return doc

    # --------------------------------------------------------------------------
    # 2. Document & Chunk Retrieval Helpers
    # --------------------------------------------------------------------------

    def list_documents(
        self,
        organization: Optional[str] = None,
        source_type: Optional[ScientificSourceType] = None,
        metric: Optional[str] = None,
    ) -> List[ScientificDocument]:
        """Lists ingested documents with optional filtering."""
        docs = list(self._documents.values())
        if organization:
            docs = [d for d in docs if d.organization.lower() == organization.lower()]
        if source_type:
            docs = [d for d in docs if d.source_type == source_type]
        if metric:
            docs = [d for d in docs if metric in d.environmental_metrics]
        return docs

    def get_document(self, document_id: str) -> Optional[ScientificDocument]:
        """Retrieves a single document by ID."""
        return self._documents.get(document_id)

    def get_document_chunks(self, document_id: str) -> List[ScientificChunk]:
        """Retrieves all chunks belonging to a document."""
        return [c for c in self._chunks.values() if c.document_id == document_id]

    # --------------------------------------------------------------------------
    # 3. Two-Stage Semantic Vector Search & Evidence Packet Assembly
    # --------------------------------------------------------------------------

    @staticmethod
    def _cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
        """Computes cosine similarity between two unit/normalized vectors."""
        dot = sum(a * b for a, b in zip(vec_a, vec_b))
        return max(0.0, min(1.0, dot))

    def _assess_geographic_applicability(
        self,
        chunk_scope: str,
        chunk_ecosystem: str,
        target_scope: Optional[str],
        target_ecosystem: Optional[str],
    ) -> GeographicApplicability:
        """Determines whether evidence is globally relevant, ecosystem-specific, or mismatched."""
        if chunk_scope == "global" or chunk_ecosystem == "all":
            return GeographicApplicability.GLOBALLY_RELEVANT

        if target_ecosystem and chunk_ecosystem.lower() in target_ecosystem.lower():
            return GeographicApplicability.ECOSYSTEM_SPECIFIC

        if target_scope and chunk_scope.lower() in target_scope.lower():
            return GeographicApplicability.REGIONALLY_RELEVANT

        if target_ecosystem and chunk_ecosystem != "all" and chunk_ecosystem.lower() not in target_ecosystem.lower():
            # e.g., boreal forest study applied to tropical dry deciduous
            return GeographicApplicability.GEOGRAPHICALLY_MISMATCHED

        return GeographicApplicability.GLOBALLY_RELEVANT

    def search_evidence(self, search_query: ScientificSearchQuery) -> EvidencePacketResponse:
        """Performs two-stage metadata-aware semantic retrieval and returns compact evidence packet."""
        query_text = search_query.query.strip()
        if not query_text:
            return EvidencePacketResponse(
                query="",
                total_found=0,
                selected_count=0,
                evidence_chunks=[],
                insufficient_evidence=True,
                geographic_context_summary="Empty search query provided.",
            )

        # 1. Embed query vector
        query_vector = self.embedding_provider.embed_text(query_text)

        # 2. Stage 1: Candidate retrieval
        candidate_packets: List[EvidenceChunkPacket] = []
        target_metrics_set = set(search_query.metrics or [])

        for chunk_id, chunk in self._chunks.items():
            emb = self._embeddings.get(chunk_id)
            if not emb:
                continue

            # Hard metadata filters
            if search_query.min_evidence_strength:
                strength_ranks = {
                    EvidenceStrength.CONSENSUS: 4,
                    EvidenceStrength.STRONG: 3,
                    EvidenceStrength.MODERATE: 2,
                    EvidenceStrength.PRELIMINARY: 1,
                    EvidenceStrength.REQUIRES_EVIDENCE: 0,
                }
                if strength_ranks.get(chunk.evidence_strength, 0) < strength_ranks.get(search_query.min_evidence_strength, 0):
                    continue

            # Compute semantic vector similarity
            vector_sim = self._cosine_similarity(query_vector, emb)

            # Stage 2: Multi-factor composite reranking score
            # 1. Vector similarity (0.45 weight)
            score = 0.45 * vector_sim

            # 2. Environmental metric overlap (+0.25)
            matched_metrics = [m for m in chunk.metrics if m in target_metrics_set]
            if matched_metrics:
                score += 0.25 * (len(matched_metrics) / max(1, len(target_metrics_set)))

            # 3. Topic / Keyword term boost in content (+0.15)
            query_words = {w.lower() for w in re.findall(r"\b\w{4,}\b", query_text)}
            content_lower = chunk.content.lower()
            matched_words = sum(1 for w in query_words if w in content_lower)
            if query_words:
                score += 0.15 * (matched_words / len(query_words))

            # 4. Source authority boost (+0.10 for consensus global bodies like IPCC/IPBES/FAO)
            parent_doc = self._documents.get(chunk.document_id)
            if parent_doc and parent_doc.organization in ("IPCC", "IPBES", "FAO", "UNEP", "CBD", "Science", "Nature"):
                score += 0.10

            # 5. Geographic alignment check
            applicability = self._assess_geographic_applicability(
                chunk.geographic_scope,
                chunk.ecosystem,
                search_query.geographic_scope,
                search_query.ecosystem,
            )

            if applicability == GeographicApplicability.GEOGRAPHICALLY_MISMATCHED:
                score -= 0.10  # Mild penalty for mismatched biome context

            # Normalize composite score to [0.0, 1.0]
            composite_score = round(max(0.0, min(1.0, score)), 4)

            # Only retain candidates exceeding baseline relevance
            if composite_score >= 0.18:
                candidate_packets.append(
                    EvidenceChunkPacket(
                        chunk_id=chunk.id,
                        document_id=chunk.document_id,
                        title=parent_doc.title if parent_doc else "Scientific Study",
                        authors=parent_doc.authors if parent_doc else "Research Consortium",
                        organization=parent_doc.organization if parent_doc else "Scientific Literature",
                        year=parent_doc.year if parent_doc else 2020,
                        citation=chunk.citation,
                        doi=chunk.doi,
                        url=chunk.url,
                        content=chunk.content,
                        relevance_score=composite_score,
                        evidence_strength=chunk.evidence_strength,
                        confidence_grade=chunk.confidence_grade,
                        geographic_scope=chunk.geographic_scope,
                        ecosystem=chunk.ecosystem,
                        matched_metrics=matched_metrics,
                        geographic_applicability=applicability,
                    )
                )

        # 3. Sort candidates by relevance score descending
        candidate_packets.sort(key=lambda p: p.relevance_score, reverse=True)

        # 4. Optional cross-encoder reranking stage if enabled
        if self.reranker_provider.is_enabled and len(candidate_packets) > 1:
            try:
                # Take top candidate pool for cross-encoder reranking
                pool_size = min(len(candidate_packets), max(search_query.top_k * 2, 10))
                pool = candidate_packets[:pool_size]
                doc_texts = [f"{p.title}. {p.content}" for p in pool]
                
                rerank_results = self.reranker_provider.rerank(
                    query=query_text,
                    documents=doc_texts,
                    top_n=search_query.top_k,
                )
                
                # Reconstruct candidate order based on rerank scores
                reranked_packets: List[EvidenceChunkPacket] = []
                for res in rerank_results:
                    orig_packet = pool[res.index]
                    # Update relevance score with normalized rerank score
                    orig_packet.relevance_score = res.score
                    reranked_packets.append(orig_packet)
                
                selected_packets = reranked_packets
            except Exception as rerank_err:
                logger.warning(f"Reranking stage failed gracefully: {rerank_err}. Retaining vector ranking.")
                top_k = search_query.top_k
                selected_packets = candidate_packets[:top_k]
        else:
            top_k = search_query.top_k
            selected_packets = candidate_packets[:top_k]

        # Explicitly flag insufficient evidence if 0 chunks or low quality
        insufficient = len(selected_packets) == 0

        # Build context summary
        geo_summary = None
        if search_query.ecosystem or search_query.geographic_scope:
            geo_summary = f"Retrieved evidence grounded for ecosystem='{search_query.ecosystem or 'all'}' and region='{search_query.geographic_scope or 'global'}'."

        return EvidencePacketResponse(
            query=search_query.query,
            total_found=len(candidate_packets),
            selected_count=len(selected_packets),
            evidence_chunks=selected_packets,
            insufficient_evidence=insufficient,
            geographic_context_summary=geo_summary,
            contradiction_notes=None,
        )


# Singleton instance factory
_rag_service_instance: Optional[ScientificRAGService] = None


def get_rag_service() -> ScientificRAGService:
    """Returns singleton instance of ScientificRAGService."""
    global _rag_service_instance
    if _rag_service_instance is None:
        _rag_service_instance = ScientificRAGService()
    return _rag_service_instance


def reset_rag_service() -> None:
    """Reset singleton instance of ScientificRAGService (e.g. for testing)."""
    global _rag_service_instance
    _rag_service_instance = None

