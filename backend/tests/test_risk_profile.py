"""Comprehensive tests for Phase 6 Nature Risk Profile Diagnostic Engine & API."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.knowledge.risk_engine import (
    NatureRiskProfileEngine,
    get_risk_engine,
)
from backend.app.schemas.environmental_state import (
    BiodiversityState,
    ClimateState,
    EnvironmentalState,
    HumanImpactState,
    LandState,
    SoilState,
    SpatialContext,
)
from backend.app.schemas.risk_profile import (
    NatureRiskProfile,
    RiskDimension,
    RiskLevel,
)
from backend.app.schemas.knowledge import EvidenceStrength

client = TestClient(app)


# ==============================================================================
# 1. COMPLETE ENVIRONMENTAL STATE TEST (MULTI-DIMENSION DIAGNOSIS)
# ==============================================================================

def test_complete_state_risk_profile_diagnosis():
    """Verifies that a complete state with severe conditions triggers High risk on relevant dimensions."""
    engine = get_risk_engine()
    state = EnvironmentalState(
        soil=SoilState(ph=5.1, organic_carbon=1.2, moisture=14.0),
        land=LandState(land_use="monoculture", land_cover="fragmented_canopy"),
        biodiversity=BiodiversityState(species_richness=22, habitat_diversity=25.0),
        climate=ClimateState(temperature=33.5, rainfall=480.0),
        human_impact=HumanImpactState(pollution=28.0, deforestation=14.0),
        spatial_context=SpatialContext(latitude=15.3, longitude=75.1, ecosystem="tropical_dry_forest", region="Western Ghats"),
    )

    profile = engine.diagnose_risk_profile(state)
    assert isinstance(profile, NatureRiskProfile)

    # 1. Water Stress -> High (Rainfall 480mm < 600, Moisture 14% < 20, Temp 33.5 > 29)
    assert profile.water_stress.level == RiskLevel.HIGH
    assert len(profile.water_stress.contributing_metrics) >= 3
    assert len(profile.water_stress.evidence_chunks) > 0
    assert profile.water_stress.explainability_chain is not None
    assert len(profile.water_stress.explainability_chain.steps) == 5

    # 2. Habitat Pressure -> High (Monoculture + fragmented canopy + defor 14%)
    assert profile.habitat_pressure.level == RiskLevel.HIGH
    assert "land.land_use" in profile.habitat_pressure.contributing_metrics
    assert len(profile.habitat_pressure.evidence_chunks) > 0

    # 3. Biodiversity Pressure -> High (Species richness 22 + diversity 25%)
    assert profile.biodiversity_pressure.level == RiskLevel.HIGH
    assert "biodiversity.species_richness" in profile.biodiversity_pressure.contributing_metrics

    # 4. Climate Exposure -> High (Temp 33.5C + rainfall 480mm)
    assert profile.climate_exposure.level == RiskLevel.HIGH

    # 5. Human Disturbance -> High (Pollution 28.0 + defor 14.0%)
    assert profile.human_disturbance.level == RiskLevel.HIGH

    # Evidence summary and limitations
    assert len(profile.evidence_summary) > 0
    assert len(profile.overall_limitations) > 0
    assert len(profile.missing_important_variables) == 0  # complete state


# ==============================================================================
# 2. PRISTINE BASELINE SCENARIO (NO PRESSURES / ALL LOW)
# ==============================================================================

def test_pristine_baseline_risk_profile():
    """Verifies that an optimal, well-managed ecosystem produces Low risk across all dimensions."""
    engine = get_risk_engine()
    state = EnvironmentalState(
        soil=SoilState(ph=6.8, organic_carbon=4.5, moisture=32.0),
        land=LandState(land_use="agroforestry", land_cover="continuous_canopy"),
        biodiversity=BiodiversityState(species_richness=95, habitat_diversity=78.0),
        climate=ClimateState(temperature=22.0, rainfall=1400.0),
        human_impact=HumanImpactState(pollution=2.0, deforestation=0.5),
        spatial_context=SpatialContext(latitude=10.0, longitude=76.0, ecosystem="tropical_wet_evergreen"),
    )

    profile = engine.diagnose_risk_profile(state)

    assert profile.water_stress.level == RiskLevel.LOW
    assert profile.habitat_pressure.level == RiskLevel.LOW
    assert profile.biodiversity_pressure.level == RiskLevel.LOW
    assert profile.climate_exposure.level == RiskLevel.LOW
    assert profile.human_disturbance.level == RiskLevel.LOW


# ==============================================================================
# 3. UNKNOWN / MISSING CONDITIONS (DISTINCTION FROM ZERO)
# ==============================================================================

def test_unknown_metrics_handling():
    """Verifies that completely missing domains evaluate to Unknown, not assumed Low or Zero."""
    engine = get_risk_engine()
    state = EnvironmentalState(
        soil=SoilState(ph=None, organic_carbon=None, moisture=None),
        land=LandState(land_use=None, land_cover=None),
        biodiversity=BiodiversityState(species_richness=None, habitat_diversity=None),
        climate=ClimateState(temperature=None, rainfall=None),
        human_impact=HumanImpactState(pollution=None, deforestation=None),
    )

    profile = engine.diagnose_risk_profile(state)

    assert profile.water_stress.level == RiskLevel.UNKNOWN
    assert profile.habitat_pressure.level == RiskLevel.UNKNOWN
    assert profile.biodiversity_pressure.level == RiskLevel.UNKNOWN
    assert profile.climate_exposure.level == RiskLevel.UNKNOWN
    assert profile.human_disturbance.level == RiskLevel.UNKNOWN

    assert len(profile.missing_important_variables) >= 10
    assert "Soil pH (soil.ph)" in profile.missing_important_variables


def test_zero_vs_unknown_distinction_in_risk():
    """Verifies that explicit 0.0 pollution/deforestation is Low risk, whereas None is Unknown."""
    engine = get_risk_engine()

    # Case A: Explicit 0.0 pollution & 0.0 deforestation (Pristine measurement)
    zero_state = EnvironmentalState(
        human_impact=HumanImpactState(pollution=0.0, deforestation=0.0),
    )
    profile_zero = engine.diagnose_risk_profile(zero_state)
    assert profile_zero.human_disturbance.level == RiskLevel.LOW
    assert "human_impact.pollution" in profile_zero.human_disturbance.observed_conditions
    assert profile_zero.human_disturbance.observed_conditions["human_impact.pollution"] == 0.0

    # Case B: None pollution & None deforestation (Unmeasured)
    unknown_state = EnvironmentalState(
        human_impact=HumanImpactState(pollution=None, deforestation=None),
    )
    profile_unknown = engine.diagnose_risk_profile(unknown_state)
    assert profile_unknown.human_disturbance.level == RiskLevel.UNKNOWN


# ==============================================================================
# 4. PARTIAL AND CONFLICTING METRICS
# ==============================================================================

def test_partial_state_isolated_water_stress():
    """Tests partial state where only climate/water metrics are provided."""
    engine = get_risk_engine()
    state = EnvironmentalState(
        soil=SoilState(moisture=12.0),
        climate=ClimateState(rainfall=420.0, temperature=34.0),
    )

    profile = engine.diagnose_risk_profile(state)

    assert profile.water_stress.level == RiskLevel.HIGH
    assert profile.climate_exposure.level == RiskLevel.HIGH
    assert profile.habitat_pressure.level == RiskLevel.UNKNOWN
    assert profile.human_disturbance.level == RiskLevel.UNKNOWN


def test_conflicting_metrics_scenario():
    """Tests conflicting conditions: high rainfall (1800mm) but extreme temperature (35°C)."""
    engine = get_risk_engine()
    state = EnvironmentalState(
        soil=SoilState(moisture=26.0),
        climate=ClimateState(rainfall=1800.0, temperature=35.0),
    )

    profile = engine.diagnose_risk_profile(state)

    # Water stress should be low/medium because rainfall and moisture are adequate
    assert profile.water_stress.level in (RiskLevel.LOW, RiskLevel.MEDIUM)
    # Climate exposure should be High due to extreme thermal stress (>33C)
    assert profile.climate_exposure.level == RiskLevel.HIGH


# ==============================================================================
# 5. EXTREME VALUES AND BOUNDARIES
# ==============================================================================

def test_extreme_rainfall_deluge_exposure():
    """Tests extreme high rainfall (>3200mm) triggering high climate exposure."""
    engine = get_risk_engine()
    state = EnvironmentalState(
        climate=ClimateState(rainfall=4500.0, temperature=24.0),
    )
    profile = engine.diagnose_risk_profile(state)
    assert profile.climate_exposure.level == RiskLevel.HIGH
    assert any("deluge" in d.lower() or "extreme" in d.lower() for d in profile.climate_exposure.inferred_drivers)


# ==============================================================================
# 6. EXPLAINABILITY STRUCTURE VERIFICATION
# ==============================================================================

def test_explainability_chain_structure():
    """Verifies that the 5-stage explainability chain contains all required stages."""
    engine = get_risk_engine()
    state = EnvironmentalState(
        soil=SoilState(ph=4.8, organic_carbon=0.9, moisture=15.0),
        land=LandState(land_use="monoculture"),
        biodiversity=BiodiversityState(species_richness=18, habitat_diversity=20.0),
        climate=ClimateState(temperature=31.0, rainfall=520.0),
        human_impact=HumanImpactState(pollution=30.0, deforestation=15.0),
    )

    profile = engine.diagnose_risk_profile(state)

    for dim in [profile.water_stress, profile.habitat_pressure, profile.biodiversity_pressure, profile.human_disturbance]:
        assert dim.explainability_chain is not None
        steps = dim.explainability_chain.steps
        assert len(steps) == 5
        stages = [s.stage for s in steps]
        assert stages == [
            "observed_conditions",
            "ecological_drivers",
            "mechanism",
            "nature_pressure",
            "evidence",
        ]


# ==============================================================================
# 7. API ENDPOINT TESTS
# ==============================================================================

def test_api_diagnose_nature_risk_profile():
    """Tests POST /api/v1/risk/profile."""
    payload = {
        "soil": {"ph": 5.2, "organic_carbon": 1.1, "moisture": 15.0},
        "land": {"land_use": "monoculture", "land_cover": "fragmented_canopy"},
        "biodiversity": {"species_richness": 25, "habitat_diversity": 30.0},
        "climate": {"temperature": 32.0, "rainfall": 510.0},
        "human_impact": {"pollution": 22.0, "deforestation": 12.0},
        "spatial_context": {"latitude": 12.5, "longitude": 76.5, "ecosystem": "tropical_dry_forest", "region": "South Asia"},
    }

    response = client.post("/api/v1/risk/profile", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert "water_stress" in data
    assert "habitat_pressure" in data
    assert "biodiversity_pressure" in data
    assert "climate_exposure" in data
    assert "human_disturbance" in data
    assert data["water_stress"]["level"] == "high"
    assert data["habitat_pressure"]["level"] == "high"
    assert len(data["evidence_summary"]) > 0


def test_api_list_risk_dimensions():
    """Tests GET /api/v1/risk/dimensions."""
    response = client.get("/api/v1/risk/dimensions")
    assert response.status_code == 200
    dims = response.json()
    assert len(dims) == 5
    dim_ids = [d["dimension_id"] for d in dims]
    assert "water_stress" in dim_ids
    assert "habitat_pressure" in dim_ids
    assert "biodiversity_pressure" in dim_ids
    assert "climate_exposure" in dim_ids
    assert "human_disturbance" in dim_ids
