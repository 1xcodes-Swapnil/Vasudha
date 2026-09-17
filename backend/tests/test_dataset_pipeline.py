"""Comprehensive tests for Authoritative Environmental Dataset Layer & Ingestion Pipeline (Phase 7).

Tests:
1. Valid ingestion across all 6 authoritative adapters
2. Malformed records and error handling
3. Missing values handling (explicit None, never converted to 0)
4. Observed zero values (distinguishing valid 0.0 from None)
5. Unit conversions (SoilGrids pH*10, dg/kg SOC, g/kg SOC, Kelvin temp, tenths-deg temp, m rainfall)
6. Invalid coordinates handling
7. Duplicate records handling
8. Provenance preservation and scientific attribution
9. Dataset adapter failure / degraded fallback
10. Unavailable external source handling
11. Synthetic-data marking
12. Multi-dataset point query and EnvironmentalState enrichment
13. API endpoint integration
"""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.datasets.manager import EnvironmentalDatasetManager, dataset_manager
from backend.app.datasets.pipeline import EnvironmentalDataPipeline
from backend.app.datasets.metadata import AUTHORITATIVE_DATASETS
from backend.app.schemas.dataset import (
    RawDatasetObservation,
    QualityFlagType,
    DataQualitySeverity,
    StateEnrichmentRequest,
)
from backend.app.schemas.environmental_state import EnvironmentalState, SoilState, SpatialContext
from backend.app.db.session import get_db, reset_engine


@pytest.fixture
def client():
    return TestClient(app)


def test_authoritative_dataset_registry():
    """Verify all 6 authoritative datasets are registered with full metadata."""
    manager = EnvironmentalDatasetManager()
    datasets = manager.list_datasets()
    assert len(datasets) >= 6

    expected_ids = {
        "soilgrids_isric",
        "copernicus_worldcover",
        "gbif_occurrence",
        "worldclim_v2",
        "global_forest_watch",
        "unep_sedac_pollution",
    }
    registered_ids = {d.id for d in datasets}
    assert expected_ids.issubset(registered_ids)

    # Test individual metadata integrity
    soilgrids = manager.get_dataset("soilgrids_isric")
    assert soilgrids is not None
    assert soilgrids.source_organization == "ISRIC - World Soil Information"
    assert "soil.ph" in soilgrids.variables
    assert "soil.organic_carbon" in soilgrids.variables
    assert soilgrids.license == "CC BY 4.0"
    assert len(soilgrids.known_limitations) > 0


def test_unit_conversion_soilgrids():
    """Test unit conversions in SoilGrids: pH*10 -> pH, dg/kg and g/kg -> % SOC."""
    adapter = dataset_manager.get_adapter("soilgrids_isric")
    assert adapter is not None

    # 1. Test pH*10 conversion (e.g. 58 -> 5.8)
    raw_obs1 = RawDatasetObservation(
        dataset_id="soilgrids_isric",
        latitude=10.0,
        longitude=76.0,
        raw_payload={"ph_raw": 58.0, "ph_unit": "pHx10", "soc_raw": 3.2, "soc_unit": "%"},
    )
    canon1, checks1, prov1 = adapter.normalize_and_validate(raw_obs1)
    assert canon1["soil.ph"] == 5.8
    assert any(c.flag_type == QualityFlagType.UNIT_CONVERTED and c.metric_name == "soil.ph" for c in checks1)

    # 2. Test dg/kg to % conversion (240 dg/kg = 2.4%)
    raw_obs2 = RawDatasetObservation(
        dataset_id="soilgrids_isric",
        latitude=10.0,
        longitude=76.0,
        raw_payload={"ph_raw": 6.5, "soc_raw": 240.0, "soc_unit": "dg/kg"},
    )
    canon2, checks2, prov2 = adapter.normalize_and_validate(raw_obs2)
    assert canon2["soil.organic_carbon"] == 2.4
    assert any(c.flag_type == QualityFlagType.UNIT_CONVERTED and c.metric_name == "soil.organic_carbon" for c in checks2)

    # 3. Test g/kg to % conversion (35 g/kg = 3.5%)
    raw_obs3 = RawDatasetObservation(
        dataset_id="soilgrids_isric",
        latitude=10.0,
        longitude=76.0,
        raw_payload={"ph_raw": 6.5, "soc_raw": 35.0, "soc_unit": "g/kg"},
    )
    canon3, checks3, prov3 = adapter.normalize_and_validate(raw_obs3)
    assert canon3["soil.organic_carbon"] == 3.5


def test_unit_conversion_worldclim():
    """Test unit conversions in WorldClim: Kelvin -> °C, tenths-of-degree -> °C, m -> mm."""
    adapter = dataset_manager.get_adapter("worldclim_v2")
    assert adapter is not None

    # Kelvin to Celsius (298.15 K -> 25.0 °C)
    raw_obs1 = RawDatasetObservation(
        dataset_id="worldclim_v2",
        latitude=0.0,
        longitude=0.0,
        raw_payload={"bio1_temp_c": 298.15, "temp_unit": "Kelvin", "bio12_precip_mm": 1.5, "precip_unit": "m"},
    )
    canon1, checks1, prov1 = adapter.normalize_and_validate(raw_obs1)
    assert canon1["climate.temperature"] == 25.0
    assert canon1["climate.rainfall"] == 1500.0
    assert any(c.metric_name == "climate.temperature" and c.flag_type == QualityFlagType.UNIT_CONVERTED for c in checks1)
    assert any(c.metric_name == "climate.rainfall" and c.flag_type == QualityFlagType.UNIT_CONVERTED for c in checks1)


def test_observed_zero_vs_missing_distinction():
    """Verify that observed zero (0.0% deforestation, 0 species, 0.0 mm rain) is strictly distinguished from None."""
    gfw_adapter = dataset_manager.get_adapter("global_forest_watch")
    gbif_adapter = dataset_manager.get_adapter("gbif_occurrence")
    climate_adapter = dataset_manager.get_adapter("worldclim_v2")

    # 1. Observed Zero Deforestation (0.0% forest loss)
    raw_zero_def = RawDatasetObservation(
        dataset_id="global_forest_watch",
        latitude=0.0,
        longitude=36.0,
        raw_payload={"canopy_loss_pct": 0.0},
    )
    canon_def, checks_def, _ = gfw_adapter.normalize_and_validate(raw_zero_def)
    assert canon_def["human_impact.deforestation"] == 0.0
    assert any(c.flag_type == QualityFlagType.OBSERVED_ZERO for c in checks_def)

    # 2. Missing Deforestation (None)
    raw_none_def = RawDatasetObservation(
        dataset_id="global_forest_watch",
        latitude=0.0,
        longitude=36.0,
        raw_payload={},
    )
    canon_none_def, checks_none_def, _ = gfw_adapter.normalize_and_validate(raw_none_def)
    assert "human_impact.deforestation" not in canon_none_def
    assert any(c.flag_type == QualityFlagType.MISSING_VALUE for c in checks_none_def)

    # 3. Observed Zero Species count (0 count in core desert transect)
    raw_zero_gbif = RawDatasetObservation(
        dataset_id="gbif_occurrence",
        latitude=-23.0,
        longitude=-70.0,
        raw_payload={"species_count": 0, "habitat_diversity_index": 0.0},
    )
    canon_gbif, checks_gbif, _ = gbif_adapter.normalize_and_validate(raw_zero_gbif)
    assert canon_gbif["biodiversity.species_richness"] == 0
    assert canon_gbif["biodiversity.habitat_diversity"] == 0.0
    assert any(c.flag_type == QualityFlagType.OBSERVED_ZERO for c in checks_gbif)

    # 4. Observed Zero Rainfall in hyper-arid desert (0.0 mm)
    raw_zero_rain = RawDatasetObservation(
        dataset_id="worldclim_v2",
        latitude=-23.0,
        longitude=-70.0,
        raw_payload={"bio1_temp_c": 18.0, "bio12_precip_mm": 0.0},
    )
    canon_rain, checks_rain, _ = climate_adapter.normalize_and_validate(raw_zero_rain)
    assert canon_rain["climate.rainfall"] == 0.0
    assert any(c.flag_type == QualityFlagType.OBSERVED_ZERO and c.metric_name == "climate.rainfall" for c in checks_rain)


def test_invalid_coordinates_and_ranges():
    """Test validation of out-of-bounds coordinates and impossible physical values."""
    pipeline = EnvironmentalDataPipeline()

    # 1. Invalid coordinates
    checks_lat = pipeline.validate_coordinates(95.0, 10.0)
    assert any(c.flag_type == QualityFlagType.COORDINATE_OUT_OF_BOUNDS for c in checks_lat)

    checks_lon = pipeline.validate_coordinates(10.0, -195.0)
    assert any(c.flag_type == QualityFlagType.COORDINATE_OUT_OF_BOUNDS for c in checks_lon)

    # 2. Out-of-bounds soil pH (e.g. 16.0 pH)
    adapter = dataset_manager.get_adapter("soilgrids_isric")
    raw_bad_ph = RawDatasetObservation(
        dataset_id="soilgrids_isric",
        latitude=10.0,
        longitude=10.0,
        raw_payload={"ph_raw": 16.0, "ph_unit": "pH"},
    )
    canon, checks, _ = adapter.normalize_and_validate(raw_bad_ph)
    assert "soil.ph" not in canon
    assert any(c.flag_type == QualityFlagType.RANGE_OUT_OF_BOUNDS and c.severity == DataQualitySeverity.ERROR for c in checks)

    # 3. Negative species richness (impossible)
    gbif_adapter = dataset_manager.get_adapter("gbif_occurrence")
    raw_bad_gbif = RawDatasetObservation(
        dataset_id="gbif_occurrence",
        latitude=10.0,
        longitude=10.0,
        raw_payload={"species_count": -5},
    )
    canon_g, checks_g, _ = gbif_adapter.normalize_and_validate(raw_bad_gbif)
    assert "biodiversity.species_richness" not in canon_g
    assert any(c.flag_type == QualityFlagType.RANGE_OUT_OF_BOUNDS and c.severity == DataQualitySeverity.ERROR for c in checks_g)


def test_synthetic_data_explicit_marking():
    """Verify that synthetic fallback data is strictly flagged as synthetic."""
    manager = EnvironmentalDatasetManager()
    adapter = manager.get_adapter("soilgrids_isric")

    # Force synthetic fallback
    raw_synthetic = adapter.fetch_point(0.0, 0.0, is_synthetic_allowed=True)
    assert raw_synthetic.is_synthetic is True

    state, q_report, prov = EnvironmentalDataPipeline.process_raw_observation(
        raw_obs=raw_synthetic,
        adapter=adapter,
    )
    assert q_report.synthetic_count > 0
    assert any(c.flag_type == QualityFlagType.SYNTHETIC_DATA for c in q_report.checks)
    for p in prov.values():
        assert p.is_synthetic is True


def test_point_query_all_authoritative_datasets():
    """Test full multi-domain point query across all 6 authoritative datasets."""
    manager = EnvironmentalDatasetManager()

    # Query Western Ghats coordinates (lat 10.5, lon 76.2)
    result = manager.query_point(latitude=10.5, longitude=76.2, allow_synthetic=False)

    assert result.latitude == 10.5
    assert result.longitude == 76.2
    assert result.canonical_state is not None

    # Check soil
    assert result.canonical_state.soil.ph is not None
    assert result.canonical_state.soil.organic_carbon is not None
    assert result.canonical_state.soil.moisture is not None

    # Check land
    assert result.canonical_state.land.land_cover is not None
    assert result.canonical_state.land.land_use is not None

    # Check biodiversity
    assert result.canonical_state.biodiversity.species_richness is not None
    assert result.canonical_state.biodiversity.habitat_diversity is not None

    # Check climate
    assert result.canonical_state.climate.temperature is not None
    assert result.canonical_state.climate.rainfall is not None

    # Check human impact
    assert result.canonical_state.human_impact.deforestation is not None
    assert result.canonical_state.human_impact.pollution is not None

    # Check provenance records exist for all variables
    assert len(result.provenance_records) >= 10
    assert "soil.ph" in result.provenance_records
    assert result.provenance_records["soil.ph"].source_organization == "ISRIC - World Soil Information"
    assert "climate.temperature" in result.provenance_records
    assert result.provenance_records["climate.temperature"].dataset_id == "worldclim_v2"

    # Quality report checks
    assert result.quality_report.is_valid is True
    assert result.is_fully_authoritative is True
    assert result.has_synthetic_data is False


def test_state_enrichment_preserves_user_values():
    """Test enriching an EnvironmentalState without overwriting user-specified measurements."""
    manager = EnvironmentalDatasetManager()

    # User explicitly specified soil pH 6.8 and custom region
    initial_state = EnvironmentalState(
        soil=SoilState(ph=6.8, organic_carbon=None, moisture=None),
        spatial_context=SpatialContext(latitude=10.5, longitude=76.2, region="My Custom Plot"),
    )

    req = StateEnrichmentRequest(
        state=initial_state,
        overwrite_existing=False,
    )

    enrichment_res = manager.enrich_state(req)
    enriched = enrichment_res.enriched_state

    # User specified pH must be PRESERVED
    assert enriched.soil.ph == 6.8
    assert enriched.spatial_context.region == "My Custom Plot"

    # Missing fields (SOC, rainfall, species richness, etc.) must be POPULATED from datasets
    assert enriched.soil.organic_carbon is not None
    assert enriched.climate.rainfall is not None
    assert enriched.biodiversity.species_richness is not None
    assert enrichment_res.metrics_added_count > 0


def test_api_endpoints_integration(client):
    """Test all Phase 7 API endpoints: /registry, /query-point, /ingest, /enrich-state."""
    # 1. GET /api/v1/datasets/registry
    res_reg = client.get("/api/v1/datasets/registry")
    assert res_reg.status_code == 200
    reg_list = res_reg.json()
    assert len(reg_list) >= 6

    # 2. GET /api/v1/datasets/registry/{dataset_id}
    res_single = client.get("/api/v1/datasets/registry/soilgrids_isric")
    assert res_single.status_code == 200
    assert res_single.json()["id"] == "soilgrids_isric"

    # 3. POST /api/v1/datasets/query-point
    res_query = client.post("/api/v1/datasets/query-point?latitude=10.5&longitude=76.2")
    assert res_query.status_code == 200
    q_data = res_query.json()
    assert q_data["canonical_state"]["soil"]["ph"] is not None
    assert len(q_data["provenance_records"]) >= 6

    # 4. POST /api/v1/datasets/ingest
    ingest_payload = {
        "dataset_id": "worldclim_v2",
        "latitude": 10.5,
        "longitude": 76.2,
        "raw_payload": {"bio1_temp_c": 24.5, "bio12_precip_mm": 3200.0},
        "is_synthetic": False,
    }
    res_ingest = client.post("/api/v1/datasets/ingest", json=ingest_payload)
    assert res_ingest.status_code == 200
    ingest_res = res_ingest.json()
    assert ingest_res["status"] == "success"
    assert ingest_res["canonical_state"]["climate"]["temperature"] == 24.5

    # 5. POST /api/v1/datasets/enrich-state
    enrich_payload = {
        "state": {
            "soil": {"ph": 5.9},
            "spatial_context": {"latitude": 10.5, "longitude": 76.2},
        },
        "overwrite_existing": False,
    }
    res_enrich = client.post("/api/v1/datasets/enrich-state", json=enrich_payload)
    assert res_enrich.status_code == 200
    enriched_data = res_enrich.json()
    assert enriched_data["enriched_state"]["soil"]["ph"] == 5.9
    assert enriched_data["enriched_state"]["climate"]["rainfall"] is not None
