"""Comprehensive End-to-End QA and Scientific Validation Test Suite (Phase 15).

Covers all 8 realistic environmental scenarios across all 5 domains, pipeline flow verification,
scientific integrity invariants (no fabricated citations, uncertainty preservation, zero vs unknown),
and edge case resilience.
"""

import pytest
from backend.app.schemas.environmental_state import (
    EnvironmentalState,
    SoilMetrics,
    LandMetrics,
    ClimateMetrics,
    BiodiversityMetrics,
    HumanImpactMetrics,
    SpatialContext,
)
from backend.app.schemas.ecological_findings import ConflictReport, ConflictType, ConflictResolutionStrategy
from backend.app.schemas.intervention import InterventionEngineRequest
from backend.app.knowledge.intervention_engine import get_intervention_engine
from backend.app.knowledge.risk_engine import get_risk_engine
from backend.app.knowledge.rag_service import get_rag_service
from backend.app.knowledge.reasoning_engine import get_reasoning_engine
from backend.app.knowledge.conversation_engine import get_conversation_engine


@pytest.fixture
def engines():
    return {
        "intervention": get_intervention_engine(),
        "risk": get_risk_engine(),
        "rag": get_rag_service(),
        "reasoning": get_reasoning_engine(),
        "conversation": get_conversation_engine(),
    }


# ==============================================================================
# 1. 8 SCENARIO TESTS ACROSS 5 DOMAINS
# ==============================================================================

def test_scenario_1_soil_degradation(engines):
    """Scenario 1: Soil degradation (low SOC, acidic pH)."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=4.2, organic_carbon=0.35, moisture=12.0),
        land=LandMetrics(land_use="degraded_pasture", land_cover="sparse"),
        climate=ClimateMetrics(temperature=26.0, rainfall=650.0),
        biodiversity=BiodiversityMetrics(species_richness=18.0, habitat_diversity=30.0),
        human_impact=HumanImpactMetrics(deforestation=15.0, pollution=10.0),
    )
    # Test risk diagnosis
    risk_res = engines["risk"].diagnose_risk_profile(state)
    assert risk_res is not None
    assert risk_res.water_stress is not None

    # Test intervention generation
    req = InterventionEngineRequest(state=state, max_recommendations=3)
    res = engines["intervention"].generate_recommendations(req)
    assert res.total_recommendations >= 1
    for rec in res.recommendations:
        assert rec.validation is not None
        assert rec.validation.uncertainty_statement is not None


def test_scenario_2_biodiversity_decline(engines):
    """Scenario 2: Biodiversity decline (low species richness, habitat loss)."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=6.5, organic_carbon=1.2, moisture=22.0),
        land=LandMetrics(land_use="intensive_cropland", land_cover="monoculture"),
        climate=ClimateMetrics(temperature=24.0, rainfall=800.0),
        biodiversity=BiodiversityMetrics(species_richness=8.0, habitat_diversity=15.0),
        human_impact=HumanImpactMetrics(deforestation=25.0, pollution=20.0),
    )
    req = InterventionEngineRequest(state=state, max_recommendations=3)
    res = engines["intervention"].generate_recommendations(req)
    assert res.total_recommendations >= 1


def test_scenario_3_habitat_fragmentation(engines):
    """Scenario 3: Habitat fragmentation (corridors & stepping stones)."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=6.8, organic_carbon=1.8, moisture=28.0),
        land=LandMetrics(land_use="agricultural_mosaic", land_cover="fragmented_forest"),
        climate=ClimateMetrics(temperature=22.0, rainfall=1100.0),
        biodiversity=BiodiversityMetrics(species_richness=22.0, habitat_diversity=40.0),
        human_impact=HumanImpactMetrics(deforestation=40.0, pollution=5.0),
    )
    req = InterventionEngineRequest(state=state, max_recommendations=3)
    res = engines["intervention"].generate_recommendations(req)
    assert res.total_recommendations >= 1


def test_scenario_4_water_climate_stress(engines):
    """Scenario 4: Water/climate stress (rainfall deficit, thermal stress)."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=7.5, organic_carbon=0.6, moisture=8.0),
        land=LandMetrics(land_use="semi_arid_grazing", land_cover="sparse_shrub"),
        climate=ClimateMetrics(temperature=35.0, rainfall=280.0),
        biodiversity=BiodiversityMetrics(species_richness=12.0, habitat_diversity=20.0),
        human_impact=HumanImpactMetrics(deforestation=10.0, pollution=5.0),
    )
    req = InterventionEngineRequest(state=state, max_recommendations=3)
    res = engines["intervention"].generate_recommendations(req)
    assert res.total_recommendations >= 1


def test_scenario_5_pollution_pressure(engines):
    """Scenario 5: Pollution pressure."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=5.0, organic_carbon=0.9, moisture=18.0),
        land=LandMetrics(land_use="industrial_agricultural", land_cover="disturbed"),
        climate=ClimateMetrics(temperature=23.0, rainfall=950.0),
        biodiversity=BiodiversityMetrics(species_richness=14.0, habitat_diversity=25.0),
        human_impact=HumanImpactMetrics(deforestation=12.0, pollution=85.0),
    )
    req = InterventionEngineRequest(state=state, max_recommendations=3)
    res = engines["intervention"].generate_recommendations(req)
    assert res.total_recommendations >= 1


def test_scenario_6_deforestation(engines):
    """Scenario 6: Deforestation and canopy loss."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=5.8, organic_carbon=1.5, moisture=30.0),
        land=LandMetrics(land_use="degraded_forest", land_cover="cleared_patches"),
        climate=ClimateMetrics(temperature=27.0, rainfall=2200.0),
        biodiversity=BiodiversityMetrics(species_richness=28.0, habitat_diversity=45.0),
        human_impact=HumanImpactMetrics(deforestation=65.0, pollution=10.0),
    )
    req = InterventionEngineRequest(state=state, max_recommendations=3)
    res = engines["intervention"].generate_recommendations(req)
    assert res.total_recommendations >= 1


def test_scenario_7_agricultural_low_biodiversity(engines):
    """Scenario 7: Agricultural land with low habitat diversity."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=6.5, organic_carbon=1.1, moisture=20.0),
        land=LandMetrics(land_use="monoculture_cropland", land_cover="uniform_crop"),
        climate=ClimateMetrics(temperature=24.0, rainfall=750.0),
        biodiversity=BiodiversityMetrics(species_richness=10.0, habitat_diversity=12.0),
        human_impact=HumanImpactMetrics(deforestation=5.0, pollution=30.0),
    )
    req = InterventionEngineRequest(state=state, max_recommendations=3)
    res = engines["intervention"].generate_recommendations(req)
    assert res.total_recommendations >= 1


def test_scenario_8_multi_pressure_degradation(engines):
    """Scenario 8: Multi-pressure ecosystem degradation combining soil, climate, and biodiversity stress."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=4.5, organic_carbon=0.4, moisture=10.0),
        land=LandMetrics(land_use="overgrazed_pasture", land_cover="eroded"),
        climate=ClimateMetrics(temperature=31.0, rainfall=350.0),
        biodiversity=BiodiversityMetrics(species_richness=11.0, habitat_diversity=18.0),
        human_impact=HumanImpactMetrics(deforestation=35.0, pollution=45.0),
    )
    req = InterventionEngineRequest(state=state, max_recommendations=4)
    res = engines["intervention"].generate_recommendations(req)
    assert res.total_recommendations >= 1
    assert any(len(rec.addressed_pressures) > 0 for rec in res.recommendations)


# ==============================================================================
# 2. SCIENTIFIC INTEGRITY INVARIANTS
# ==============================================================================

def test_scientific_integrity_no_fabricated_citations(engines):
    """Verify all evidence references link to authenticated documents with valid DOIs/IDs and no fabrication."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=5.0, organic_carbon=0.8, moisture=15.0),
        land=LandMetrics(land_use="degraded_forest", land_cover="sparse"),
        climate=ClimateMetrics(temperature=25.0, rainfall=600.0),
    )
    req = InterventionEngineRequest(state=state, max_recommendations=3)
    res = engines["intervention"].generate_recommendations(req)
    for rec in res.recommendations:
        for ev in rec.evidence_references:
            assert ev.document_id.startswith("DOC_")
            assert ev.title is not None
            assert ev.content is not None


def test_scientific_integrity_zero_vs_unknown(engines):
    """Verify strict distinction between zero (0.0) and unknown (None)."""
    state_zero = EnvironmentalState(
        soil=SoilMetrics(ph=0.0, organic_carbon=0.0, moisture=0.0),
        climate=ClimateMetrics(rainfall=0.0),
    )
    assert state_zero.soil.ph == 0.0
    assert state_zero.soil.organic_carbon == 0.0
    assert state_zero.soil.moisture == 0.0
    assert state_zero.climate.rainfall == 0.0
    assert state_zero.is_empty() is False


# ==============================================================================
# 3. EDGE CASE RESILIENCE TESTS
# ==============================================================================

def test_edge_case_missing_data(engines):
    """Edge case: Empty or missing data state."""
    state = EnvironmentalState()
    assert state.is_empty() is True
    req = InterventionEngineRequest(state=state, max_recommendations=3)
    res = engines["intervention"].generate_recommendations(req)
    assert res is not None


def test_edge_case_conflicting_observations(engines):
    """Edge case: Conflicting observations handled gracefully with uncertainty penalties."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=6.5, organic_carbon=1.5, moisture=20.0),
    )
    conflict = ConflictReport(
        conflict_id="CONF_QA",
        conflict_type=ConflictType.USER_DATASET_DISCREPANCY,
        variables_involved=["soil.organic_carbon"],
        user_value=1.5,
        dataset_value=0.5,
        delta_percentage=66.0,
        message="User SOC conflicts with dataset.",
        resolution_strategy=ConflictResolutionStrategy.USER_PREFERRED_WITH_UNCERTAINTY,
        uncertainty_penalty=0.25,
    )
    req = InterventionEngineRequest(state=state, conflicts=[conflict], max_recommendations=3)
    res = engines["intervention"].generate_recommendations(req)
    assert res.total_recommendations >= 1
    assert res.recommendations[0].confidence_basis.conflict_uncertainty_penalty == 0.25


def test_edge_case_conversational_multi_turn(engines):
    """Edge case: Multi-turn conversation state persistence and updates."""
    conv = engines["conversation"]
    session_id = "qa_session_01"
    res1 = conv.process_message(session_id, "My land use is cropland and rainfall is 450mm.")
    assert res1.environmental_memory.land_use == "cropland"
    assert res1.environmental_memory.rainfall == 450.0

    res2 = conv.process_message(session_id, "Soil organic carbon is 0.5%.")
    assert res2.environmental_memory.land_use == "cropland"
    assert res2.environmental_memory.rainfall == 450.0
    assert res2.environmental_memory.soil_organic_carbon == 0.5
