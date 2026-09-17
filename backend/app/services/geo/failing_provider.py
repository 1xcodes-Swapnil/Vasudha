"""Simulated failing or unavailable geospatial service provider.

Used specifically for testing error handling and verifying that the
system degrades gracefully when external geospatial APIs encounter outages.
"""

from backend.app.services.geo.base import GeoContextProvider
from backend.app.schemas.geo import GeoContextResult


class FailingGeoContextProvider(GeoContextProvider):
    """Provider that simulates network timeout or external GIS service failure."""

    @property
    def name(self) -> str:
        return "mock_failing_provider"

    @property
    def description(self) -> str:
        return "Simulated unreachable external geospatial provider for resilience testing."

    def lookup(self, latitude: float, longitude: float) -> GeoContextResult:
        """Simulate an external API timeout or connection failure."""
        raise RuntimeError("Geospatial satellite upstream service timed out (simulated outage).")

    def health_check(self) -> dict:
        return {
            "name": self.name,
            "status": "outage",
            "error": "Upstream service unreachable",
        }
