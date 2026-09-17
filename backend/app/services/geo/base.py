"""Abstract base class for Geographic Context Providers (Phase 2).

This abstraction guarantees that the intelligence and recommendation layers
are decoupled from any specific GIS vendor, remote sensing provider, or external API.
Providers can be local rule-based, NASA EarthData, Copernicus, ESA WorldCover,
OpenStreetMap, or proprietary enterprise spatial engines.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from backend.app.schemas.geo import GeoContextResult


class GeoContextProvider(ABC):
    """Abstract interface for resolving geographic and ecosystem context from coordinates."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Unique identifier for this geospatial provider."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Human-readable description of provider and data source."""
        pass

    @property
    def requires_api_key(self) -> bool:
        """Whether this provider requires external credentials."""
        return False

    @abstractmethod
    def lookup(self, latitude: float, longitude: float) -> GeoContextResult:
        """Resolve geographic region, ecosystem, biome, and spatial properties for coordinates.

        Args:
            latitude: Decimal degrees [-90.0, 90.0]
            longitude: Decimal degrees [-180.0, 180.0]

        Returns:
            GeoContextResult containing region, ecosystem, confidence, and degradation flags.

        Raises:
            ValueError: If coordinates are out of bounds.
            RuntimeError: If provider fails or external service is unreachable.
        """
        pass

    def health_check(self) -> Dict[str, Any]:
        """Perform a readiness check on the provider."""
        return {
            "name": self.name,
            "status": "ready",
            "requires_api_key": self.requires_api_key,
        }

    def enrich_external_datasets(
        self, latitude: float, longitude: float
    ) -> Dict[str, Any]:
        """Future extension point for land-cover, canopy height, and climate rasters.

        Returns an empty dictionary by default until future Phase datasets are linked.
        """
        return {}
