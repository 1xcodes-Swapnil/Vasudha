"""Pydantic schemas for Scientific Corpus, RAG, and Multi-Metric Reasoning (Phases 4 & 5)."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.knowledge import (
    EvidenceStrength,
    MetricDomain,
    ReasoningChain,
    VariableObservationState,
    VariableStatus,
    MultiMetricCompoundPressure,
)


class GeographicApplicability(str, Enum):
    """Geographic and biome applicability grade of retrieved scientific evidence."""

    GLOBALLY_RELEVANT = "globally_relevant"
    REGIONALLY_RELEVANT = "regionally_relevant"
    ECOSYSTEM_SPECIFIC = "ecosystem_specific"
    GEOGRAPHICALLY_MISMATCHED = "geographically_mismatched"


class ScientificSourceType(str, Enum):
    """Classification of scientific evidence sources."""

    GLOBAL_ASSESSMENT = "global_assessment"
    SYSTEMATIC_REVIEW = "systematic_review"
    META_ANALYSIS = "meta_analysis"
    PEER_REVIEWED_JOURNAL = "peer_reviewed_journal"
    INSTITUTIONAL_REPORT = "institutional_report"


# ==============================================================================
# 1. SCIENTIFIC CORPUS SCHEMAS (PHASE 4)
# ==============================================================================

class ScientificChunkBase(BaseModel):
    """Base definition for a chunk within a scientific document."""

    chunk_index: int = Field(..., description="Zero-indexed position in document")
    content: str = Field(..., description="Clean text content of scientific passage")
    section: Optional[str] = Field(None, description="Section or chapter header")
    metrics: List[str] = Field(default_factory=list, description="Associated environmental metrics (e.g. soil.organic_carbon)")
    ecosystem: str = Field("all", description="Target ecosystem / biome")
    geographic_scope: str = Field("global", description="global, tropical, arid, temperate, etc.")
    evidence_strength: EvidenceStrength = Field(EvidenceStrength.STRONG, description="Evidence tier")
    confidence_grade: str = Field("high", description="high, moderate, preliminary")


class ScientificChunk(ScientificChunkBase):
    """Full chunk model with IDs and source traceability."""

    id: str = Field(..., description="Unique chunk ID e.g. DOC_IPBES_2019_C01")
    document_id: str = Field(..., description="Parent document identifier")
    citation: str = Field(..., description="Full parent citation for direct traceability")
    doi: Optional[str] = Field(None, description="Valid DOI if available")
    url: Optional[str] = Field(None, description="Publication link")


class ScientificDocumentCreate(BaseModel):
    """Payload for ingesting a scientific document into the corpus."""

    id: str = Field(..., description="Unique document ID, e.g. 'DOC_IPCC_WG2_2022_CH2'")
    title: str = Field(..., description="Full formal title of study or report")
    authors: str = Field(..., description="Author names or lead organization")
    organization: str = Field(..., description="IPCC, IPBES, FAO, UNEP, CBD, etc.")
    year: int = Field(..., description="Publication year")
    source_type: ScientificSourceType = Field(..., description="Source classification")
    citation: str = Field(..., description="Standard academic citation")
    url: Optional[str] = Field(None, description="Official publication URL")
    doi: Optional[str] = Field(None, description="Digital Object Identifier")
    geographic_scope: str = Field("global", description="Geographic scope of study")
    ecosystem: str = Field("all", description="Applicable ecosystem or biome")
    topics: List[str] = Field(default_factory=list, description="Key ecological topics")
    environmental_metrics: List[str] = Field(default_factory=list, description="Metrics analyzed in document")
    evidence_strength: EvidenceStrength = Field(EvidenceStrength.STRONG, description="Evidence hierarchy tier")
    abstract: Optional[str] = Field(None, description="Executive summary or abstract")
    full_text: str = Field(..., description="Full text or structured excerpts of document")


class ScientificDocument(BaseModel):
    """Full scientific document representation in the knowledge store."""

    id: str
    title: str
    authors: str
    organization: str
    year: int
    source_type: ScientificSourceType
    citation: str
    url: Optional[str] = None
    doi: Optional[str] = None
    geographic_scope: str
    ecosystem: str
    topics: List[str]
    environmental_metrics: List[str]
    evidence_strength: EvidenceStrength
    abstract: Optional[str] = None
    chunk_count: int
    created_at: Optional[str] = None


class ScientificSearchQuery(BaseModel):
    """Query parameters for semantic vector and metadata retrieval."""

    query: str = Field(..., description="Natural language scientific or ecological query")
    metrics: Optional[List[str]] = Field(None, description="Filter/boost by environmental metrics")
    ecosystem: Optional[str] = Field(None, description="Target ecosystem context")
    geographic_scope: Optional[str] = Field(None, description="Target geographic context")
    min_evidence_strength: Optional[EvidenceStrength] = Field(None, description="Minimum evidence strength filter")
    top_k: int = Field(6, ge=1, le=20, description="Target number of relevant chunks (target 5-8)")


class EvidenceChunkPacket(BaseModel):
    """Compact, structured scientific evidence chunk returned by RAG."""

    chunk_id: str
    document_id: str
    title: str
    authors: str
    organization: str
    year: int
    citation: str
    doi: Optional[str] = None
    url: Optional[str] = None
    content: str
    relevance_score: float = Field(..., description="Composite relevance score [0.0 - 1.0]")
    evidence_strength: EvidenceStrength
    confidence_grade: str
    geographic_scope: str
    ecosystem: str
    matched_metrics: List[str] = Field(default_factory=list)
    geographic_applicability: GeographicApplicability = Field(
        GeographicApplicability.GLOBALLY_RELEVANT,
        description="Applicability evaluation based on geographic alignment"
    )


class EvidencePacketResponse(BaseModel):
    """Structured evidence packet response returned by the RAG retrieval system."""

    query: str
    total_found: int
    selected_count: int
    evidence_chunks: List[EvidenceChunkPacket]
    insufficient_evidence: bool = Field(False, description="True if no reliable evidence satisfied quality thresholds")
    geographic_context_summary: Optional[str] = None
    contradiction_notes: Optional[str] = None


# ==============================================================================
# 2. MULTI-METRIC REASONING & NATURE PRESSURE SCHEMAS (PHASE 5)
# ==============================================================================

class NaturePressureSeverity(str, Enum):
    """Severity classification of an ecological pressure."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class NaturePressure(BaseModel):
    """Structured ecological pressure with multi-metric reasoning and attached evidence."""

    pressure_id: str
    pressure_type: str = Field(..., description="e.g. 'thermal_hydro_drought', 'habitat_simplification', 'soil_degradation'")
    name: str
    severity: NaturePressureSeverity
    contributing_metrics: List[str] = Field(..., description="3+ metrics when sufficient data exists")
    observed_conditions: Dict[str, Any] = Field(..., description="Exact observed values triggering pressure")
    inferred_mechanisms: List[str] = Field(..., description="Biophysical mechanisms explaining the pressure cascade")
    reasoning_chain: Optional[ReasoningChain] = None
    evidence_packet: List[EvidenceChunkPacket] = Field(default_factory=list, description="5-8 retrieved evidence chunks")
    evidence_strength: EvidenceStrength = Field(EvidenceStrength.STRONG)
    confidence: float = Field(0.9, ge=0.0, le=1.0)
    geographic_applicability: GeographicApplicability = Field(GeographicApplicability.GLOBALLY_RELEVANT)
    contradictory_evidence_notes: Optional[str] = None
    uncertainty_and_limitations: List[str] = Field(default_factory=list)


class MultiMetricAnalysisResponse(BaseModel):
    """Comprehensive output of Multi-Metric Ecological Reasoning + Scientific RAG."""

    observed_conditions: Dict[str, Any]
    variables_status: List[VariableStatus]
    pressures: List[NaturePressure]
    multi_metric_synergies: List[MultiMetricCompoundPressure]
    reasoning_chains: List[ReasoningChain]
    total_evidence_chunks_attached: int
    observed_metrics_count: int
    unknown_metrics_count: int
    system_limitations: List[str]
    evaluation_timestamp: str
