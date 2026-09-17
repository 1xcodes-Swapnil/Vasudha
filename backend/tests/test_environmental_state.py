"""Comprehensive test suite for Phase 1: Canonical Environmental State & Data Model.

Covers:
- valid complete state
- valid partial state
- null vs zero
- invalid pH
- invalid rainfall
- invalid coordinates
- boundary coordinate values
- state updates (merge semantics)
- conflicting values (latest explicit override)
- missing fields
- malformed JSON and schema violations
- API endpoints (POST create, GET retrieve, PATCH update, POST validate)
"""

import pytest
from pydantic import ValidationError
from backend.app.schemas.environmental_state import (
    EnvironmentalState,
    SoilState,
    LandState,
    BiodiversityState,
    ClimateState,
    HumanImpactState,
    SpatialContext,
    EnvironmentalStateCreate,
    EnvironmentalStateUpdate,
)
from backend.app.models.environmental_state import EnvironmentalProfile


# ==============================================================================
# 1. VALID COMPLETE STATE TESTS
# ==============================================================================

def test_valid_complete_environmental_state():
    """Verify a complete state with all 15 scientific variables passes validation."""
    state_data = {
        "soil": {
            "ph": 6.8,
            "organic_carbon": 3.45,
            "moisture": 24.5,
        },
        "land": {
            "land_use": "agroforestry",
            "land_cover": "tropical_semi_evergreen",
        },
        "biodiversity": {
            "species_richness": 142,
            "habitat_diversity": 78.5,
        },
        "climate": {
            "temperature": 23.4,
            "rainfall": 1850.0,
        },
        "human_impact": {
            "pollution": 12.0,
            "deforestation": 5.2,
        },
        "spatial_context": {
            "latitude": 13.0827,
            "longitude": 80.2707,
            "region": "Western Ghats Foothills",
            "ecosystem": "Tropical Moist Broadleaf Forest",
        },
    }

    state = EnvironmentalState.model_validate(state_data)

    assert state.soil.ph == 6.8
    assert state.soil.organic_carbon == 3.45
    assert state.soil.moisture == 24.5
    assert state.land.land_use == "agroforestry"
    assert state.land.land_cover == "tropical_semi_evergreen"
    assert state.biodiversity.species_richness == 142
    assert state.biodiversity.habitat_diversity == 78.5
    assert state.climate.temperature == 23.4
    assert state.climate.rainfall == 1850.0
    assert state.human_impact.pollution == 12.0
    assert state.human_impact.deforestation == 5.2
    assert state.spatial_context.latitude == 13.0827
    assert state.spatial_context.longitude == 80.2707
    assert state.spatial_context.region == "Western Ghats Foothills"
    assert state.spatial_context.ecosystem == "Tropical Moist Broadleaf Forest"

    assert state.count_known_metrics() == 15
    assert not state.is_empty()


# ==============================================================================
# 2. VALID PARTIAL STATE TESTS
# ==============================================================================

def test_valid_partial_environmental_state():
    """Verify partial states where user provides only a subset of variables."""
    # Only soil pH and location provided
    state_data = {
        "soil": {"ph": 7.2},
        "spatial_context": {"latitude": 45.5, "longitude": -122.6},
    }
    state = EnvironmentalState.model_validate(state_data)

    assert state.soil.ph == 7.2
    assert state.soil.organic_carbon is None
    assert state.soil.moisture is None
    assert state.climate.rainfall is None
    assert state.climate.temperature is None
    assert state.spatial_context.latitude == 45.5
    assert state.spatial_context.longitude == -122.6
    assert state.count_known_metrics() == 3
    assert not state.is_empty()


# ==============================================================================
# 3. NULL VS ZERO TESTS
# ==============================================================================

def test_null_vs_zero_distinction():
    """Verify that null (None) means unknown, while 0/0.0 is an observed zero."""
    # State with explicit zero values
    state_zero = EnvironmentalState.model_validate({
        "soil": {"moisture": 0.0},
        "climate": {"rainfall": 0.0, "temperature": 0.0},
        "biodiversity": {"species_richness": 0},
        "human_impact": {"deforestation": 0.0, "pollution": 0.0},
    })

    assert state_zero.soil.moisture is not None
    assert state_zero.soil.moisture == 0.0
    assert state_zero.climate.rainfall is not None
    assert state_zero.climate.rainfall == 0.0
    assert state_zero.climate.temperature is not None
    assert state_zero.climate.temperature == 0.0
    assert state_zero.biodiversity.species_richness is not None
    assert state_zero.biodiversity.species_richness == 0
    assert state_zero.human_impact.deforestation == 0.0
    assert state_zero.human_impact.pollution == 0.0

    # State with null (unknown) values
    state_null = EnvironmentalState.model_validate({
        "soil": {"moisture": None},
        "climate": {"rainfall": None, "temperature": None},
        "biodiversity": {"species_richness": None},
        "human_impact": {"deforestation": None, "pollution": None},
    })

    assert state_null.soil.moisture is None
    assert state_null.climate.rainfall is None
    assert state_null.climate.temperature is None
    assert state_null.biodiversity.species_richness is None
    assert state_null.human_impact.deforestation is None
    assert state_null.human_impact.pollution is None

    # Merge behavior: 0.0 MUST overwrite previous positive value, but None MUST NOT
    base_state = EnvironmentalState.model_validate({
        "climate": {"rainfall": 1500.0, "temperature": 28.0},
        "biodiversity": {"species_richness": 50},
    })

    # Update with observed zero rainfall and omitted/None temperature
    merged = base_state.merge_update({
        "climate": {"rainfall": 0.0, "temperature": None},
    })

    # Rainfall is now 0.0 (observed zero overridden)
    assert merged.climate.rainfall == 0.0
    # Temperature 28.0 is preserved because update was None
    assert merged.climate.temperature == 28.0
    # Species richness 50 is preserved because not mentioned
    assert merged.biodiversity.species_richness == 50


# ==============================================================================
# 4. INVALID PH TESTS
# ==============================================================================

def test_invalid_ph_rejected():
    """Verify pH outside 0.0 - 14.0 is rejected with clear validation error."""
    # Negative pH
    with pytest.raises(ValidationError) as exc:
        SoilState(ph=-0.5)
    assert "Soil pH must be between 0.0 and 14.0" in str(exc.value)

    # Excessive pH
    with pytest.raises(ValidationError) as exc:
        SoilState(ph=14.5)
    assert "Soil pH must be between 0.0 and 14.0" in str(exc.value)

    with pytest.raises(ValidationError) as exc:
        SoilState(ph=20.0)
    assert "Soil pH must be between 0.0 and 14.0" in str(exc.value)


# ==============================================================================
# 5. INVALID RAINFALL TESTS
# ==============================================================================

def test_invalid_rainfall_rejected():
    """Verify negative or physically impossible rainfall is rejected."""
    # Negative rainfall
    with pytest.raises(ValidationError) as exc:
        ClimateState(rainfall=-10.0)
    assert "cannot be negative" in str(exc.value).lower()

    # Beyond terrestrial maximum
    with pytest.raises(ValidationError) as exc:
        ClimateState(rainfall=25000.0)
    assert "maximum recorded terrestrial precipitation" in str(exc.value)


# ==============================================================================
# 6. INVALID COORDINATES TESTS
# ==============================================================================

def test_invalid_coordinates_rejected():
    """Verify out-of-bounds latitude and longitude are rejected."""
    # Latitude > 90
    with pytest.raises(ValidationError) as exc:
        SpatialContext(latitude=90.1)
    assert "Latitude must be between -90.0 and 90.0" in str(exc.value)

    # Latitude < -90
    with pytest.raises(ValidationError) as exc:
        SpatialContext(latitude=-90.01)
    assert "Latitude must be between -90.0 and 90.0" in str(exc.value)

    # Longitude > 180
    with pytest.raises(ValidationError) as exc:
        SpatialContext(longitude=180.5)
    assert "Longitude must be between -180.0 and 180.0" in str(exc.value)

    # Longitude < -180
    with pytest.raises(ValidationError) as exc:
        SpatialContext(longitude=-181.0)
    assert "Longitude must be between -180.0 and 180.0" in str(exc.value)


# ==============================================================================
# 7. BOUNDARY COORDINATE VALUES TESTS
# ==============================================================================

def test_boundary_coordinate_values():
    """Verify exact boundary values for latitude (-90, 90, 0) and longitude (-180, 180, 0)."""
    # North Pole boundary
    sc1 = SpatialContext(latitude=90.0, longitude=180.0)
    assert sc1.latitude == 90.0
    assert sc1.longitude == 180.0

    # South Pole boundary
    sc2 = SpatialContext(latitude=-90.0, longitude=-180.0)
    assert sc2.latitude == -90.0
    assert sc2.longitude == -180.0

    # Equator & Prime Meridian
    sc3 = SpatialContext(latitude=0.0, longitude=0.0)
    assert sc3.latitude == 0.0
    assert sc3.longitude == 0.0


# ==============================================================================
# 8. STATE UPDATES & NON-DESTRUCTIVE MERGE TESTS
# ==============================================================================

def test_state_updates_merge_preserves_unmentioned_fields():
    """Verify updating a state does not erase previously known values."""
    initial = EnvironmentalState.model_validate({
        "soil": {"ph": 6.2, "organic_carbon": 2.1, "moisture": 18.0},
        "land": {"land_use": "pasture", "land_cover": "grassland"},
        "climate": {"rainfall": 900.0, "temperature": 19.5},
    })

    # Update only soil pH and add region
    update_data = {
        "soil": {"ph": 6.5},
        "spatial_context": {"region": "Southern Highlands"},
    }

    updated = initial.merge_update(update_data)

    # Updated fields
    assert updated.soil.ph == 6.5
    assert updated.spatial_context.region == "Southern Highlands"

    # Preserved fields
    assert updated.soil.organic_carbon == 2.1
    assert updated.soil.moisture == 18.0
    assert updated.land.land_use == "pasture"
    assert updated.land.land_cover == "grassland"
    assert updated.climate.rainfall == 900.0
    assert updated.climate.temperature == 19.5


# ==============================================================================
# 9. CONFLICTING VALUES (LATEST EXPLICIT OVERRIDE) TESTS
# ==============================================================================

def test_conflicting_values_override_rule():
    """Verify latest explicit user value overrides the older value."""
    state = EnvironmentalState.model_validate({
        "soil": {"ph": 5.0},
        "biodiversity": {"species_richness": 12},
    })

    # Conflict: new pH = 7.4, new species_richness = 85
    updated = state.merge_update({
        "soil": {"ph": 7.4},
        "biodiversity": {"species_richness": 85},
    })

    assert updated.soil.ph == 7.4
    assert updated.biodiversity.species_richness == 85


# ==============================================================================
# 10. MISSING FIELDS TESTS
# ==============================================================================

def test_missing_fields_default_to_empty():
    """Verify an empty EnvironmentalState defaults all fields cleanly to None."""
    empty_state = EnvironmentalState()
    assert empty_state.is_empty()
    assert empty_state.count_known_metrics() == 0
    assert empty_state.soil.ph is None
    assert empty_state.climate.rainfall is None
    assert empty_state.spatial_context.latitude is None


# ==============================================================================
# 11. MALFORMED JSON AND EXTRA FIELDS TESTS
# ==============================================================================

def test_extra_fields_forbidden():
    """Verify arbitrary unrecognized fields are rejected (extra='forbid')."""
    with pytest.raises(ValidationError):
        SoilState.model_validate({"ph": 6.5, "unrecognized_chemical": 99.9})

    with pytest.raises(ValidationError):
        EnvironmentalState.model_validate({"unknown_domain": {"data": 123}})


def test_type_coercion_invalid_types_rejected():
    """Verify non-numeric strings for numeric metrics raise validation errors."""
    with pytest.raises(ValidationError):
        SoilState.model_validate({"ph": "very_acidic"})

    with pytest.raises(ValidationError):
        ClimateState.model_validate({"rainfall": "moderate_rain"})


# ==============================================================================
# 12. API ENDPOINTS INTEGRATION TESTS
# ==============================================================================

def test_api_create_and_get_environmental_state(client):
    """Test POST /api/v1/environmental-state and GET /{id}."""
    payload = {
        "name": "Boreal Peatland Site 1",
        "description": "Sub-arctic wetland baseline measurement",
        "state": {
            "soil": {"ph": 4.5, "organic_carbon": 42.0, "moisture": 85.0},
            "climate": {"temperature": 3.5, "rainfall": 650.0},
            "spatial_context": {
                "latitude": 60.5,
                "longitude": 25.0,
                "region": "Fennoscandia",
                "ecosystem": "Boreal Peatland",
            },
        },
    }

    # 1. Create profile
    res_create = client.post("/api/v1/environmental-state", json=payload)
    assert res_create.status_code == 201
    data = res_create.json()

    assert "id" in data
    profile_id = data["id"]
    assert data["name"] == "Boreal Peatland Site 1"
    assert data["metrics_count"] == 9
    assert data["state"]["soil"]["ph"] == 4.5
    assert data["state"]["spatial_context"]["latitude"] == 60.5

    # 2. Retrieve profile
    res_get = client.get(f"/api/v1/environmental-state/{profile_id}")
    assert res_get.status_code == 200
    retrieved = res_get.json()
    assert retrieved["id"] == profile_id
    assert retrieved["state"]["soil"]["organic_carbon"] == 42.0
    assert retrieved["state"]["climate"]["temperature"] == 3.5


def test_api_patch_environmental_state(client):
    """Test PATCH /api/v1/environmental-state/{id} with partial merge semantics."""
    # 1. Create initial profile
    initial_payload = {
        "name": "Arid Grassland Plot",
        "state": {
            "soil": {"ph": 7.8, "moisture": 5.0},
            "climate": {"rainfall": 250.0},
        },
    }
    create_res = client.post("/api/v1/environmental-state", json=initial_payload)
    assert create_res.status_code == 201
    profile_id = create_res.json()["id"]

    # 2. Patch with observed zero rainfall and new biodiversity richness
    patch_payload = {
        "climate": {"rainfall": 0.0},
        "biodiversity": {"species_richness": 18},
    }
    patch_res = client.patch(f"/api/v1/environmental-state/{profile_id}", json=patch_payload)
    assert patch_res.status_code == 200
    patched = patch_res.json()

    # Rainfall overwritten to 0.0
    assert patched["state"]["climate"]["rainfall"] == 0.0
    # Species richness added
    assert patched["state"]["biodiversity"]["species_richness"] == 18
    # Soil ph and moisture preserved
    assert patched["state"]["soil"]["ph"] == 7.8
    assert patched["state"]["soil"]["moisture"] == 5.0


def test_api_validate_endpoint_valid_and_invalid(client):
    """Test POST /api/v1/environmental-state/validate pure validator."""
    # Valid payload
    valid_res = client.post(
        "/api/v1/environmental-state/validate",
        json={"soil": {"ph": 6.5}, "climate": {"rainfall": 800.0}},
    )
    assert valid_res.status_code == 200
    assert valid_res.json()["valid"] is True
    assert valid_res.json()["metrics_count"] == 2

    # Invalid payload (pH = 18.0)
    invalid_res = client.post(
        "/api/v1/environmental-state/validate",
        json={"soil": {"ph": 18.0}},
    )
    assert invalid_res.status_code == 422


def test_api_get_nonexistent_profile_returns_404(client):
    """Test GET with unknown UUID returns 404."""
    res = client.get("/api/v1/environmental-state/non-existent-uuid-1234")
    assert res.status_code == 404
