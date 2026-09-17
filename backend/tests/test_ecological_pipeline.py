"""Comprehensive test suite for Phase 9: Data Integration and Ecological Reasoning Pipeline."""

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.schemas.environmental_state import (
    EnvironmentalState,
    SoilState,
    LandState,
    BiodiversityState,
    ClimateState,
    HumanImpactState,
    SpatialContext,
)
from backend.app.schemas.ecological_findings import (
    EcologicalFindingsRequest,
    ObservationSource,
    ConflictType,
)
from backend.app.schemas.knowledge import VariableObservationState
from backend.app.knowledge.text_extractor import text_extractor
from backend.app.knowledge.conflict_detector import conflict_detector
from backend.app.knowledge.pipeline_service import get_findings_pipeline_service

client = TestClient(app)


# ==============================================================================
# 1. Text Extractor Tests
# ==============================================================================

def test_text_extractor_comprehensive_parsing():
    """Verify regex & semantic extraction of numeric and categorical environmental variables."""
    query = (
        "Site in Western Ghats tropical rainforest at lat: 12.5, lon: 75.4. "
        "Soil pH is 5.2, organic carbon 3.4%, moisture 22%. "
        "Ambient temperature 29.5°C and annual rainfall of 2400 mm. "
        "Species richness of 48 species and habitat diversity of 65%. "
        "Monoculture land use with deforestation of 18% and chemical pollution index 42."
    )
    state, extracted_map = text_extractor.extract_from_text(query)

    assert extracted_map["soil.ph"] == 5.2
    assert extracted_map["soil.organic_carbon"] == 3.4
    assert extracted_map["soil.moisture"] == 22.0
    assert extracted_map["climate.temperature"] == 29.5
    assert extracted_map["climate.rainfall"] == 2400.0
    assert extracted_map["biodiversity.species_richness"] == 48
    assert extracted_map["biodiversity.habitat_diversity"] == 65.0
    assert extracted_map["land.land_use"] == "monoculture"
    assert extracted_map["human_impact.deforestation"] == 18.0
    assert extracted_map["human_impact.pollution"] == 42.0
    assert extracted_map["spatial_context.latitude"] == 12.5
    assert extracted_map["spatial_context.longitude"] == 75.4
    assert extracted_map["spatial_context.region"] == "Western Ghats"
    assert extracted_map["spatial_context.ecosystem"] == "tropical_forest"

    # Canonical state validation
    assert state.soil.ph == 5.2
    assert state.climate.rainfall == 2400.0
    assert state.spatial_context.region == "Western Ghats"


def test_text_extractor_empty_and_partial():
    """Verify graceful handling of empty or partial text."""
    state_empty, map_empty = text_extractor.extract_from_text("")
    assert len(map_empty) == 0
    assert state_empty.soil.ph is None

    state_partial, map_partial = text_extractor.extract_from_text("Acidic soil with pH 4.8 and temp 32C.")
    assert map_partial["soil.ph"] == 4.8
    assert map_partial["climate.temperature"] == 32.0
    assert "climate.rainfall" not in map_partial
    assert state_partial.climate.rainfall is None


# ==============================================================================
# 2. Multi-Metric Deterministic Reasoning (3+ Variables)
# ==============================================================================

def test_pipeline_water_climate_stress_reasoning():
    """Verify multi-metric reasoning across rainfall + soil.moisture + temperature."""
    req = EcologicalFindingsRequest(
        state=EnvironmentalState(
            climate=ClimateState(rainfall=350.0, temperature=34.0),
            soil=SoilState(moisture=8.0, ph=7.2, organic_carbon=1.2),
            spatial_context=SpatialContext(ecosystem="semi_arid", region="East Africa"),
        ),
        enrich_from_datasets=False,
    )
    service = get_findings_pipeline_service()
    res = service.process_request(req)

    assert res.total_findings_count > 0
    # Check for Thermal-Hydro Drought finding
    drought_finding = next(
        (f for f in res.findings if "Drought" in f.title or "Water-Climate" in f.title or "Thermal" in f.title),
        None,
    )
    assert drought_finding is not None
    assert "climate.rainfall" in drought_finding.contributing_variables
    assert "soil.moisture" in drought_finding.contributing_variables
    assert "climate.temperature" in drought_finding.contributing_variables
    assert len(drought_finding.contributing_variables) >= 3
    assert len(drought_finding.evidence_references) > 0
    assert drought_finding.confidence >= 0.80


def test_pipeline_soil_acidity_carbon_depletion_reasoning():
    """Verify multi-metric reasoning across soil.ph + soil.organic_carbon + soil.moisture."""
    req = EcologicalFindingsRequest(
        state=EnvironmentalState(
            soil=SoilState(ph=4.6, organic_carbon=0.8, moisture=14.0),
            spatial_context=SpatialContext(ecosystem="tropical_forest"),
        ),
        enrich_from_datasets=False,
    )
    service = get_findings_pipeline_service()
    res = service.process_request(req)

    soil_finding = next(
        (f for f in res.findings if "Soil Acidity" in f.title or "Inertia" in f.title),
        None,
    )
    assert soil_finding is not None
    assert "soil.ph" in soil_finding.contributing_variables
    assert "soil.organic_carbon" in soil_finding.contributing_variables
    assert soil_finding.severity in ("high", "critical")
    assert "al3+" in soil_finding.ecological_mechanism.lower() or "microbe" in soil_finding.ecological_mechanism.lower()


def test_pipeline_agro_homogenization_reasoning():
    """Verify multi-metric reasoning across land_use + land_cover + species_richness + habitat_diversity."""
    req = EcologicalFindingsRequest(
        state=EnvironmentalState(
            land=LandState(land_use="monoculture", land_cover="cropland"),
            biodiversity=BiodiversityState(species_richness=12, habitat_diversity=15.0),
        ),
        enrich_from_datasets=False,
    )
    service = get_findings_pipeline_service()
    res = service.process_request(req)

    agro_finding = next(
        (f for f in res.findings if "Agro-Landscape" in f.title or "Homogenization" in f.title),
        None,
    )
    assert agro_finding is not None
    assert "land.land_use" in agro_finding.contributing_variables
    assert "biodiversity.species_richness" in agro_finding.contributing_variables
    assert "biodiversity.habitat_diversity" in agro_finding.contributing_variables
    assert len(agro_finding.contributing_variables) >= 3


# ==============================================================================
# 3. Dataset Integration & Provenance Tracking
# ==============================================================================

def test_pipeline_dataset_enrichment_and_provenance():
    """Verify that coordinates trigger authoritative dataset enrichment and variable provenance."""
    # Western Ghats coordinates
    req = EcologicalFindingsRequest(
        latitude=12.5,
        longitude=75.4,
        enrich_from_datasets=True,
    )
    service = get_findings_pipeline_service()
    res = service.process_request(req)

    # State should be enriched from SoilGrids, WorldClim, Copernicus, etc.
    assert res.canonical_state.soil.ph is not None
    assert res.canonical_state.climate.rainfall is not None
    assert res.dataset_derived_metrics_count > 0
    assert len(res.provenance_map) > 0

    # SoilGrids provenance verification
    soil_prov = res.provenance_map.get("soil.ph")
    assert soil_prov is not None
    assert soil_prov.dataset_id == "soilgrids_isric"
    assert "ISRIC" in soil_prov.source_organization

    # Climate provenance verification
    climate_prov = res.provenance_map.get("climate.rainfall")
    assert climate_prov is not None
    assert climate_prov.dataset_id == "worldclim_v2"


def test_pipeline_user_vs_dataset_distinction():
    """Verify strict separation between user-supplied and dataset-derived variables."""
    # User provides soil pH 6.0, leaving climate rainfall empty
    req = EcologicalFindingsRequest(
        latitude=12.5,
        longitude=75.4,
        state=EnvironmentalState(
            soil=SoilState(ph=6.0),
        ),
        enrich_from_datasets=True,
        overwrite_user_values=False,
    )
    service = get_findings_pipeline_service()
    res = service.process_request(req)

    # User soil pH should be preserved (6.0), rainfall enriched from dataset
    assert res.canonical_state.soil.ph == 6.0
    assert res.observed_user_metrics_count >= 1
    assert res.dataset_derived_metrics_count >= 1

    # Check detail sources in findings
    for finding in res.findings:
        for detail in finding.variable_details:
            if detail.variable_id == "soil.ph":
                assert detail.source == ObservationSource.USER_SUPPLIED
                assert detail.value == 6.0


# ==============================================================================
# 4. Conflict & Uncertainty Detection
# ==============================================================================

def test_conflict_detection_user_vs_dataset_discrepancy():
    """Verify that a large numeric divergence between user and dataset is flagged with penalty."""
    # Western Ghats baseline soil pH is ~5.4; user provides 8.5 (delta > 3.0 pH)
    req = EcologicalFindingsRequest(
        latitude=12.5,
        longitude=75.4,
        state=EnvironmentalState(
            soil=SoilState(ph=8.5),
        ),
        enrich_from_datasets=True,
        overwrite_user_values=False,
    )
    service = get_findings_pipeline_service()
    res = service.process_request(req)

    assert res.has_conflicts is True
    assert len(res.conflicts_detected) > 0

    ph_conflict = next(
        (c for c in res.conflicts_detected if "soil.ph" in c.variables_involved),
        None,
    )
    assert ph_conflict is not None
    assert ph_conflict.conflict_type == ConflictType.USER_DATASET_DISCREPANCY
    assert ph_conflict.user_value == 8.5
    assert ph_conflict.uncertainty_penalty > 0.0


def test_conflict_detection_geographic_mismatch():
    """Verify that claiming a tropical forest in Polar coordinates triggers geographic mismatch."""
    req = EcologicalFindingsRequest(
        latitude=78.2,
        longitude=15.6,
        ecosystem="tropical_forest",
        enrich_from_datasets=False,
    )
    service = get_findings_pipeline_service()
    res = service.process_request(req)

    assert res.has_conflicts is True
    geo_conflict = next(
        (c for c in res.conflicts_detected if c.conflict_type == ConflictType.GEOGRAPHIC_MISMATCH),
        None,
    )
    assert geo_conflict is not None
    assert "polar" in geo_conflict.message.lower() or "arctic" in geo_conflict.message.lower()


# ==============================================================================
# 5. Missing Data & Unknown Handling
# ==============================================================================

def test_missing_data_distinguishes_zero_from_unknown():
    """Verify that null variables remain UNKNOWN and do not trigger false zero alerts."""
    # State with valid 0 deforestation vs unknown pollution
    req = EcologicalFindingsRequest(
        state=EnvironmentalState(
            human_impact=HumanImpactState(deforestation=0.0, pollution=None),
        ),
        enrich_from_datasets=False,
    )
    service = get_findings_pipeline_service()
    res = service.process_request(req)

    # Deforestation is observed (0.0), pollution is unknown (None)
    assert res.unknown_metrics_count > 0

    defor_status = next(v for v in res.variables_status if v.metric_id == "human_impact.deforestation")
    assert defor_status.status == VariableObservationState.OBSERVED
    assert defor_status.observed_value == 0.0

    poll_status = next(v for v in res.variables_status if v.metric_id == "human_impact.pollution")
    assert poll_status.status == VariableObservationState.UNKNOWN
    assert poll_status.observed_value is None


# ==============================================================================
# 6. Deterministic Consistency & RAG Grounding
# ==============================================================================

def test_deterministic_reasoning_repeatability():
    """Verify that multiple executions on identical state produce identical findings."""
    req = EcologicalFindingsRequest(
        state=EnvironmentalState(
            climate=ClimateState(rainfall=400.0, temperature=33.0),
            soil=SoilState(moisture=10.0),
        ),
        enrich_from_datasets=False,
    )
    service = get_findings_pipeline_service()
    res1 = service.process_request(req)
    res2 = service.process_request(req)

    assert len(res1.findings) == len(res2.findings)
    assert res1.findings[0].finding_id == res2.findings[0].finding_id
    assert res1.findings[0].confidence == res2.findings[0].confidence
    assert res1.overall_confidence_score == res2.overall_confidence_score


# ==============================================================================
# 7. End-to-End FastAPI API Endpoints
# ==============================================================================

def test_api_ecological_findings_from_text():
    """Test POST /api/v1/reasoning/ecological-findings with free-form text."""
    payload = {
        "text_description": "Degraded agricultural plot in Western Ghats at lat 12.5, lon 75.4 with soil pH 5.0, rainfall 500mm, organic carbon 0.9%, temperature 32C.",
        "enrich_from_datasets": True,
        "overwrite_user_values": False,
        "top_k_evidence": 4,
    }
    resp = client.post("/api/v1/reasoning/ecological-findings", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["canonical_state"]["soil"]["ph"] == 5.0
    assert data["total_findings_count"] > 0
    assert len(data["findings"]) > 0
    assert "evidence_references" in data["findings"][0]
    assert len(data["findings"][0]["evidence_references"]) <= 4


def test_api_extract_state_endpoint():
    """Test POST /api/v1/reasoning/extract-state."""
    payload = {
        "text": "Intensive monoculture site with pH 5.8, temperature 31C, and 20% deforestation."
    }
    resp = client.post("/api/v1/reasoning/extract-state", json=payload)
    assert resp.status_code == 200
    data = resp.json()

    assert data["variables_count"] >= 3
    assert data["extracted_variables"]["soil.ph"] == 5.8
    assert data["extracted_variables"]["climate.temperature"] == 31.0
    assert data["extracted_variables"]["human_impact.deforestation"] == 20.0
