"""SQLAlchemy ORM models for persistent environmental state profiles."""

import uuid
from typing import Any, Dict, Optional
from sqlalchemy import String, Text, Float, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.base import Base, TimestampMixin
from backend.app.schemas.environmental_state import EnvironmentalState


class EnvironmentalProfile(Base, TimestampMixin):
    """Database model storing an environmental profile observation/state."""

    __tablename__ = "environmental_profiles"

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
    name: Mapped[Optional[str]] = mapped_column(
        String(255),
        nullable=True,
        index=True,
    )
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # Indexed top-level spatial anchors for rapid filtering/queries
    latitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        index=True,
    )
    longitude: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
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

    # Serialized canonical EnvironmentalState dictionary
    state_data: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: EnvironmentalState().model_dump(),
    )

    # Count of non-null scientific variables
    metrics_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    # Future-proof metadata storage for evidence links, session notes, conversation ID
    metadata_json: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        default=dict,
    )

    def to_canonical_state(self) -> EnvironmentalState:
        """Deserialize internal JSON dictionary into validated Pydantic EnvironmentalState."""
        return EnvironmentalState.model_validate(self.state_data or {})

    def sync_spatial_and_metrics(self, state: EnvironmentalState) -> None:
        """Synchronize indexed columns and metrics count from a canonical state."""
        self.state_data = state.model_dump()
        self.metrics_count = state.count_known_metrics()
        self.latitude = state.spatial_context.latitude
        self.longitude = state.spatial_context.longitude
        self.region = state.spatial_context.region
        self.ecosystem = state.spatial_context.ecosystem
