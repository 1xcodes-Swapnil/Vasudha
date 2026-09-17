"""SQLAlchemy ORM models for the Ecological Knowledge Base (Phase 3)."""

from typing import Any, Dict, List, Optional
from sqlalchemy import Boolean, Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.base import Base, TimestampMixin


class EnvironmentalMetricModel(Base, TimestampMixin):
    """Database entity representing an environmental variable or derived state."""

    __tablename__ = "environmental_metrics"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    domain: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    unit: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    metric_type: Mapped[str] = mapped_column(String(32), nullable=False, default="numeric")
    description: Mapped[str] = mapped_column(Text, nullable=False)
    min_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    max_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    categories_json: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)


class EvidenceMetadataModel(Base, TimestampMixin):
    """Database entity storing peer-reviewed and institutional scientific evidence."""

    __tablename__ = "evidence_sources"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    citation: Mapped[str] = mapped_column(Text, nullable=False)
    doi: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    institution: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    url: Mapped[Optional[str]] = mapped_column(String(256), nullable=True)
    requires_evidence: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    confidence_grade: Mapped[str] = mapped_column(String(32), nullable=False, default="high")


class EcologicalRelationshipModel(Base, TimestampMixin):
    """Database entity storing deterministic scientific ecological relationships."""

    __tablename__ = "ecological_relationships"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    source_metric: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    operator: Mapped[str] = mapped_column(String(16), nullable=False)
    threshold_value: Mapped[Any] = mapped_column(JSON, nullable=False)
    target_metric: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    target_state: Mapped[str] = mapped_column(String(64), nullable=False)
    relationship_type: Mapped[str] = mapped_column(String(32), nullable=False)
    direction: Mapped[str] = mapped_column(String(32), nullable=False, default="negative")
    ecological_mechanism: Mapped[str] = mapped_column(Text, nullable=False)
    evidence_ids: Mapped[List[str]] = mapped_column(JSON, nullable=False, default=list)
    evidence_strength: Mapped[str] = mapped_column(String(32), nullable=False, default="strong")
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.9)
    ecosystem_context: Mapped[str] = mapped_column(String(64), nullable=False, default="all")
    quality_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False, default=dict)
