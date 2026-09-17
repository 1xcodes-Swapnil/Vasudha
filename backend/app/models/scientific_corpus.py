"""SQLAlchemy ORM models for Scientific Corpus & Document Chunks (Phase 4)."""

from typing import Any, Dict, List, Optional
from sqlalchemy import Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.base import Base, TimestampMixin


class ScientificDocumentModel(Base, TimestampMixin):
    """Database entity representing a peer-reviewed or institutional scientific publication."""

    __tablename__ = "scientific_documents"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    title: Mapped[str] = mapped_column(String(256), nullable=False, index=True)
    authors: Mapped[str] = mapped_column(String(256), nullable=False)
    organization: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    citation: Mapped[str] = mapped_column(Text, nullable=False)
    url: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    doi: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    geographic_scope: Mapped[str] = mapped_column(String(64), nullable=False, default="global", index=True)
    ecosystem: Mapped[str] = mapped_column(String(64), nullable=False, default="all", index=True)
    topics_json: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    metrics_json: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    evidence_strength: Mapped[str] = mapped_column(String(32), nullable=False, default="strong")
    abstract: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    full_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class ScientificChunkModel(Base, TimestampMixin):
    """Database entity representing a chunk of scientific text with embedding and metadata."""

    __tablename__ = "scientific_chunks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    document_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    section: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    metrics_json: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    ecosystem: Mapped[str] = mapped_column(String(64), nullable=False, default="all")
    geographic_scope: Mapped[str] = mapped_column(String(64), nullable=False, default="global")
    evidence_strength: Mapped[str] = mapped_column(String(32), nullable=False, default="strong")
    confidence_grade: Mapped[str] = mapped_column(String(32), nullable=False, default="high")
    embedding_json: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
