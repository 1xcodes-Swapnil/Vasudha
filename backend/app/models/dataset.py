"""SQLAlchemy ORM models for Authoritative Datasets and Environmental Observations (Phase 7).

Stores:
- DatasetRegistryModel: Registry of authoritative environmental datasets and metadata
- IngestedObservationModel: Ingested, quality-checked environmental observations with full provenance
"""

import uuid
from typing import Any, Dict, Optional, List
from sqlalchemy import String, Text, Float, Integer, Boolean, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.base import Base, TimestampMixin


class DatasetRegistryModel(Base, TimestampMixin):
    """Database model storing metadata for authoritative environmental datasets."""

    __tablename__ = "dataset_registry"

    id: Mapped[str] = mapped_column(
        String(64),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    source_organization: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
    )
    source_url: Mapped[str] = mapped_column(
        String(512),
        nullable=False,
    )
    license: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    domain: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    variables_json: Mapped[List[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    raw_units_json: Mapped[Dict[str, str]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    canonical_units_json: Mapped[Dict[str, str]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    geographic_coverage: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    temporal_coverage: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    spatial_resolution: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
    )
    retrieval_date: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )
    provenance: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    known_limitations_json: Mapped[List[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
    )
    is_authoritative: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )


class IngestedObservationModel(Base, TimestampMixin):
    """Database model storing ingested, quality-checked environmental observations."""

    __tablename__ = "ingested_environmental_observations"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    dataset_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
    )
    latitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        index=True,
    )
    longitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        index=True,
    )
    region: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )
    ecosystem: Mapped[Optional[str]] = mapped_column(
        String(128),
        nullable=True,
        index=True,
    )
    raw_payload_json: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    normalized_state_json: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    provenance_json: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    quality_report_json: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=dict,
    )
    is_valid: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        index=True,
    )
    is_synthetic: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )
