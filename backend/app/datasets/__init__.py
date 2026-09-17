"""Authoritative Environmental Dataset Layer (Phase 7)."""

from backend.app.datasets.metadata import AUTHORITATIVE_DATASETS
from backend.app.datasets.base_adapter import DatasetAdapter
from backend.app.datasets.pipeline import EnvironmentalDataPipeline
from backend.app.datasets.manager import EnvironmentalDatasetManager, dataset_manager

__all__ = [
    "AUTHORITATIVE_DATASETS",
    "DatasetAdapter",
    "EnvironmentalDataPipeline",
    "EnvironmentalDatasetManager",
    "dataset_manager",
]
