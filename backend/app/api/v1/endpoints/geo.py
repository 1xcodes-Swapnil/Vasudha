"""API endpoints for Geographic Context & Spatial Resolution (Phase 2)."""

from typing import List
from fastapi import APIRouter, HTTPException, status
from backend.app.schemas.geo import (
    GeoLookupRequest,
    GeoContextResult,
    GeoStateSyncRequest,
    GeoStateSyncResponse,
    GeoProviderInfo,
)
from backend.app.services.geo.manager import (
    resolve_geo_context,
    update_environmental_state_spatial_context,
    list_geo_providers,
    set_geo_provider,
)
from backend.app.core.logging import logger

router = APIRouter()


@router.post(
    "/lookup",
    response_model=GeoContextResult,
    status_code=status.HTTP_200_OK,
    summary="Resolve geographic context from coordinates",
    description="Look up region, ecosystem, and biome from decimal latitude/longitude coordinates.",
)
def lookup_geographic_context(payload: GeoLookupRequest) -> GeoContextResult:
    """Resolve spatial context with graceful degradation if provider is unavailable."""
    try:
        return resolve_geo_context(
            latitude=payload.latitude,
            longitude=payload.longitude,
            allow_degraded=True,
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        logger.error(f"Unexpected error in geo lookup: {exc}")
        # Return fallback preserved coordinates with unknown region/ecosystem
        return GeoContextResult(
            latitude=payload.latitude,
            longitude=payload.longitude,
            region=None,
            ecosystem=None,
            confidence=0.0,
            provider_name="emergency_fallback",
            degraded=True,
        )


@router.post(
    "/sync-state",
    response_model=GeoStateSyncResponse,
    status_code=status.HTTP_200_OK,
    summary="Synchronize spatial context into EnvironmentalState",
    description="Update coordinates, region, and ecosystem in an EnvironmentalState without altering other metrics.",
)
def sync_spatial_to_state(payload: GeoStateSyncRequest) -> GeoStateSyncResponse:
    """Update or clear spatial context within an EnvironmentalState."""
    try:
        updated_state = update_environmental_state_spatial_context(
            state=payload.state,
            latitude=payload.latitude,
            longitude=payload.longitude,
            region=payload.region,
            ecosystem=payload.ecosystem,
            auto_enrich=payload.auto_enrich,
            clear_location=payload.clear_location,
        )

        metrics_count = updated_state.count_known_metrics()
        status_msg = "cleared" if payload.clear_location else "enriched"

        return GeoStateSyncResponse(
            state=updated_state,
            spatial_context=updated_state.spatial_context,
            metrics_count=metrics_count,
            enrichment_status=status_msg,
            provider="geo_manager",
        )
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(val_err),
        )
    except Exception as exc:
        logger.error(f"Failed to sync spatial context to state: {exc}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Spatial state synchronization failed: {exc}",
        )


@router.get(
    "/providers",
    response_model=List[GeoProviderInfo],
    summary="List available geospatial providers",
)
def get_providers() -> List[GeoProviderInfo]:
    """List registered GeoContextProviders and operational statuses."""
    return list_geo_providers()


@router.post(
    "/providers/switch",
    status_code=status.HTTP_200_OK,
    summary="Switch active geospatial provider",
)
def switch_active_provider(name: str):
    """Switch the current active GeoContextProvider."""
    try:
        set_geo_provider(name)
        return {"status": "success", "active_provider": name}
    except ValueError as val_err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(val_err),
        )
