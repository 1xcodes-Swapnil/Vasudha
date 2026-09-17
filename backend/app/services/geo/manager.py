"""Geographic Context Provider Registry and Orchestration Manager.

Handles provider selection, resilience fallback, and EnvironmentalState integration.
"""

from typing import Dict, Any, List, Optional
from backend.app.core.logging import logger
from backend.app.services.geo.base import GeoContextProvider
from backend.app.services.geo.rule_based_provider import RuleBasedGeoContextProvider
from backend.app.schemas.geo import GeoContextResult, GeoProviderInfo
from backend.app.schemas.environmental_state import EnvironmentalState, SpatialContext

# In-memory registry of available GeoContextProviders
_REGISTERED_PROVIDERS: Dict[str, GeoContextProvider] = {
    "rule_based_local": RuleBasedGeoContextProvider(),
}

# Current active provider
_ACTIVE_PROVIDER_NAME: str = "rule_based_local"


def get_geo_provider(name: Optional[str] = None) -> GeoContextProvider:
    """Retrieve requested or default active GeoContextProvider."""
    target = name or _ACTIVE_PROVIDER_NAME
    if target not in _REGISTERED_PROVIDERS:
        logger.warning(f"Requested geo provider '{target}' not registered. Using 'rule_based_local'.")
        return _REGISTERED_PROVIDERS["rule_based_local"]
    return _REGISTERED_PROVIDERS[target]


def register_geo_provider(provider: GeoContextProvider) -> None:
    """Register a new GeoContextProvider (e.g. future EarthData/Copernicus)."""
    _REGISTERED_PROVIDERS[provider.name] = provider
    logger.info(f"Registered new GeoContextProvider: '{provider.name}'")


def set_geo_provider(name: str) -> None:
    """Set the system-wide active GeoContextProvider."""
    global _ACTIVE_PROVIDER_NAME
    if name not in _REGISTERED_PROVIDERS:
        raise ValueError(f"Provider '{name}' is not registered. Available: {list(_REGISTERED_PROVIDERS.keys())}")
    _ACTIVE_PROVIDER_NAME = name
    logger.info(f"Active GeoContextProvider switched to: '{name}'")


def list_geo_providers() -> List[GeoProviderInfo]:
    """List all registered providers and their operational status."""
    results = []
    for name, provider in _REGISTERED_PROVIDERS.items():
        is_active = (name == _ACTIVE_PROVIDER_NAME)
        health = provider.health_check()
        results.append(
            GeoProviderInfo(
                name=name,
                description=provider.description,
                is_active=is_active,
                requires_api_key=provider.requires_api_key,
                status=health.get("status", "unknown"),
                capabilities={"enrich_datasets": True},
            )
        )
    return results


def resolve_geo_context(
    latitude: float,
    longitude: float,
    provider_name: Optional[str] = None,
    allow_degraded: bool = True,
) -> GeoContextResult:
    """Resolve geographic and ecosystem context with automatic graceful degradation.

    If the active provider fails, this returns the preserved coordinates with
    region and ecosystem marked as None (unknown), rather than terminating execution.
    """
    if latitude < -90.0 or latitude > 90.0:
        raise ValueError(f"Latitude coordinate {latitude} is outside valid [-90.0, 90.0] range")
    if longitude < -180.0 or longitude > 180.0:
        raise ValueError(f"Longitude coordinate {longitude} is outside valid [-180.0, 180.0] range")

    provider = get_geo_provider(provider_name)

    try:
        result = provider.lookup(latitude, longitude)
        return result
    except Exception as exc:
        logger.warning(f"GeoContextProvider '{provider.name}' failed during lookup({latitude}, {longitude}): {exc}")
        if not allow_degraded:
            raise exc

        # Graceful degradation: preserve coordinates, mark region/ecosystem as unknown
        return GeoContextResult(
            latitude=latitude,
            longitude=longitude,
            region=None,
            ecosystem=None,
            biome_code=None,
            confidence=0.0,
            provider_name=provider.name,
            degraded=True,
        )


def update_environmental_state_spatial_context(
    state: EnvironmentalState,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
    region: Optional[str] = None,
    ecosystem: Optional[str] = None,
    auto_enrich: bool = True,
    clear_location: bool = False,
) -> EnvironmentalState:
    """Non-destructively updates the spatial context of an EnvironmentalState.

    Strictly preserves all other ecological indicators (soil, land, biodiversity,
    climate, human_impact). If clearing, resets spatial coordinates to None.
    If auto-enriching with coordinates, resolves region and ecosystem if not explicitly passed.
    """
    # Create a clone of the state to avoid mutating input directly
    updated_dict = state.model_dump()

    if clear_location:
        # Clear spatial context completely
        updated_dict["spatial_context"] = {
            "latitude": None,
            "longitude": None,
            "region": None,
            "ecosystem": None,
        }
        return EnvironmentalState(**updated_dict)

    # If coordinates provided
    resolved_region = region
    resolved_ecosystem = ecosystem

    if latitude is not None and longitude is not None:
        if auto_enrich and (not resolved_region or not resolved_ecosystem):
            geo_res = resolve_geo_context(latitude, longitude, allow_degraded=True)
            if not resolved_region:
                resolved_region = geo_res.region
            if not resolved_ecosystem:
                resolved_ecosystem = geo_res.ecosystem

    current_spatial = updated_dict.get("spatial_context", {})
    new_spatial = {
        "latitude": latitude if latitude is not None else current_spatial.get("latitude"),
        "longitude": longitude if longitude is not None else current_spatial.get("longitude"),
        "region": resolved_region if resolved_region is not None else current_spatial.get("region"),
        "ecosystem": resolved_ecosystem if resolved_ecosystem is not None else current_spatial.get("ecosystem"),
    }

    updated_dict["spatial_context"] = new_spatial
    return EnvironmentalState(**updated_dict)
