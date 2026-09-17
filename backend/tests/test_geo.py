"""Comprehensive Unit and Integration Tests for Phase 2: Geographic Context & Map Enrichment."""

import pytest
from backend.app.schemas.geo import GeoLookupRequest, GeoContextResult, GeoStateSyncRequest
from backend.app.schemas.environmental_state import EnvironmentalState, SoilState, ClimateState, SpatialContext
from backend.app.services.geo.rule_based_provider import RuleBasedGeoContextProvider
from backend.app.services.geo.failing_provider import FailingGeoContextProvider
from backend.app.services.geo.manager import (
    resolve_geo_context,
    update_environmental_state_spatial_context,
    register_geo_provider,
    set_geo_provider,
    get_geo_provider,
    list_geo_providers,
)


# ==============================================================================
# 1. PROVIDER UNIT TESTS: VALID COORDINATES & BIOME ASSIGNMENTS
# ==============================================================================

def test_rule_based_provider_western_ghats():
    """Verify known high-biodiversity region resolves accurate ecoregion."""
    provider = RuleBasedGeoContextProvider()
    # Coordinates in Western Ghats, India (e.g. Wayanad / Kudremukh)
    res = provider.lookup(latitude=12.5, longitude=75.5)
    assert res.latitude == 12.5
    assert res.longitude == 75.5
    assert res.region == "Western Ghats"
    assert "Tropical Moist Broadleaf" in res.ecosystem
    assert res.biome_code == "TMBF_WG"
    assert res.confidence >= 0.9
    assert res.degraded is False


def test_rule_based_provider_amazon_basin():
    """Verify Amazon Basin coordinates."""
    provider = RuleBasedGeoContextProvider()
    res = provider.lookup(latitude=-3.4, longitude=-62.2)
    assert res.region == "Amazon Basin"
    assert "Rainforest" in res.ecosystem
    assert res.degraded is False


def test_rule_based_provider_fennoscandia_boreal():
    """Verify Boreal Fennoscandian peatland coordinates."""
    provider = RuleBasedGeoContextProvider()
    res = provider.lookup(latitude=61.0, longitude=24.0)
    assert res.region == "Fennoscandia"
    assert "Boreal" in res.ecosystem


def test_rule_based_provider_latitudinal_fallback():
    """Verify general latitudinal fallback for coordinates outside explicit bounding boxes."""
    provider = RuleBasedGeoContextProvider()
    # Subtropical coordinate in central China / ocean edge
    res = provider.lookup(latitude=28.0, longitude=115.0)
    assert "Subtropical" in res.region or "Subtropical" in res.ecosystem
    assert res.confidence > 0.5


# ==============================================================================
# 2. VALIDATION: INVALID AND BOUNDARY COORDINATES
# ==============================================================================

def test_invalid_latitude_rejected_by_schema():
    """Latitude > 90 or < -90 must raise validation error."""
    with pytest.raises(ValueError):
        GeoLookupRequest(latitude=90.0001, longitude=0.0)

    with pytest.raises(ValueError):
        GeoLookupRequest(latitude=-95.0, longitude=0.0)


def test_invalid_longitude_rejected_by_schema():
    """Longitude > 180 or < -180 must raise validation error."""
    with pytest.raises(ValueError):
        GeoLookupRequest(latitude=0.0, longitude=180.5)

    with pytest.raises(ValueError):
        GeoLookupRequest(latitude=0.0, longitude=-190.0)


def test_boundary_coordinates_accepted():
    """Exact boundary coordinates (±90 lat, ±180 lon) must be valid."""
    req_north = GeoLookupRequest(latitude=90.0, longitude=180.0)
    assert req_north.latitude == 90.0
    assert req_north.longitude == 180.0

    req_south = GeoLookupRequest(latitude=-90.0, longitude=-180.0)
    assert req_south.latitude == -90.0
    assert req_south.longitude == -180.0


# ==============================================================================
# 3. SELECTING, UPDATING, AND CLEARING A LOCATION IN ENVIRONMENTAL STATE
# ==============================================================================

def test_environmental_state_spatial_update_preserves_other_metrics():
    """Selecting a new location must update spatial_context without altering soil/climate."""
    initial_state = EnvironmentalState(
        soil=SoilState(ph=6.5, organic_carbon=28.0, moisture=22.5),
        climate=ClimateState(temperature=24.0, rainfall=1200.0),
        spatial_context=SpatialContext(latitude=None, longitude=None),
    )

    # 1. Update location (select pin in Western Ghats)
    updated_state = update_environmental_state_spatial_context(
        state=initial_state,
        latitude=13.0,
        longitude=75.6,
        auto_enrich=True,
    )

    # Spatial context updated and auto-enriched
    assert updated_state.spatial_context.latitude == 13.0
    assert updated_state.spatial_context.longitude == 75.6
    assert updated_state.spatial_context.region == "Western Ghats"

    # Soil and climate metrics are completely intact
    assert updated_state.soil.ph == 6.5
    assert updated_state.soil.organic_carbon == 28.0
    assert updated_state.soil.moisture == 22.5
    assert updated_state.climate.temperature == 24.0
    assert updated_state.climate.rainfall == 1200.0


def test_environmental_state_update_location():
    """Updating location from one set of coordinates to another."""
    state_v1 = EnvironmentalState(
        soil=SoilState(ph=7.0),
        spatial_context=SpatialContext(latitude=12.0, longitude=75.0, region="Western Ghats"),
    )

    # Update to Fennoscandia
    state_v2 = update_environmental_state_spatial_context(
        state=state_v1,
        latitude=60.5,
        longitude=25.0,
        auto_enrich=True,
    )

    assert state_v2.spatial_context.latitude == 60.5
    assert state_v2.spatial_context.longitude == 25.0
    assert state_v2.spatial_context.region == "Fennoscandia"
    # Soil remains unchanged
    assert state_v2.soil.ph == 7.0


def test_environmental_state_clear_location():
    """Clearing location resets spatial coordinates to None while preserving ecological metrics."""
    state_with_loc = EnvironmentalState(
        soil=SoilState(ph=5.8, organic_carbon=19.4),
        climate=ClimateState(temperature=18.0),
        spatial_context=SpatialContext(
            latitude=45.0,
            longitude=10.0,
            region="Mediterranean Basin",
            ecosystem="Mediterranean Scrub",
        ),
    )

    cleared_state = update_environmental_state_spatial_context(
        state=state_with_loc,
        clear_location=True,
    )

    # Coordinates and ecosystem cleared
    assert cleared_state.spatial_context.latitude is None
    assert cleared_state.spatial_context.longitude is None
    assert cleared_state.spatial_context.region is None
    assert cleared_state.spatial_context.ecosystem is None

    # Soil and Climate metrics strictly preserved
    assert cleared_state.soil.ph == 5.8
    assert cleared_state.soil.organic_carbon == 19.4
    assert cleared_state.climate.temperature == 18.0


# ==============================================================================
# 4. MISSING GEO INFORMATION & GRACEFUL DEGRADATION ON PROVIDER FAILURE
# ==============================================================================

def test_missing_geo_information_defaults_to_none():
    """State created without geo coordinates has all spatial attributes as None."""
    state = EnvironmentalState(soil=SoilState(ph=6.0))
    assert state.spatial_context.latitude is None
    assert state.spatial_context.longitude is None
    assert state.spatial_context.region is None
    assert state.spatial_context.ecosystem is None


def test_geo_provider_failure_graceful_degradation():
    """When a geo provider fails, coordinates are preserved and region/ecosystem marked as None."""
    failing_provider = FailingGeoContextProvider()
    register_geo_provider(failing_provider)

    try:
        # Resolve using failing provider
        result = resolve_geo_context(
            latitude=21.0,
            longitude=78.0,
            provider_name="mock_failing_provider",
            allow_degraded=True,
        )

        # Coordinates preserved
        assert result.latitude == 21.0
        assert result.longitude == 78.0
        # Region and ecosystem marked as None (unknown)
        assert result.region is None
        assert result.ecosystem is None
        assert result.confidence == 0.0
        assert result.degraded is True
    finally:
        # Reset active provider
        set_geo_provider("rule_based_local")


# ==============================================================================
# 5. API INTEGRATION TESTS (LOOKUP, SYNC-STATE, PROVIDERS)
# ==============================================================================

def test_api_geo_lookup_success(client):
    """POST /api/v1/geo/lookup returns 200 with resolved context."""
    res = client.post("/api/v1/geo/lookup", json={"latitude": 12.97, "longitude": 77.59})
    assert res.status_code == 200
    data = res.json()
    assert data["latitude"] == 12.97
    assert data["longitude"] == 77.59
    assert data["region"] is not None
    assert data["ecosystem"] is not None
    assert data["degraded"] is False


def test_api_geo_lookup_invalid_coordinates(client):
    """POST /api/v1/geo/lookup with latitude > 90 returns 422."""
    res = client.post("/api/v1/geo/lookup", json={"latitude": 95.0, "longitude": 10.0})
    assert res.status_code == 422

    res2 = client.post("/api/v1/geo/lookup", json={"latitude": 10.0, "longitude": -195.0})
    assert res2.status_code == 422


def test_api_geo_sync_state_and_clear(client):
    """POST /api/v1/geo/sync-state modifies spatial context and clear works."""
    payload = {
        "state": {
            "soil": {"ph": 6.2, "moisture": 18.0},
            "climate": {"rainfall": 950.0},
        },
        "latitude": 13.0,
        "longitude": 75.5,
        "auto_enrich": True,
        "clear_location": False,
    }

    res = client.post("/api/v1/geo/sync-state", json=payload)
    assert res.status_code == 200
    body = res.json()
    assert body["spatial_context"]["latitude"] == 13.0
    assert body["spatial_context"]["longitude"] == 75.5
    assert body["spatial_context"]["region"] == "Western Ghats"
    # Metrics count includes soil (2) + climate (1) + spatial (4) = 7
    assert body["metrics_count"] >= 5

    # Now clear location via API
    clear_payload = {
        "state": body["state"],
        "clear_location": True,
    }
    clear_res = client.post("/api/v1/geo/sync-state", json=clear_payload)
    assert clear_res.status_code == 200
    cleared_body = clear_res.json()
    assert cleared_body["spatial_context"]["latitude"] is None
    assert cleared_body["spatial_context"]["longitude"] is None
    # Soil remains intact
    assert cleared_body["state"]["soil"]["ph"] == 6.2
    assert cleared_body["state"]["soil"]["moisture"] == 18.0


def test_api_geo_list_providers(client):
    """GET /api/v1/geo/providers returns list of registered providers."""
    res = client.get("/api/v1/geo/providers")
    assert res.status_code == 200
    providers = res.json()
    assert len(providers) >= 1
    assert any(p["name"] == "rule_based_local" for p in providers)
