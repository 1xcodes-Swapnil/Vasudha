"""Abstract Base Adapter for Environmental Dataset Providers (Phase 7).

Defines standard interface for fetching, parsing, normalizing, quality-checking,
and generating provenance for environmental observations.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple, Optional
from backend.app.schemas.dataset import (
    DatasetMetadata,
    RawDatasetObservation,
    DataQualityCheck,
    VariableProvenance,
    DataQualitySeverity,
    QualityFlagType,
)


class DatasetAdapter(ABC):
    """Abstract base class for all authoritative environmental dataset adapters."""

    def __init__(self, metadata: DatasetMetadata):
        self.metadata = metadata

    @property
    def dataset_id(self) -> str:
        return self.metadata.id

    @property
    def name(self) -> str:
        return self.metadata.name

    @abstractmethod
    def fetch_point(
        self,
        latitude: float,
        longitude: float,
        is_synthetic_allowed: bool = False,
    ) -> RawDatasetObservation:
        """Fetch raw observation for a geographic coordinate point.

        Args:
            latitude: Decimal degrees [-90.0, 90.0]
            longitude: Decimal degrees [-180.0, 180.0]
            is_synthetic_allowed: If True, allow synthetic fallback if offline/out-of-bounds

        Returns:
            RawDatasetObservation containing provider payload and synthetic flag
        """
        pass

    @abstractmethod
    def normalize_and_validate(
        self,
        raw_obs: RawDatasetObservation,
    ) -> Tuple[Dict[str, Any], List[DataQualityCheck], Dict[str, VariableProvenance]]:
        """Clean, unit-convert, validate, and generate provenance for variables in this dataset.

        Args:
            raw_obs: Raw observation

        Returns:
            Tuple of:
            - canonical_values: Dict mapping variable paths (e.g. 'soil.ph') to normalized values
            - quality_checks: List of DataQualityCheck items
            - provenance: Dict mapping variable paths to VariableProvenance records
        """
        pass

    def health_check(self) -> Dict[str, Any]:
        """Perform operational check for this dataset adapter."""
        return {
            "dataset_id": self.dataset_id,
            "name": self.name,
            "status": "ready",
            "is_authoritative": self.metadata.is_authoritative,
        }
