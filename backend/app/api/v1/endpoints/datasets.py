"""API Endpoints for Authoritative Environmental Datasets & Ingestion Pipeline (Phase 7)."""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.schemas.dataset import (
    DatasetMetadata,
    RawDatasetObservation,
    PointQueryResult,
    StateEnrichmentRequest,
    StateEnrichmentResponse,
    DataQualityReport,
)
from backend.app.schemas.environmental_state import EnvironmentalState
from backend.app.datasets.manager import dataset_manager
from backend.app.datasets.pipeline import EnvironmentalDataPipeline
from backend.app.core.logging import logger

router = APIRouter()


@router.get(
    "/registry",
    response_model=List[DatasetMetadata],
    status_code=status.HTTP_200_OK,
    summary="List all authoritative environmental datasets",
    description="Retrieve registered datasets across Soil, Land, Biodiversity, Climate, and Human Impact domains.",
)
def list_datasets(
    db: Session = Depends(get_db),
) -> List[DatasetMetadata]:
    """Retrieve metadata for all authoritative environmental datasets."""
    # Ensure database registry is synced
    dataset_manager.seed_registry_db(db)
    return dataset_manager.list_datasets()


@router.get(
    "/registry/{dataset_id}",
    response_model=DatasetMetadata,
    status_code=status.HTTP_200_OK,
    summary="Get metadata for a specific environmental dataset",
)
def get_dataset(
    dataset_id: str,
) -> DatasetMetadata:
    """Retrieve dataset metadata, license, units, and limitations."""
    meta = dataset_manager.get_dataset(dataset_id)
    if not meta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Authoritative dataset '{dataset_id}' not found in registry.",
        )
    return meta


@router.post(
    "/query-point",
    response_model=PointQueryResult,
    status_code=status.HTTP_200_OK,
    summary="Query all authoritative datasets for a geographic point",
    description="Fetch and normalize real-world environmental data for coordinates across Soil, Land, Biodiversity, Climate, and Human Impact domains.",
)
def query_point(
    latitude: float = Query(..., ge=-90.0, le=90.0, description="Latitude coordinate [-90, 90]"),
    longitude: float = Query(..., ge=-180.0, le=180.0, description="Longitude coordinate [-180, 180]"),
    allow_synthetic: bool = Query(default=False, description="Allow synthetic fallback if out of reference bounds"),
    db: Session = Depends(get_db),
) -> PointQueryResult:
    """Query all 6 authoritative datasets for a coordinate point."""
    try:
        return dataset_manager.query_point(
            latitude=latitude,
            longitude=longitude,
            allow_synthetic=allow_synthetic,
            db_session=db,
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        logger.error(f"Error executing point query for ({latitude}, {longitude}): {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Environmental dataset point query failed: {exc}",
        )


@router.post(
    "/ingest",
    status_code=status.HTTP_200_OK,
    summary="Ingest and normalize raw dataset observation",
    description="Run raw sensor or external API observation through data cleaning, unit conversion, and quality checks.",
)
def ingest_observation(
    observation: RawDatasetObservation,
    region: Optional[str] = Query(default=None, description="Optional administrative region label"),
    ecosystem: Optional[str] = Query(default=None, description="Optional biome classification"),
    db: Session = Depends(get_db),
):
    """Process a raw observation through the ingestion pipeline."""
    adapter = dataset_manager.get_adapter(observation.dataset_id)
    if not adapter:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No adapter registered for dataset ID '{observation.dataset_id}'.",
        )

    try:
        state, quality_report, provenance = EnvironmentalDataPipeline.process_raw_observation(
            raw_obs=observation,
            adapter=adapter,
            db_session=db,
            region=region,
            ecosystem=ecosystem,
        )
        return {
            "status": "success",
            "is_valid": quality_report.is_valid,
            "canonical_state": state,
            "quality_report": quality_report,
            "provenance": provenance,
        }
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        logger.error(f"Ingestion pipeline failure: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Observation ingestion failed: {exc}",
        )


@router.post(
    "/enrich-state",
    response_model=StateEnrichmentResponse,
    status_code=status.HTTP_200_OK,
    summary="Enrich an EnvironmentalState with authoritative dataset values",
    description="Fill missing/null variables in an EnvironmentalState from real-world authoritative datasets while strictly preserving existing user measurements.",
)
def enrich_environmental_state(
    payload: StateEnrichmentRequest,
    db: Session = Depends(get_db),
) -> StateEnrichmentResponse:
    """Enrich an existing environmental profile state with authoritative dataset records."""
    try:
        return dataset_manager.enrich_state(payload, db_session=db)
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        logger.error(f"State enrichment failed: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Environmental state enrichment failed: {exc}",
        )
