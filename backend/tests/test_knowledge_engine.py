"""Comprehensive test suite for Phase 3: Ecological Knowledge Base & Relationship Engine."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.schemas.environmental_state import (
    BiodiversityState,
    ClimateState,
    EnvironmentalState,
    HumanImpactState,
    LandState,
    SoilState,
    SpatialContext,
)
from backend.app.schemas.knowledge import (
    ConditionOperator,
    MetricDomain,
    VariableObservationState,
)
from backend.app.knowledge.reasoning_engine import (
    EcologicalReasoningEngine,
    get_reasoning_engine,
)
from backend.app.knowledge.curated_metrics import CURATED_METRICS
from backend.app.knowledge.curated_evidence import CURATED_EVIDENCE
from backend.app.knowledge.curated_relationships import CURATED_RELATIONSHIPS


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def engine():
    """Instantiated EcologicalReasoningEngine fixture."""
    return get_reasoning_engine()


# ==============================================================================
# 1. KNOWLEDGE MODELS & CURATED ASSETS TESTS
# ==============================================================================

def test_curated_metrics_structure():
    """Verify all curated metrics satisfy schema validation and domain constraints."""
    assert len(CURATED_METRICS) >= 15
    domains = {m.domain for m in CURATED_METRICS}
    assert MetricDomain.SOIL in domains
    assert MetricDomain.LAND in domains
    assert MetricDomain.BIODIVERSITY in domains
    assert MetricDomain.CLIMATE in domains
    assert MetricDomain.HUMAN_IMPACT in domains
    assert MetricDomain.ECOLOGICAL_STATE in domains

    metric_ids = [m.id for m in CURATED_METRICS]
    assert "soil.ph" in metric_ids
    assert "soil.organic_carbon" in metric_ids
    assert "soil.moisture" in metric_ids
    assert "climate.rainfall" in metric_ids
    assert "climate.temperature" in metric_ids
    assert "human_impact.deforestation" in metric_ids
    assert "human_impact.pollution" in metric_ids


def test_curated_evidence_integrity():
    """Verify all curated evidence metadata contain authentic citations and institutional sources."""
    assert len(CURATED_EVIDENCE) >= 10
    for ev in CURATED_EVIDENCE:
        assert ev.id
        assert ev.citation
        assert ev.year >= 2000
        assert ev.institution in ["FAO", "IPCC", "IPBES", "UNEP", "CBD", "Science", "Annual Reviews", "Ecological Society of America", "Science Advances", "Geoderma", "Agriculture", "Biological Reviews", "Trends in Ecology & Evolution"]
        assert ev.confidence_grade in ["high", "moderate", "preliminary"]


def test_curated_relationships_count_and_evidence():
    """Verify curated relationships are between 30-50, have evidence IDs, and valid mechanisms."""
    assert 30 <= len(CURATED_RELATIONSHIPS) <= 50
    evidence_ids_pool = {e.id for e in CURATED_EVIDENCE}

    for rel in CURATED_RELATIONSHIPS:
        assert rel.id.startswith("REL_")
        assert len(rel.ecological_mechanism) > 30, f"Mechanism too short for {rel.id}"
        assert rel.confidence >= 0.8
        # Ensure referenced evidence exists in curated evidence pool
        for ev_id in rel.evidence_ids:
            assert ev_id in evidence_ids_pool, f"Evidence ID '{ev_id}' in {rel.id} not found in pool"


# ==============================================================================
# 2. INDIVIDUAL RELATIONSHIP EVALUATION TESTS
# ==============================================================================

def test_soil_organic_carbon_depletion_trigger(engine: EcologicalReasoningEngine):
    """Test SOC < 1.5% triggers soil biological activity degradation."""
    state = EnvironmentalState(
        soil=SoilState(organic_carbon=1.2)
    )
    result = engine.evaluate_state(state)
    pressure_ids = [p.pressure_id for p in result.inferred_pressures]
    assert "INF_derived_soil_biological_activity_degraded" in pressure_ids

    # Find the specific pressure and verify mechanism & evidence
    pressure = next(p for p in result.inferred_pressures if p.pressure_id == "INF_derived_soil_biological_activity_degraded")
    assert pressure.triggering_metric == "soil.organic_carbon"
    assert pressure.triggering_value == 1.2
    assert "heterotrophic microbes" in pressure.ecological_mechanism
    assert "FAO_SOIL_2020" in pressure.evidence_ids


def test_soil_ph_acidic_trigger(engine: EcologicalReasoningEngine):
    """Test soil pH < 5.5 triggers acid-restricted nutrient availability."""
    state = EnvironmentalState(
        soil=SoilState(ph=4.8)
    )
    result = engine.evaluate_state(state)
    pressures = {p.target_metric: p.inferred_state for p in result.inferred_pressures}
    assert pressures.get("derived.nutrient_availability") == "acid_restricted"


def test_soil_ph_alkaline_trigger(engine: EcologicalReasoningEngine):
    """Test soil pH > 8.2 triggers alkaline-restricted nutrient availability."""
    state = EnvironmentalState(
        soil=SoilState(ph=8.6)
    )
    result = engine.evaluate_state(state)
    pressures = {p.target_metric: p.inferred_state for p in result.inferred_pressures}
    assert pressures.get("derived.nutrient_availability") == "alkaline_restricted"


def test_rainfall_deficit_trigger(engine: EcologicalReasoningEngine):
    """Test rainfall < 500 mm triggers landscape water availability deficit."""
    state = EnvironmentalState(
        climate=ClimateState(rainfall=350.0)
    )
    result = engine.evaluate_state(state)
    pressures = {p.target_metric: p.inferred_state for p in result.inferred_pressures}
    assert pressures.get("derived.water_availability") == "deficit"


def test_deforestation_habitat_loss_and_fragmentation(engine: EcologicalReasoningEngine):
    """Test deforestation > 10% triggers both habitat loss and fragmentation."""
    state = EnvironmentalState(
        human_impact=HumanImpactState(deforestation=14.0)
    )
    result = engine.evaluate_state(state)
    target_states = {p.target_metric: p.inferred_state for p in result.inferred_pressures}
    assert target_states.get("derived.habitat_loss") == "severe"
    assert target_states.get("derived.habitat_fragmentation") == "elevated"


# ==============================================================================
# 3. MULTI-STEP REASONING CHAIN TESTS
# ==============================================================================

def test_monoculture_multi_step_chain(engine: EcologicalReasoningEngine):
    """Test multi-step forward reasoning chain:
    monoculture
    → habitat simplification
    → low habitat heterogeneity
    → restricted ecological niches
    → species survival / biodiversity loss pressure
    """
    state = EnvironmentalState(
        land=LandState(land_use="monoculture"),
        biodiversity=BiodiversityState(habitat_diversity=30.0, species_richness=25),
    )
    result = engine.evaluate_state(state)

    # Verify that multi-step cascading pressures fired
    target_metrics = {p.target_metric for p in result.inferred_pressures}
    assert "derived.habitat_heterogeneity" in target_metrics
    assert "derived.ecological_niches" in target_metrics
    assert "derived.species_survival_pressure" in target_metrics

    # Verify that reasoning chains exist
    assert len(result.reasoning_chains) > 0
    # Check chain connecting monoculture to downstream pressure
    monoculture_chains = [
        c for c in result.reasoning_chains if c.root_observed_metric == "land.land_use"
    ]
    assert len(monoculture_chains) >= 1
    # Find the deepest multi-step chain
    deep_chain = max(monoculture_chains, key=lambda c: len(c.links))
    assert deep_chain.root_observed_value == "monoculture"
    assert len(deep_chain.links) >= 2
    assert deep_chain.links[0].relationship_id in ("REL_MONOCULTURE_HABITAT_HETEROGENEITY", "REL_MONOCULTURE_HABITAT_DIVERSITY")
    assert deep_chain.links[0].ecological_mechanism


def test_deforestation_cascading_chain(engine: EcologicalReasoningEngine):
    """Test multi-step chain:
    deforestation
    → fragmentation
    → impaired connectivity
    → genetic isolation pressure
    """
    state = EnvironmentalState(
        human_impact=HumanImpactState(deforestation=12.0)
    )
    result = engine.evaluate_state(state)

    inferred_states = {p.inferred_state for p in result.inferred_pressures}
    assert "elevated" in inferred_states
    assert "impaired" in inferred_states
    assert "genetic_isolation" in inferred_states

    # Verify complete multi-step reasoning chain from deforestation
    defor_chains = [
        c for c in result.reasoning_chains if c.root_observed_metric == "human_impact.deforestation"
    ]
    assert len(defor_chains) >= 1
    deep_chain = max(defor_chains, key=lambda c: len(c.links))
    assert len(deep_chain.links) >= 3
    assert deep_chain.links[0].relationship_id == "REL_DEFORESTATION_FRAGMENTATION"
    assert deep_chain.links[1].relationship_id == "REL_FRAGMENTATION_CONNECTIVITY"
    assert deep_chain.links[2].relationship_id == "REL_CONNECTIVITY_GENETIC_PRESSURE"


# ==============================================================================
# 4. ZERO VS UNKNOWN & MISSING METRICS TESTS
# ==============================================================================

def test_zero_vs_unknown_distinction(engine: EcologicalReasoningEngine):
    """Ensure strict distinction between 0.0 (observed zero) and None (unknown)."""
    # Case A: pollution is 0.0 (clean environment)
    state_zero_pollution = EnvironmentalState(
        human_impact=HumanImpactState(pollution=0.0, deforestation=None)
    )
    result_zero = engine.evaluate_state(state_zero_pollution)

    poll_status = next(s for s in result_zero.variables_status if s.metric_id == "human_impact.pollution")
    assert poll_status.status == VariableObservationState.OBSERVED
    assert poll_status.observed_value == 0.0

    defor_status = next(s for s in result_zero.variables_status if s.metric_id == "human_impact.deforestation")
    assert defor_status.status == VariableObservationState.UNKNOWN
    assert defor_status.observed_value is None

    # Crucial: 0.0 pollution must NOT trigger pollution > 25.0
    toxicity_pressures = [
        p for p in result_zero.inferred_pressures if p.target_metric == "derived.environmental_toxicity_stress"
    ]
    assert len(toxicity_pressures) == 0

    # Case B: pollution is None (unknown)
    state_unknown_pollution = EnvironmentalState(
        human_impact=HumanImpactState(pollution=None)
    )
    result_unknown = engine.evaluate_state(state_unknown_pollution)
    poll_status_unknown = next(s for s in result_unknown.variables_status if s.metric_id == "human_impact.pollution")
    assert poll_status_unknown.status == VariableObservationState.UNKNOWN
    assert poll_status_unknown.observed_value is None


def test_missing_metrics_graceful_handling(engine: EcologicalReasoningEngine):
    """Engine must gracefully handle an almost completely empty state without crashing."""
    state = EnvironmentalState(
        soil=SoilState(ph=None, organic_carbon=None, moisture=None)
    )
    result = engine.evaluate_state(state)
    assert result.observed_metrics_count == 0
    assert result.unknown_metrics_count >= 10
    assert len(result.inferred_pressures) == 0
    assert len(result.compound_pressures) == 0
    assert len(result.reasoning_chains) == 0


# ==============================================================================
# 5. MULTI-METRIC COMPOUND STRESS TESTS
# ==============================================================================

def test_multi_metric_thermal_hydro_drought(engine: EcologicalReasoningEngine):
    """Test compound pressure: low rainfall (<600) + high temperature (>30) -> Thermal-Hydro Drought."""
    state = EnvironmentalState(
        climate=ClimateState(rainfall=400.0, temperature=34.0)
    )
    result = engine.evaluate_state(state)
    compound_ids = [c.compound_id for c in result.compound_pressures]
    assert "COMPOUND_THERMAL_HYDRO_DROUGHT" in compound_ids

    compound = next(c for c in result.compound_pressures if c.compound_id == "COMPOUND_THERMAL_HYDRO_DROUGHT")
    assert compound.severity == "critical"
    assert "climate.rainfall" in compound.participating_metrics
    assert "climate.temperature" in compound.participating_metrics
    assert "vapor pressure deficit" in compound.synergistic_mechanism


def test_multi_metric_monoculture_and_depleted_species(engine: EcologicalReasoningEngine):
    """Test compound pressure: monoculture + species richness < 40 -> Agro-Homogenization Collapse."""
    state = EnvironmentalState(
        land=LandState(land_use="monoculture"),
        biodiversity=BiodiversityState(species_richness=18),
    )
    result = engine.evaluate_state(state)
    compound_ids = [c.compound_id for c in result.compound_pressures]
    assert "COMPOUND_MONOCULTURE_BIODIVERSITY_COLLAPSE" in compound_ids


# ==============================================================================
# 6. NO APPLICABLE RELATIONSHIP & PRISTINE BASELINE TESTS
# ==============================================================================

def test_pristine_baseline_no_adverse_pressures(engine: EcologicalReasoningEngine):
    """Test pristine/optimal state does not fire degradation rules."""
    state = EnvironmentalState(
        soil=SoilState(ph=6.8, organic_carbon=4.5, moisture=35.0),
        land=LandState(land_use="conservation_forest", land_cover="closed_canopy_forest"),
        biodiversity=BiodiversityState(species_richness=120, habitat_diversity=85.0),
        climate=ClimateState(rainfall=1400.0, temperature=22.0),
        human_impact=HumanImpactState(pollution=0.0, deforestation=0.0),
    )
    result = engine.evaluate_state(state)

    # Adverse degradation pressures should not fire
    adverse_targets = {
        p.target_metric: p.inferred_state
        for p in result.inferred_pressures
        if p.severity in ("critical", "high")
    }
    assert "derived.soil_biological_activity" not in adverse_targets
    assert "derived.plant_water_stress" not in adverse_targets
    assert "derived.environmental_toxicity_stress" not in adverse_targets
    assert len(result.compound_pressures) == 0


def test_unsupported_condition_handling(engine: EcologicalReasoningEngine):
    """Unsupported or non-matching categorical values produce no false triggers."""
    state = EnvironmentalState(
        land=LandState(land_use="unknown_custom_classification")
    )
    result = engine.evaluate_state(state)
    assert len(result.inferred_pressures) == 0


# ==============================================================================
# 7. API ENDPOINT TESTS (INTEGRATION)
# ==============================================================================

def test_api_list_metrics(client: TestClient):
    """GET /api/v1/knowledge/metrics returns all metrics."""
    response = client.get("/api/v1/knowledge/metrics")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 15
    metric_ids = [m["id"] for m in data]
    assert "soil.ph" in metric_ids
    assert "climate.rainfall" in metric_ids


def test_api_list_metrics_domain_filter(client: TestClient):
    """GET /api/v1/knowledge/metrics?domain=soil filters strictly by soil domain."""
    response = client.get("/api/v1/knowledge/metrics?domain=soil")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3
    for m in data:
        assert m["domain"] == "soil"


def test_api_list_relationships(client: TestClient):
    """GET /api/v1/knowledge/relationships returns curated relationships."""
    response = client.get("/api/v1/knowledge/relationships")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 30
    first = data[0]
    assert "id" in first
    assert "ecological_mechanism" in first
    assert "evidence_ids" in first


def test_api_list_evidence(client: TestClient):
    """GET /api/v1/knowledge/evidence returns authentic citations."""
    response = client.get("/api/v1/knowledge/evidence")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 10
    ev_ids = [e["id"] for e in data]
    assert "FAO_SOIL_2020" in ev_ids
    assert "IPCC_WG2_2022_CH2" in ev_ids


def test_api_evaluate_reasoning_endpoint(client: TestClient):
    """POST /api/v1/reasoning/evaluate performs forward-chaining reasoning."""
    payload = {
        "soil": {"ph": 4.5, "organic_carbon": 1.1},
        "climate": {"rainfall": 420.0, "temperature": 33.0},
        "land": {"land_use": "monoculture"},
        "biodiversity": {"habitat_diversity": 25.0},
        "human_impact": {"pollution": 0.0, "deforestation": 12.0},
    }
    response = client.post("/api/v1/reasoning/evaluate", json=payload)
    assert response.status_code == 200
    result = response.json()

    assert result["observed_metrics_count"] >= 7
    assert result["inferred_pressures_count"] >= 5
    assert len(result["compound_pressures"]) >= 1
    assert len(result["reasoning_chains"]) >= 2

    # Verify zero pollution was observed and not inferred as toxic
    poll_stat = next(s for s in result["variables_status"] if s["metric_id"] == "human_impact.pollution")
    assert poll_stat["status"] == "observed"
    assert poll_stat["observed_value"] == 0.0


def test_api_explain_relationship_endpoint(client: TestClient):
    """GET /api/v1/reasoning/explain/{id} returns details for a specific relationship."""
    response = client.get("/api/v1/reasoning/explain/REL_SOC_BIOLOGICAL_ACTIVITY")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "REL_SOC_BIOLOGICAL_ACTIVITY"
    assert "heterotrophic microbes" in data["ecological_mechanism"]
    assert "FAO_SOIL_2020" in data["evidence_ids"]


def test_api_explain_relationship_not_found(client: TestClient):
    """GET /api/v1/reasoning/explain/{id} returns 404 for unknown relationship."""
    response = client.get("/api/v1/reasoning/explain/NON_EXISTENT_RELATIONSHIP")
    assert response.status_code == 404
