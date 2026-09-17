"""Adapters package for Authoritative Environmental Datasets (Phase 7)."""

from backend.app.datasets.adapters.soilgrids_adapter import SoilGridsAdapter
from backend.app.datasets.adapters.copernicus_adapter import CopernicusLandCoverAdapter
from backend.app.datasets.adapters.gbif_adapter import GBIFBiodiversityAdapter
from backend.app.datasets.adapters.worldclim_adapter import WorldClimClimateAdapter
from backend.app.datasets.adapters.gfw_adapter import GlobalForestWatchAdapter
from backend.app.datasets.adapters.unep_adapter import UNEPPollutionAdapter

__all__ = [
    "SoilGridsAdapter",
    "CopernicusLandCoverAdapter",
    "GBIFBiodiversityAdapter",
    "WorldClimClimateAdapter",
    "GlobalForestWatchAdapter",
    "UNEPPollutionAdapter",
]
