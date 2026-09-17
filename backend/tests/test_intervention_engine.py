"""Comprehensive Scientific Unit and Integration Tests for Ecological Intervention Engine (Phase 10).

Tests:
- Suitable intervention matching
- Unsuitable context biophysical exclusion (e.g. wetland in desert, agroforestry in intact forest)
- Insufficient data handling & confidence calibration
- Multiple environmental pressures handling
- Missing evidence handling & penalty
- Conflicting evidence / data discrepancy penalty
- Unsupported quantitative claims prevention (strictly directional fallback)
- Recommendation provenance & finding traceability
- Deterministic repeatability across multiple runs
- FastAPI endpoint integrations (/catalogue, /{id}, /recommend)
"""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.schemas.environmental_state import (
    EnvironmentalState,
    SoilMetrics,
    LandMetrics,
    ClimateMetrics,
    BiodiversityMetrics,
    HumanImpactMetrics,
    SpatialContext,
)
from backend.app.schemas.ecological_findings import (
    EcologicalFinding,
    ConflictReport,
    ConflictType,
    ConflictResolutionStrategy,
    NaturePressureSeverity,
)
from backend.app.schemas.intervention import (
    DirectionOfChange,
    InterventionEngineRequest,
    TimeHorizon,
)
from backend.app.knowledge.intervention_engine import get_intervention_engine


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def engine():
    return get_intervention_engine()


# --------------------------------------------------------------------------
# 1. Test Suitable Intervention Matching
# --------------------------------------------------------------------------
def test_suitable_intervention_matching(engine):
    """Verify appropriate intervention matching for soil carbon depletion and moisture stress."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=6.5, organic_carbon=0.9, moisture=12.0),
        land=LandMetrics(land_use="cropland", land_cover="sparse_vegetation"),
        climate=ClimateMetrics(temperature=28.0, rainfall=650.0),
        biodiversity=BiodiversityMetrics(species_richness=18.0, habitat_diversity=35.0),
        human_impact=HumanImpactMetrics(deforestation=5.0, pollution=15.0),
        spatial_context=SpatialContext(latitude=15.5, longitude=75.0, region="Semi-Arid Deccan", ecosystem="agroecosystems"),
    )

    finding = EcologicalFinding(
        finding_id="FINDING_SOIL_WATER_STRESS",
        title="Soil Moisture & Carbon Depletion",
        domain="soil_health",
        severity=NaturePressureSeverity.HIGH,
        contributing_variables=["soil.organic_carbon", "soil.moisture", "climate.rainfall"],
        variable_details=[],
        inferred_pressure="soil_water_stress",
        ecological_mechanism="Depleted organic carbon reduces macro-aggregates and available water capacity.",
        supporting_relationships=["REL_001"],
        confidence=0.88,
        geographic_relevance="semi_arid",
    )

    request = InterventionEngineRequest(
        state=state,
        findings=[finding],
        max_recommendations=5,
        min_confidence_threshold=0.40,
    )

    response = engine.generate_recommendations(request)

    assert response.total_recommendations >= 1
    top_rec = response.recommendations[0]

    # Verify top recommendations include soil cover or agroforestry
    rec_ids = [r.intervention_id for r in response.recommendations]
    assert "INT_SOIL_COVER_PRACTICES" in rec_ids or "INT_AGROFORESTRY_SYSTEMS" in rec_ids

    # Verify required recommendation fields
    assert top_rec.what_to_do is not None and len(top_rec.what_to_do) > 20
    assert top_rec.why_it_works is not None and len(top_rec.why_it_works) > 20
    assert top_rec.ecological_mechanism is not None and len(top_rec.ecological_mechanism) > 20
    assert len(top_rec.target_metrics) > 0
    assert len(top_rec.evidence_ids) > 0
    assert top_rec.confidence_basis.overall_confidence >= 0.50
    assert top_rec.relevance_rank == 1


# --------------------------------------------------------------------------
# 2. Test Unsuitable Context Biophysical Exclusion
# --------------------------------------------------------------------------
def test_unsuitable_context_exclusions(engine):
    """Verify that interventions are disqualified when biophysical context is incompatible."""
    # Context A: Hyper-arid desert (should exclude wetland restoration and high-rainfall interventions)
    arid_state = EnvironmentalState(
        soil=SoilMetrics(ph=8.2, organic_carbon=0.3, moisture=4.0),
        land=LandMetrics(land_use="arid_rangeland", land_cover="bare_soil"),
        climate=ClimateMetrics(temperature=38.0, rainfall=95.0),
        biodiversity=BiodiversityMetrics(species_richness=6.0, habitat_diversity=15.0),
        human_impact=HumanImpactMetrics(deforestation=0.0, pollution=5.0),
        spatial_context=SpatialContext(latitude=24.0, longitude=12.0, region="Sahara", ecosystem="hyper_arid_desert_sand_sheet"),
    )

    request = InterventionEngineRequest(
        state=arid_state,
        findings=[],
        max_recommendations=5,
    )

    response = engine.generate_recommendations(request)
    assert "INT_WETLAND_RESTORATION" in response.excluded_interventions
    assert "INT_NATIVE_VEGETATION_RESTORATION" in response.excluded_interventions or "rainfall" in response.excluded_interventions.get("INT_NATIVE_VEGETATION_RESTORATION", "").lower()

    # Context B: Intact primary forest (should exclude agroforestry and monoculture intercropping)
    forest_state = EnvironmentalState(
        soil=SoilMetrics(ph=5.8, organic_carbon=4.5, moisture=38.0),
        land=LandMetrics(land_use="intact_primary_forest", land_cover="dense_canopy"),
        climate=ClimateMetrics(temperature=24.0, rainfall=2200.0),
        biodiversity=BiodiversityMetrics(species_richness=85.0, habitat_diversity=90.0),
        human_impact=HumanImpactMetrics(deforestation=0.0, pollution=2.0),
        spatial_context=SpatialContext(latitude=-3.0, longitude=-60.0, region="Central Amazon", ecosystem="tropical_forest"),
    )

    request_forest = InterventionEngineRequest(
        state=forest_state,
        findings=[],
        max_recommendations=5,
    )
    response_forest = engine.generate_recommendations(request_forest)
    assert "INT_AGROFORESTRY_SYSTEMS" in response_forest.excluded_interventions
    assert "intact_primary_forest" in response_forest.excluded_interventions["INT_AGROFORESTRY_SYSTEMS"]


# --------------------------------------------------------------------------
# 3. Test Insufficient Data Handling
# --------------------------------------------------------------------------
def test_insufficient_data_confidence_calibration(engine):
    """Verify that unknown/missing metrics transparently reduce data completeness and confidence."""
    sparse_state = EnvironmentalState(
        soil=SoilMetrics(ph=None, organic_carbon=None, moisture=None),
        land=LandMetrics(land_use="cropland", land_cover=None),
        climate=ClimateMetrics(temperature=None, rainfall=None),
        biodiversity=BiodiversityMetrics(species_richness=None, habitat_diversity=25.0),
        human_impact=HumanImpactMetrics(deforestation=None, pollution=None),
        spatial_context=SpatialContext(region="Unknown", ecosystem="agroecosystems"),
    )

    sparse_finding = EcologicalFinding(
        finding_id="FINDING_HABITAT_SIMPLIFICATION",
        title="Habitat Simplification",
        domain="biodiversity_trophic",
        severity=NaturePressureSeverity.HIGH,
        contributing_variables=["biodiversity.habitat_diversity"],
        variable_details=[],
        inferred_pressure="monoculture_simplification",
        ecological_mechanism="Simplified structure limits niches.",
        supporting_relationships=["REL_002"],
        confidence=0.60,
        geographic_relevance="global",
    )

    request = InterventionEngineRequest(
        state=sparse_state,
        findings=[sparse_finding],
        max_recommendations=5,
    )

    response = engine.generate_recommendations(request)
    assert response.total_recommendations >= 1

    # Check top recommendation confidence reflects lower data completeness
    top_rec = response.recommendations[0]
    assert top_rec.confidence_basis.data_completeness_factor < 0.90
    assert "Data completeness=" in top_rec.confidence_basis.justification_summary


# --------------------------------------------------------------------------
# 4. Test Multiple Environmental Pressures Handling
# --------------------------------------------------------------------------
def test_multiple_environmental_pressures(engine):
    """Verify that multiple distinct pressures trigger complementary diverse interventions."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=4.6, organic_carbon=0.8, moisture=14.0),
        land=LandMetrics(land_use="cropland", land_cover="fragmented"),
        climate=ClimateMetrics(temperature=26.0, rainfall=1200.0),
        biodiversity=BiodiversityMetrics(species_richness=12.0, habitat_diversity=22.0),
        human_impact=HumanImpactMetrics(deforestation=35.0, pollution=45.0),
        spatial_context=SpatialContext(latitude=12.0, longitude=76.0, region="Western Ghats Foothills", ecosystem="tropical_forest"),
    )

    findings = [
        EcologicalFinding(
            finding_id="FINDING_FRAGMENTATION_DEFORESTATION",
            title="Severe Forest Fragmentation",
            domain="anthropogenic_pressure",
            severity=NaturePressureSeverity.CRITICAL,
            contributing_variables=["human_impact.deforestation", "biodiversity.habitat_diversity"],
            variable_details=[],
            inferred_pressure="habitat_fragmentation",
            ecological_mechanism="Canopy clearing isolates native populations.",
            supporting_relationships=["REL_004"],
            confidence=0.92,
            geographic_relevance="tropical_forest",
        ),
        EcologicalFinding(
            finding_id="FINDING_AGROCHEMICAL_POLLUTION",
            title="Agrochemical Runoff & Ecotoxicity",
            domain="anthropogenic_pressure",
            severity=NaturePressureSeverity.HIGH,
            contributing_variables=["human_impact.pollution"],
            variable_details=[],
            inferred_pressure="chemical_pollution",
            ecological_mechanism="Pesticide drift and nutrient runoff impair freshwater organisms.",
            supporting_relationships=["REL_005"],
            confidence=0.89,
            geographic_relevance="tropical_forest",
        ),
    ]

    request = InterventionEngineRequest(
        state=state,
        findings=findings,
        max_recommendations=5,
    )

    response = engine.generate_recommendations(request)
    assert response.total_recommendations >= 2
    assert response.targeted_findings_count >= 2

    rec_categories = [r.category for r in response.recommendations]
    # Should include connectivity/restoration AND riparian/agroecology
    has_connectivity = any(c in ["habitat_connectivity", "native_restoration"] for c in rec_categories)
    has_water_or_soil = any(c in ["water_and_riparian", "soil_conservation", "agroecology", "landscape_heterogeneity"] for c in rec_categories)
    assert has_connectivity and has_water_or_soil


# --------------------------------------------------------------------------
# 5. Test Conflicting Evidence & Discrepancy Penalties
# --------------------------------------------------------------------------
def test_conflicting_evidence_uncertainty_penalty(engine):
    """Verify that data conflicts apply a mathematical penalty to recommendation confidence."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=6.8, organic_carbon=1.1, moisture=16.0),
        land=LandMetrics(land_use="cropland", land_cover="sparse"),
        climate=ClimateMetrics(temperature=25.0, rainfall=800.0),
        biodiversity=BiodiversityMetrics(species_richness=20.0, habitat_diversity=30.0),
        human_impact=HumanImpactMetrics(deforestation=10.0, pollution=20.0),
    )

    conflict = ConflictReport(
        conflict_id="CONF_SOIL_PH_MISMATCH",
        conflict_type=ConflictType.USER_DATASET_DISCREPANCY,
        variables_involved=["soil.ph"],
        user_value=6.8,
        dataset_value=4.9,
        delta_percentage=38.7,
        message="User reported pH 6.8 but authoritative dataset indicates acidic pH 4.9.",
        resolution_strategy=ConflictResolutionStrategy.USER_PREFERRED_WITH_UNCERTAINTY,
        uncertainty_penalty=0.18,
    )

    request_no_conflict = InterventionEngineRequest(state=state, findings=[], conflicts=[])
    request_with_conflict = InterventionEngineRequest(state=state, findings=[], conflicts=[conflict])

    resp_clean = engine.generate_recommendations(request_no_conflict)
    resp_conflict = engine.generate_recommendations(request_with_conflict)

    if resp_clean.recommendations and resp_conflict.recommendations:
        conf_clean = resp_clean.recommendations[0].confidence_basis.overall_confidence
        conf_conflict = resp_conflict.recommendations[0].confidence_basis.overall_confidence
        assert conf_conflict < conf_clean
        assert resp_conflict.recommendations[0].confidence_basis.conflict_uncertainty_penalty > 0


# --------------------------------------------------------------------------
# 6. Test Unsupported Quantitative Claims Prevention
# --------------------------------------------------------------------------
def test_unsupported_quantitative_claims_prevention(engine):
    """Verify that expected metric effects use directional terms when not explicitly cited."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=6.2, organic_carbon=1.2, moisture=18.0),
        land=LandMetrics(land_use="cropland", land_cover="herbaceous"),
        climate=ClimateMetrics(temperature=22.0, rainfall=750.0),
        biodiversity=BiodiversityMetrics(species_richness=15.0, habitat_diversity=28.0),
        human_impact=HumanImpactMetrics(deforestation=5.0, pollution=10.0),
    )

    request = InterventionEngineRequest(state=state, max_recommendations=5)
    response = engine.generate_recommendations(request)

    for rec in response.recommendations:
        for effect in rec.expected_metric_effects:
            assert isinstance(effect.expected_direction, DirectionOfChange)
            # If not quantified, quantitative_estimate must be None
            if not effect.is_quantified:
                assert effect.quantitative_estimate is None
            else:
                # If quantified, must include an explicit citation string
                assert "(" in effect.quantitative_estimate and ")" in effect.quantitative_estimate


# --------------------------------------------------------------------------
# 7. Test Recommendation Provenance
# --------------------------------------------------------------------------
def test_recommendation_provenance(engine):
    """Verify recommendations provide full traceable provenance back to findings and literature."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=6.4, organic_carbon=0.8, moisture=10.0),
        land=LandMetrics(land_use="cropland", land_cover="cultivated"),
        climate=ClimateMetrics(temperature=29.0, rainfall=500.0),
        biodiversity=BiodiversityMetrics(species_richness=14.0, habitat_diversity=25.0),
        human_impact=HumanImpactMetrics(deforestation=8.0, pollution=15.0),
    )

    finding = EcologicalFinding(
        finding_id="FINDING_SOIL_CARBON_DECAY",
        title="Soil Organic Carbon Depletion",
        domain="soil_health",
        severity=NaturePressureSeverity.HIGH,
        contributing_variables=["soil.organic_carbon", "soil.moisture"],
        variable_details=[],
        inferred_pressure="soil_carbon_depletion",
        ecological_mechanism="Continuous cropping without residue returns oxidizes organic carbon.",
        supporting_relationships=["REL_001"],
        confidence=0.90,
        geographic_relevance="global",
    )

    request = InterventionEngineRequest(state=state, findings=[finding], max_recommendations=3)
    response = engine.generate_recommendations(request)

    assert response.total_recommendations >= 1
    top_rec = response.recommendations[0]

    assert "FINDING_SOIL_CARBON_DECAY" in top_rec.addressed_findings
    assert len(top_rec.evidence_ids) > 0
    assert len(top_rec.evidence_references) > 0
    assert top_rec.evidence_references[0].document_id in top_rec.evidence_ids


# --------------------------------------------------------------------------
# 8. Test Deterministic Repeatability
# --------------------------------------------------------------------------
def test_deterministic_repeatability(engine):
    """Verify that identical inputs produce identical recommendations, rankings, and scores."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=5.2, organic_carbon=1.1, moisture=14.0),
        land=LandMetrics(land_use="cropland", land_cover="mixed"),
        climate=ClimateMetrics(temperature=25.0, rainfall=900.0),
        biodiversity=BiodiversityMetrics(species_richness=16.0, habitat_diversity=32.0),
        human_impact=HumanImpactMetrics(deforestation=15.0, pollution=25.0),
        spatial_context=SpatialContext(latitude=10.0, longitude=77.0, region="Southern Western Ghats", ecosystem="agroecosystems"),
    )

    request = InterventionEngineRequest(state=state, max_recommendations=5)

    run_1 = engine.generate_recommendations(request)
    run_2 = engine.generate_recommendations(request)

    assert run_1.total_recommendations == run_2.total_recommendations
    assert len(run_1.recommendations) == len(run_2.recommendations)

    for r1, r2 in zip(run_1.recommendations, run_2.recommendations):
        assert r1.intervention_id == r2.intervention_id
        assert r1.relevance_rank == r2.relevance_rank
        assert r1.confidence_basis.overall_confidence == r2.confidence_basis.overall_confidence
        assert r1.what_to_do == r2.what_to_do


# --------------------------------------------------------------------------
# 9. Test API Endpoints
# --------------------------------------------------------------------------
def test_api_endpoints(client):
    """Test /api/v1/interventions/catalogue, /{id}, and /recommend endpoints."""
    # 1. Catalogue
    cat_resp = client.get("/api/v1/interventions/catalogue")
    assert cat_resp.status_code == 200
    catalogue = cat_resp.json()
    assert len(catalogue) >= 10
    intervention_ids = [i["id"] for i in catalogue]
    assert "INT_NATIVE_VEGETATION_RESTORATION" in intervention_ids
    assert "INT_AGROFORESTRY_SYSTEMS" in intervention_ids
    assert "INT_SOIL_COVER_PRACTICES" in intervention_ids
    assert "INT_RIPARIAN_BUFFERS" in intervention_ids

    # 2. Get by ID
    id_resp = client.get("/api/v1/interventions/INT_AGROFORESTRY_SYSTEMS")
    assert id_resp.status_code == 200
    item = id_resp.json()
    assert item["id"] == "INT_AGROFORESTRY_SYSTEMS"
    assert "Multi-Strata Agroforestry" in item["name"]

    # 3. Get 404 for invalid ID
    bad_id_resp = client.get("/api/v1/interventions/INT_NON_EXISTENT_999")
    assert bad_id_resp.status_code == 404

    # 4. Recommend POST
    rec_payload = {
        "state": {
            "soil": {"ph": 6.5, "organic_carbon": 0.9, "moisture": 12.0},
            "land": {"land_use": "cropland", "land_cover": "sparse_vegetation"},
            "climate": {"temperature": 28.0, "rainfall": 650.0},
            "biodiversity": {"species_richness": 18.0, "habitat_diversity": 35.0},
            "human_impact": {"deforestation": 5.0, "pollution": 15.0},
            "spatial_context": {
                "latitude": 15.5,
                "longitude": 75.0,
                "region": "Semi-Arid Deccan",
                "ecosystem": "agroecosystems",
            },
        },
        "findings": [],
        "conflicts": [],
        "max_recommendations": 3,
        "min_confidence_threshold": 0.40,
        "allow_experimental": False,
    }

    rec_resp = client.post("/api/v1/interventions/recommend", json=rec_payload)
    assert rec_resp.status_code == 200
    rec_data = rec_resp.json()
    assert "recommendations" in rec_data
    assert rec_data["total_recommendations"] >= 1
    assert rec_data["recommendations"][0]["relevance_rank"] == 1


# --------------------------------------------------------------------------
# 10. Phase 11 Explainability & Feasibility Scenarios
# --------------------------------------------------------------------------
def test_phase11_complete_data(engine):
    """Test 1: Complete data scenario."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=6.5, organic_carbon=2.1, moisture=22.0),
        land=LandMetrics(land_use="cropland", land_cover="vegetated"),
        climate=ClimateMetrics(temperature=24.0, rainfall=1100.0),
        biodiversity=BiodiversityMetrics(species_richness=45.0, habitat_diversity=65.0),
        human_impact=HumanImpactMetrics(deforestation=2.0, pollution=5.0),
        spatial_context=SpatialContext(latitude=12.0, longitude=75.0, region="Western Ghats", ecosystem="agroecosystems"),
    )
    request = InterventionEngineRequest(state=state, max_recommendations=3)
    response = engine.generate_recommendations(request)
    assert response.total_recommendations >= 1
    top = response.recommendations[0]
    assert top.confidence_basis.data_completeness_factor >= 0.90
    assert top.explanation_chain is not None
    assert len(top.explanation_chain.observed_facts) >= 5
    assert top.feasibility is not None
    assert top.feasibility.status in ["Suitable", "Conditionally suitable"]
    assert len(top.impacted_metrics) >= 1


def test_phase11_partial_data(engine):
    """Test 2: Partial data scenario."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=6.0, organic_carbon=None, moisture=None),
        land=LandMetrics(land_use="cropland", land_cover=None),
        climate=ClimateMetrics(temperature=26.0, rainfall=None),
        biodiversity=BiodiversityMetrics(species_richness=None, habitat_diversity=30.0),
        human_impact=HumanImpactMetrics(deforestation=None, pollution=None),
        spatial_context=SpatialContext(region="Deccan", ecosystem="agroecosystems"),
    )
    request = InterventionEngineRequest(state=state, max_recommendations=3)
    response = engine.generate_recommendations(request)
    assert response.total_recommendations >= 1
    top = response.recommendations[0]
    assert top.confidence_basis.data_completeness_factor < 0.90
    assert top.explanation_chain is not None
    assert top.feasibility is not None


def test_phase11_unsuitable_climate(engine):
    """Test 3: Unsuitable climate scenario."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=8.5, organic_carbon=0.2, moisture=3.0),
        land=LandMetrics(land_use="rangeland", land_cover="bare"),
        climate=ClimateMetrics(temperature=42.0, rainfall=80.0),
        biodiversity=BiodiversityMetrics(species_richness=5.0, habitat_diversity=10.0),
        human_impact=HumanImpactMetrics(deforestation=0.0, pollution=2.0),
        spatial_context=SpatialContext(ecosystem="hyper_arid_desert_sand_sheet"),
    )
    request = InterventionEngineRequest(state=state, max_recommendations=5)
    response = engine.generate_recommendations(request)
    # High water / vegetation interventions should be excluded
    assert "INT_WETLAND_RESTORATION" in response.excluded_interventions


def test_phase11_insufficient_information(engine):
    """Test 4: Insufficient information scenario."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=None, organic_carbon=None, moisture=None),
        land=LandMetrics(land_use=None, land_cover=None),
        climate=ClimateMetrics(temperature=None, rainfall=None),
        biodiversity=BiodiversityMetrics(species_richness=None, habitat_diversity=None),
        human_impact=HumanImpactMetrics(deforestation=None, pollution=None),
        spatial_context=SpatialContext(region=None, ecosystem=None),
    )
    request = InterventionEngineRequest(state=state, max_recommendations=3)
    response = engine.generate_recommendations(request)
    if response.recommendations:
        top = response.recommendations[0]
        assert top.feasibility.status in ["Insufficient information", "Conditionally suitable"]


def test_phase11_geographic_mismatch(engine):
    """Test 5: Geographic mismatch scenario."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=4.5, organic_carbon=5.0, moisture=45.0),
        land=LandMetrics(land_use="intact_primary_forest", land_cover="dense"),
        climate=ClimateMetrics(temperature=22.0, rainfall=2500.0),
        biodiversity=BiodiversityMetrics(species_richness=90.0, habitat_diversity=95.0),
        human_impact=HumanImpactMetrics(deforestation=0.0, pollution=0.0),
        spatial_context=SpatialContext(ecosystem="tropical_forest"),
    )
    request = InterventionEngineRequest(state=state, max_recommendations=3)
    response = engine.generate_recommendations(request)
    assert "INT_AGROFORESTRY_SYSTEMS" in response.excluded_interventions


def test_phase11_multiple_pressures(engine):
    """Test 6: Multiple pressures scenario."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=4.2, organic_carbon=0.6, moisture=10.0),
        land=LandMetrics(land_use="cropland", land_cover="fragmented"),
        climate=ClimateMetrics(temperature=28.0, rainfall=500.0),
        biodiversity=BiodiversityMetrics(species_richness=10.0, habitat_diversity=20.0),
        human_impact=HumanImpactMetrics(deforestation=40.0, pollution=50.0),
        spatial_context=SpatialContext(ecosystem="agroecosystems"),
    )
    findings = [
        EcologicalFinding(
            finding_id="FIND_1",
            title="Severe Soil Degradation",
            domain="soil",
            severity=NaturePressureSeverity.CRITICAL,
            contributing_variables=["soil.organic_carbon", "soil.ph"],
            variable_details=[],
            inferred_pressure="soil_organic_carbon_depletion",
            ecological_mechanism="Low carbon and acidity.",
            supporting_relationships=[],
            confidence=0.9,
            geographic_relevance="global",
        ),
        EcologicalFinding(
            finding_id="FIND_2",
            title="Habitat Fragmentation",
            domain="biodiversity",
            severity=NaturePressureSeverity.HIGH,
            contributing_variables=["human_impact.deforestation"],
            variable_details=[],
            inferred_pressure="habitat_fragmentation",
            ecological_mechanism="Forest clearing.",
            supporting_relationships=[],
            confidence=0.88,
            geographic_relevance="global",
        ),
    ]
    request = InterventionEngineRequest(state=state, findings=findings, max_recommendations=5)
    response = engine.generate_recommendations(request)
    assert response.total_recommendations >= 2
    for rec in response.recommendations:
        assert rec.explanation_chain is not None
        assert rec.feasibility is not None


def test_phase11_missing_evidence(engine):
    """Test 7: Missing evidence scenario (fallback handling)."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=6.5, organic_carbon=1.0, moisture=15.0),
        land=LandMetrics(land_use="cropland", land_cover="sparse"),
        climate=ClimateMetrics(temperature=25.0, rainfall=700.0),
        biodiversity=BiodiversityMetrics(species_richness=20.0, habitat_diversity=35.0),
        human_impact=HumanImpactMetrics(deforestation=5.0, pollution=10.0),
    )
    request = InterventionEngineRequest(state=state, max_recommendations=3)
    response = engine.generate_recommendations(request)
    for rec in response.recommendations:
        assert rec.evidence is not None
        assert rec.explanation_chain.scientific_evidence_summary is not None


def test_phase11_conflicting_observations(engine):
    """Test 8: Conflicting observations scenario."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=6.5, organic_carbon=1.2, moisture=18.0),
        land=LandMetrics(land_use="cropland", land_cover="sparse"),
        climate=ClimateMetrics(temperature=25.0, rainfall=800.0),
        biodiversity=BiodiversityMetrics(species_richness=25.0, habitat_diversity=40.0),
        human_impact=HumanImpactMetrics(deforestation=5.0, pollution=10.0),
    )
    conflict = ConflictReport(
        conflict_id="CONF_1",
        conflict_type=ConflictType.USER_DATASET_DISCREPANCY,
        variables_involved=["soil.organic_carbon"],
        user_value=1.2,
        dataset_value=0.4,
        delta_percentage=66.0,
        message="User carbon 1.2% conflicts with dataset 0.4%.",
        resolution_strategy=ConflictResolutionStrategy.USER_PREFERRED_WITH_UNCERTAINTY,
        uncertainty_penalty=0.20,
    )
    request = InterventionEngineRequest(state=state, findings=[], conflicts=[conflict])
    response = engine.generate_recommendations(request)
    assert response.total_recommendations >= 1
    top = response.recommendations[0]
    assert top.confidence_basis.conflict_uncertainty_penalty == 0.20


# --------------------------------------------------------------------------
# 11. Phase 12 Scientific Validation & Ecological Risk Tests
# --------------------------------------------------------------------------
def test_phase12_supported_claim(engine):
    """Test 1: Supported scientific claim validation."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=6.5, organic_carbon=2.0, moisture=25.0),
        land=LandMetrics(land_use="degraded_forest", land_cover="vegetated"),
        climate=ClimateMetrics(temperature=24.0, rainfall=1200.0),
        biodiversity=BiodiversityMetrics(species_richness=40.0, habitat_diversity=60.0),
        human_impact=HumanImpactMetrics(deforestation=5.0, pollution=5.0),
        spatial_context=SpatialContext(ecosystem="tropical_forest"),
    )
    request = InterventionEngineRequest(state=state, max_recommendations=3)
    response = engine.generate_recommendations(request)
    assert response.total_recommendations >= 1
    top = response.recommendations[0]
    assert top.validation is not None
    assert len(top.validation.validated_claims) >= 1
    assert any(c.is_supported for c in top.validation.validated_claims)
    assert top.validation.evidence_support_summary is not None


def test_phase12_unsupported_claim_softening(engine):
    """Test 2: Unsupported claim softening and uncertainty preservation."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=6.5, organic_carbon=1.0, moisture=15.0),
        land=LandMetrics(land_use="cropland", land_cover="sparse"),
        climate=ClimateMetrics(temperature=25.0, rainfall=600.0),
        biodiversity=BiodiversityMetrics(species_richness=20.0, habitat_diversity=30.0),
        human_impact=HumanImpactMetrics(deforestation=10.0, pollution=15.0),
    )
    request = InterventionEngineRequest(state=state, max_recommendations=3)
    response = engine.generate_recommendations(request)
    for rec in response.recommendations:
        assert rec.validation.uncertainty_statement is not None
        for claim in rec.validation.validated_claims:
            if not claim.evidence_backed:
                assert claim.validation_status in ["Softened due to uncertainty", "Removed (unsupported)"]


def test_phase12_quantitative_claim_handling(engine):
    """Test 3: Quantitative claim handling without direct evidence."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=6.5, organic_carbon=1.5, moisture=20.0),
        land=LandMetrics(land_use="cropland", land_cover="sparse"),
        climate=ClimateMetrics(temperature=24.0, rainfall=900.0),
        biodiversity=BiodiversityMetrics(species_richness=30.0, habitat_diversity=50.0),
        human_impact=HumanImpactMetrics(deforestation=5.0, pollution=5.0),
    )
    request = InterventionEngineRequest(state=state, max_recommendations=3)
    response = engine.generate_recommendations(request)
    for rec in response.recommendations:
        for claim in rec.validation.validated_claims:
            if claim.claim_type == "quantitative":
                assert claim.uncertainty_preserved is True


def test_phase12_conflicting_evidence_resolution(engine):
    """Test 4: Conflicting evidence handling and audit trail."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=6.0, organic_carbon=1.5, moisture=20.0),
        land=LandMetrics(land_use="cropland", land_cover="sparse"),
        climate=ClimateMetrics(temperature=24.0, rainfall=900.0),
        biodiversity=BiodiversityMetrics(species_richness=30.0, habitat_diversity=50.0),
        human_impact=HumanImpactMetrics(deforestation=5.0, pollution=5.0),
    )
    conflict = ConflictReport(
        conflict_id="CONF_99",
        conflict_type=ConflictType.USER_DATASET_DISCREPANCY,
        variables_involved=["soil.ph"],
        user_value=6.0,
        dataset_value=4.5,
        delta_percentage=33.0,
        message="Conflicting soil pH observations.",
        resolution_strategy=ConflictResolutionStrategy.USER_PREFERRED_WITH_UNCERTAINTY,
        uncertainty_penalty=0.15,
    )
    request = InterventionEngineRequest(state=state, conflicts=[conflict], max_recommendations=3)
    response = engine.generate_recommendations(request)
    top = response.recommendations[0]
    assert len(top.validation.conflict_resolution_notes) >= 1
    assert any("Conflicting soil pH" in note for note in top.validation.conflict_resolution_notes)


def test_phase12_missing_evidence_fallback(engine):
    """Test 5: Missing evidence fallback handling."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=7.0, organic_carbon=2.0, moisture=25.0),
        land=LandMetrics(land_use="cropland", land_cover="vegetated"),
        climate=ClimateMetrics(temperature=22.0, rainfall=1000.0),
        biodiversity=BiodiversityMetrics(species_richness=50.0, habitat_diversity=70.0),
        human_impact=HumanImpactMetrics(deforestation=2.0, pollution=2.0),
    )
    request = InterventionEngineRequest(state=state, max_recommendations=3)
    response = engine.generate_recommendations(request)
    for rec in response.recommendations:
        assert rec.validation.evidence_support_summary is not None


def test_phase12_context_specific_tradeoffs(engine):
    """Test 6: Context-specific trade-offs based on state constraints."""
    # Semi-arid state with acidic soil
    state = EnvironmentalState(
        soil=SoilMetrics(ph=4.5, organic_carbon=0.8, moisture=10.0),
        land=LandMetrics(land_use="cropland", land_cover="sparse"),
        climate=ClimateMetrics(temperature=32.0, rainfall=400.0),
        biodiversity=BiodiversityMetrics(species_richness=15.0, habitat_diversity=25.0),
        human_impact=HumanImpactMetrics(deforestation=20.0, pollution=15.0),
        spatial_context=SpatialContext(ecosystem="agroecosystems"),
    )
    request = InterventionEngineRequest(state=state, max_recommendations=3)
    response = engine.generate_recommendations(request)
    top = response.recommendations[0]
    assert top.validation.context_specific_tradeoffs is not None
    # Should contain water limitation or soil acidity constraint trade-offs
    tradeoffs_str = " ".join(top.validation.context_specific_tradeoffs).lower()
    assert "water" in tradeoffs_str or "acidity" in tradeoffs_str or "constraint" in tradeoffs_str


def test_phase12_uncertain_conclusion(engine):
    """Test 7: Uncertain conclusion and boundary preservation."""
    state = EnvironmentalState(
        soil=SoilMetrics(ph=6.5, organic_carbon=1.5, moisture=20.0),
        land=LandMetrics(land_use="cropland", land_cover="sparse"),
        climate=ClimateMetrics(temperature=25.0, rainfall=800.0),
        biodiversity=BiodiversityMetrics(species_richness=30.0, habitat_diversity=50.0),
        human_impact=HumanImpactMetrics(deforestation=5.0, pollution=5.0),
    )
    request = InterventionEngineRequest(state=state, max_recommendations=3)
    response = engine.generate_recommendations(request)
    for rec in response.recommendations:
        assert rec.validation.uncertainty_statement is not None
        assert "microclimatic variability" in rec.validation.uncertainty_statement

