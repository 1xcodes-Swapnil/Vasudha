"""Comprehensive test suite for Scientific Corpus, RAG, and Multi-Metric Ecological Reasoning (Phases 4 & 5)."""

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app
from backend.app.knowledge.rag_service import ScientificRAGService, get_rag_service
from backend.app.knowledge.multi_metric_engine import MultiMetricReasoningEngine, get_multi_metric_engine
from backend.app.schemas.environmental_state import (
    BiodiversityState,
    ClimateState,
    EnvironmentalState,
    HumanImpactState,
    LandState,
    SoilState,
    SpatialContext,
)
from backend.app.schemas.knowledge import EvidenceStrength, VariableObservationState
from backend.app.schemas.scientific_rag import (
    GeographicApplicability,
    NaturePressureSeverity,
    ScientificDocumentCreate,
    ScientificSearchQuery,
    ScientificSourceType,
)


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    return TestClient(app)


@pytest.fixture
def rag_service():
    """Clean ScientificRAGService instance."""
    return get_rag_service()


@pytest.fixture
def multi_metric_engine():
    """Clean MultiMetricReasoningEngine instance."""
    return get_multi_metric_engine()


# ==============================================================================
# 1. SCIENTIFIC CORPUS & CHUNKING TESTS (PHASE 4)
# ==============================================================================

def test_curated_corpus_initialization(rag_service: ScientificRAGService):
    """Verify curated scientific documents and chunks are indexed on startup."""
    docs = rag_service.list_documents()
    assert len(docs) >= 10, f"Expected at least 10 curated documents, found {len(docs)}"

    # Check key authoritative organizations are present
    orgs = {d.organization for d in docs}
    assert "IPCC" in orgs
    assert "IPBES" in orgs
    assert "FAO" in orgs
    assert "UNEP" in orgs

    # Verify document attributes
    for doc in docs:
        assert doc.id.startswith("DOC_")
        assert doc.title
        assert doc.authors
        assert doc.year > 1990
        assert doc.citation
        assert doc.chunk_count > 0


def test_chunk_traceability(rag_service: ScientificRAGService):
    """Verify all chunks retain 100% parent source traceability (citation, DOI, year)."""
    chunks = rag_service.get_document_chunks("DOC_IPCC_WG2_2022_CH2")
    assert len(chunks) >= 2

    for chunk in chunks:
        assert chunk.document_id == "DOC_IPCC_WG2_2022_CH2"
        assert chunk.citation
        assert chunk.doi == "10.1017/9781009325844.004"
        assert len(chunk.content) > 50
        assert chunk.evidence_strength in (EvidenceStrength.CONSENSUS, EvidenceStrength.STRONG)


def test_document_ingestion_validation(rag_service: ScientificRAGService):
    """Verify malformed document ingestion fails gracefully with clear error."""
    # Missing required content
    with pytest.raises(ValueError):
        rag_service.ingest_document(
            ScientificDocumentCreate(
                id="",
                title="",
                authors="Test",
                organization="Test Org",
                year=2023,
                source_type=ScientificSourceType.PEER_REVIEWED_JOURNAL,
                citation="Test citation",
                full_text="",
            )
        )


# ==============================================================================
# 2. TWO-STAGE SEMANTIC RAG RETRIEVAL TESTS (PHASE 4)
# ==============================================================================

def test_semantic_evidence_retrieval_returns_compact_packet(rag_service: ScientificRAGService):
    """Verify search returns a compact, high-signal evidence packet (5-8 chunks)."""
    query = ScientificSearchQuery(
        query="soil organic carbon water retention and biological microbial activity",
        metrics=["soil.organic_carbon", "soil.moisture"],
        top_k=6,
    )
    response = rag_service.search_evidence(query)

    assert not response.insufficient_evidence
    assert 1 <= len(response.evidence_chunks) <= 6
    assert response.selected_count == len(response.evidence_chunks)

    top_chunk = response.evidence_chunks[0]
    assert top_chunk.relevance_score > 0.30
    assert top_chunk.title
    assert top_chunk.citation
    assert top_chunk.content


def test_evidence_strength_filtering(rag_service: ScientificRAGService):
    """Verify min_evidence_strength strictly filters lower-confidence sources."""
    query = ScientificSearchQuery(
        query="biodiversity habitat loss and species extinction",
        min_evidence_strength=EvidenceStrength.CONSENSUS,
        top_k=5,
    )
    response = rag_service.search_evidence(query)

    assert not response.insufficient_evidence
    for chunk in response.evidence_chunks:
        assert chunk.evidence_strength == EvidenceStrength.CONSENSUS


def test_insufficient_evidence_handling(rag_service: ScientificRAGService):
    """Verify empty or out-of-domain queries trigger insufficient_evidence without hallucinating."""
    empty_query = ScientificSearchQuery(query="")
    response = rag_service.search_evidence(empty_query)

    assert response.insufficient_evidence
    assert len(response.evidence_chunks) == 0


def test_geographic_applicability_classification(rag_service: ScientificRAGService):
    """Verify geographic context determines applicability (global vs specific vs mismatched)."""
    # Global study tested against regional query
    query = ScientificSearchQuery(
        query="climate drought vegetation stress",
        ecosystem="tropical_dry_forest",
        geographic_scope="regional_south_asia",
        top_k=5,
    )
    response = rag_service.search_evidence(query)
    assert not response.insufficient_evidence

    # Chunks with global scope are marked GLOBALLY_RELEVANT
    has_global = any(c.geographic_applicability == GeographicApplicability.GLOBALLY_RELEVANT for c in response.evidence_chunks)
    assert has_global


# ==============================================================================
# 3. MULTI-METRIC REASONING ENGINE TESTS (PHASE 5)
# ==============================================================================

def test_thermal_hydro_drought_multi_metric_stress(multi_metric_engine: MultiMetricReasoningEngine):
    """Verify 3-variable reasoning: low rainfall + low soil moisture + high temperature."""
    state = EnvironmentalState(
        climate=ClimateState(temperature=34.5, rainfall=420.0),
        soil=SoilState(moisture=11.2, organic_carbon=1.2),
        spatial_context=SpatialContext(region="Semi-Arid Zone", ecosystem="dryland"),
    )
    result = multi_metric_engine.analyze_environmental_state(state)

    # Check observed vs unknown distinction
    assert result.observed_conditions["climate.rainfall"] == 420.0
    assert result.observed_conditions["climate.temperature"] == 34.5
    assert result.observed_conditions["soil.moisture"] == 11.2
    assert result.unknown_metrics_count > 0  # Missing metrics tracked cleanly

    # Verify compound pressure detection
    drought_pressures = [p for p in result.pressures if p.pressure_type == "thermal_hydro_drought"]
    assert len(drought_pressures) == 1

    dp = drought_pressures[0]
    assert dp.severity == NaturePressureSeverity.CRITICAL
    assert len(dp.contributing_metrics) == 3
    assert "climate.rainfall" in dp.contributing_metrics
    assert "soil.moisture" in dp.contributing_metrics
    assert "climate.temperature" in dp.contributing_metrics

    # Verify causal reasoning chain
    assert dp.reasoning_chain is not None
    assert len(dp.reasoning_chain.links) >= 2
    assert "cavitation" in dp.reasoning_chain.narrative_summary.lower() or "drought" in dp.reasoning_chain.narrative_summary.lower()

    # Verify attached scientific RAG evidence packet
    assert len(dp.evidence_packet) >= 1
    evidence_orgs = {e.organization for e in dp.evidence_packet}
    assert "IPCC" in evidence_orgs or "Geoderma" in evidence_orgs or "Science" in evidence_orgs


def test_agro_homogenization_multi_metric_stress(multi_metric_engine: MultiMetricReasoningEngine):
    """Verify 3-variable reasoning: monoculture + low habitat diversity + low species richness."""
    state = EnvironmentalState(
        land=LandState(land_use="monoculture"),
        biodiversity=BiodiversityState(habitat_diversity=22.0, species_richness=18),
    )
    result = multi_metric_engine.analyze_environmental_state(state)

    homog_pressures = [p for p in result.pressures if p.pressure_type == "habitat_simplification"]
    assert len(homog_pressures) == 1

    hp = homog_pressures[0]
    assert hp.severity == NaturePressureSeverity.CRITICAL
    assert set(hp.contributing_metrics) == {"land.land_use", "biodiversity.habitat_diversity", "biodiversity.species_richness"}
    assert len(hp.evidence_packet) >= 1
    assert any("Benton" in e.citation or "Tilman" in e.citation or "IPBES" in e.citation for e in hp.evidence_packet)


def test_anthropogenic_fragmentation_and_ecotoxicity(multi_metric_engine: MultiMetricReasoningEngine):
    """Verify compound stress: deforestation (>8%) + pollution index (>20)."""
    state = EnvironmentalState(
        human_impact=HumanImpactState(deforestation=14.0, pollution=35.0),
        land=LandState(land_cover="fragmented_canopy"),
    )
    result = multi_metric_engine.analyze_environmental_state(state)

    anthro_pressures = [p for p in result.pressures if p.pressure_type == "anthropogenic_compound_stress"]
    assert len(anthro_pressures) == 1
    ap = anthro_pressures[0]
    assert ap.severity == NaturePressureSeverity.CRITICAL
    assert "human_impact.deforestation" in ap.contributing_metrics
    assert "human_impact.pollution" in ap.contributing_metrics
    assert len(ap.evidence_packet) >= 1


def test_zero_vs_unknown_distinction_in_reasoning(multi_metric_engine: MultiMetricReasoningEngine):
    """Verify 0.0 pollution is OBSERVED pristine zero, not unknown and not triggering false toxicity."""
    state = EnvironmentalState(
        human_impact=HumanImpactState(deforestation=0.0, pollution=0.0),
        soil=SoilState(organic_carbon=3.5, moisture=45.0, ph=6.8),
    )
    result = multi_metric_engine.analyze_environmental_state(state)

    # Pollution 0.0 is observed
    assert result.observed_conditions["human_impact.pollution"] == 0.0
    assert result.observed_conditions["human_impact.deforestation"] == 0.0

    # No toxic synergy or critical pressures inferred
    critical_pressures = [p for p in result.pressures if p.severity == NaturePressureSeverity.CRITICAL]
    assert len(critical_pressures) == 0


# ==============================================================================
# 4. API ENDPOINTS INTEGRATION TESTS
# ==============================================================================

def test_api_corpus_documents_list(client: TestClient):
    """Test GET /api/v1/corpus/documents."""
    res = client.get("/api/v1/corpus/documents")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 10


def test_api_corpus_document_detail_and_chunks(client: TestClient):
    """Test GET /api/v1/corpus/documents/{id} and /chunks."""
    res = client.get("/api/v1/corpus/documents/DOC_IPCC_WG2_2022_CH2")
    assert res.status_code == 200
    doc = res.json()
    assert doc["id"] == "DOC_IPCC_WG2_2022_CH2"
    assert doc["organization"] == "IPCC"

    chunks_res = client.get("/api/v1/corpus/documents/DOC_IPCC_WG2_2022_CH2/chunks")
    assert chunks_res.status_code == 200
    chunks = chunks_res.json()
    assert len(chunks) >= 2


def test_api_corpus_semantic_search(client: TestClient):
    """Test POST /api/v1/corpus/search."""
    payload = {
        "query": "soil acidification aluminum toxicity and root damage",
        "metrics": ["soil.ph"],
        "top_k": 5,
    }
    res = client.post("/api/v1/corpus/search", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert not data["insufficient_evidence"]
    assert len(data["evidence_chunks"]) >= 1
    assert data["evidence_chunks"][0]["citation"] is not None


def test_api_multi_metric_analysis_endpoint(client: TestClient):
    """Test POST /api/v1/reasoning/multi-metric-analysis."""
    payload = {
        "soil": {"ph": 4.8, "organic_carbon": 0.9, "moisture": 14.0},
        "climate": {"temperature": 32.0, "rainfall": 480.0},
        "land": {"land_use": "monoculture"},
        "biodiversity": {"habitat_diversity": 20.0, "species_richness": 15},
    }
    res = client.post("/api/v1/reasoning/multi-metric-analysis", json=payload)
    assert res.status_code == 200
    data = res.json()

    assert data["observed_metrics_count"] >= 6
    assert len(data["pressures"]) >= 2
    assert data["total_evidence_chunks_attached"] >= 2
    assert len(data["system_limitations"]) >= 1

    # Verify each pressure has full structured evidence
    for pressure in data["pressures"]:
        assert pressure["pressure_id"]
        assert pressure["name"]
        assert pressure["severity"] in ["critical", "high", "medium", "low"]
        assert len(pressure["contributing_metrics"]) >= 1
        assert len(pressure["evidence_packet"]) >= 1
        assert pressure["evidence_packet"][0]["citation"]
