"""Pydantic schemas for the Ecological Knowledge Base & Relationship Engine (Phase 3)."""

from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class MetricDomain(str, Enum):
    """Core environmental and ecological domains."""

    SOIL = "soil"
    LAND = "land"
    BIODIVERSITY = "biodiversity"
    CLIMATE = "climate"
    HUMAN_IMPACT = "human_impact"
    ECOLOGICAL_STATE = "ecological_state"


class ConditionOperator(str, Enum):
    """Supported operators for relationship condition matching."""

    LESS_THAN = "<"
    LESS_THAN_OR_EQUAL = "<="
    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    EQUALS = "=="
    NOT_EQUALS = "!="
    IN_LIST = "in"
    CATEGORY_IS = "category_is"
    RANGE = "range"


class RelationshipDirection(str, Enum):
    """Scientific nature of the relationship influence."""

    POSITIVE = "positive"
    NEGATIVE = "negative"
    NON_LINEAR = "non_linear"
    THRESHOLD = "threshold"


class EvidenceStrength(str, Enum):
    """Weight of scientific backing."""

    CONSENSUS = "consensus"
    STRONG = "strong"
    MODERATE = "moderate"
    PRELIMINARY = "preliminary"
    REQUIRES_EVIDENCE = "requires_evidence"


# ==============================================================================
# 1. ENVIRONMENTAL METRIC DEFINITION
# ==============================================================================

class EnvironmentalMetricDefinition(BaseModel):
    """Definition of an environmental variable or derived state."""

    id: str = Field(..., description="Canonical metric identifier, e.g. 'soil.ph' or 'derived.water_retention'")
    name: str = Field(..., description="Human-readable title")
    domain: MetricDomain = Field(..., description="Scientific environmental domain")
    unit: Optional[str] = Field(None, description="Physical unit of measurement, e.g. 'pH', '%', 'mm/yr', '°C'")
    metric_type: str = Field("numeric", description="numeric, categorical, index, or state_flag")
    description: str = Field(..., description="Biophysical definition and ecological significance")
    min_value: Optional[float] = Field(None, description="Lower physical or typical boundary")
    max_value: Optional[float] = Field(None, description="Upper physical or typical boundary")
    categories: Optional[List[str]] = Field(None, description="Permitted string categories if categorical")


# ==============================================================================
# 2. EVIDENCE METADATA
# ==============================================================================

class EvidenceMetadata(BaseModel):
    """Scientific evidence source metadata."""

    id: str = Field(..., description="Citation ID, e.g. 'FAO_SOIL_2020', 'IPCC_WG2_2022'")
    source_type: str = Field(..., description="institutional_report, systematic_review, meta_analysis, peer_reviewed")
    citation: str = Field(..., description="Full authentic scientific citation")
    doi: Optional[str] = Field(None, description="Valid DOI string or None for institutional reports")
    year: int = Field(..., description="Publication year")
    institution: str = Field(..., description="Publishing body or journal (e.g., FAO, IPCC, IPBES, UNEP, Science, Nature)")
    url: Optional[str] = Field(None, description="Official publication URL")
    requires_evidence: bool = Field(False, description="Flag indicating empirical evidence is pending/open")
    confidence_grade: str = Field("high", description="high, moderate, preliminary")


# ==============================================================================
# 3. ECOLOGICAL RELATIONSHIP
# ==============================================================================

class EcologicalRelationship(BaseModel):
    """Structured ecological relationship representing a scientific mechanism."""

    id: str = Field(..., description="Unique relationship identifier, e.g. 'REL_SOC_WATER_RETENTION'")
    name: str = Field(..., description="Concise descriptive title of relationship")
    source_metric: str = Field(..., description="Triggering metric, e.g. 'soil.organic_carbon' or 'land.land_use'")
    operator: ConditionOperator = Field(..., description="Condition operator to evaluate against observed value")
    threshold_value: Any = Field(..., description="Threshold numeric value, category, or range for trigger")
    target_metric: str = Field(..., description="Target affected metric or derived pressure, e.g. 'water_retention'")
    target_state: str = Field(..., description="Inferred state or impact value, e.g. 'degraded', 'restricted', 'elevated'")
    relationship_type: str = Field(..., description="inhibits, enhances, degrades, limits, drives, induces")
    direction: RelationshipDirection = Field(RelationshipDirection.NEGATIVE, description="Directionality of effect")
    ecological_mechanism: str = Field(..., description="Detailed scientific explanation of the biophysical mechanism")
    evidence_ids: List[str] = Field(default_factory=list, description="IDs of cited scientific evidence sources")
    evidence_strength: EvidenceStrength = Field(EvidenceStrength.STRONG, description="Consensus/evidence grade")
    confidence: float = Field(0.9, ge=0.0, le=1.0, description="Mathematical certainty score for this rule")
    ecosystem_context: str = Field("all", description="Applicable ecosystem or 'all'")
    quality_metadata: Dict[str, Any] = Field(default_factory=dict, description="Metadata tags, e.g. peer-review tier")


# ==============================================================================
# 4. REASONING ENGINE INPUTS AND OUTPUTS
# ==============================================================================

class VariableObservationState(str, Enum):
    """Status classification of an environmental variable in a given evaluation."""

    OBSERVED = "observed"
    INFERRED = "inferred"
    UNKNOWN = "unknown"


class VariableStatus(BaseModel):
    """Metadata tracking whether a variable was observed or unknown."""

    metric_id: str
    name: str
    domain: MetricDomain
    status: VariableObservationState
    observed_value: Any = None
    unit: Optional[str] = None


class InferredPressure(BaseModel):
    """Ecological pressure or driver inferred by the relationship engine."""

    pressure_id: str
    name: str
    target_metric: str
    inferred_state: str
    severity: str = Field("medium", description="critical, high, medium, low")
    triggering_metric: str
    triggering_value: Any
    condition_matched: str
    ecological_mechanism: str
    evidence_ids: List[str]
    confidence: float
    chain_depth: int = 1


class MultiMetricCompoundPressure(BaseModel):
    """Ecological pressure emerging from simultaneous conditions across multiple metrics."""

    compound_id: str
    name: str
    severity: str = Field("critical", description="critical, high, medium")
    participating_metrics: List[str]
    triggering_conditions: Dict[str, Any]
    synergistic_mechanism: str
    evidence_ids: List[str]
    confidence: float


class ReasoningChainLink(BaseModel):
    """Individual link in an ecological reasoning chain."""

    step: int
    from_concept: str
    to_concept: str
    relationship_id: str
    relationship_type: str
    ecological_mechanism: str
    evidence_ids: List[str]


class ReasoningChain(BaseModel):
    """Complete causal reasoning chain from observed condition to systemic pressure."""

    chain_id: str
    root_observed_metric: str
    root_observed_value: Any
    final_pressure: str
    links: List[ReasoningChainLink]
    narrative_summary: str


class ReasoningEvaluationResult(BaseModel):
    """Complete structured output from the Ecological Reasoning Engine."""

    observed_metrics: Dict[str, Any] = Field(default_factory=dict)
    variables_status: List[VariableStatus] = Field(default_factory=list)
    inferred_pressures: List[InferredPressure] = Field(default_factory=list)
    compound_pressures: List[MultiMetricCompoundPressure] = Field(default_factory=list)
    reasoning_chains: List[ReasoningChain] = Field(default_factory=list)
    unknown_metrics_count: int = 0
    observed_metrics_count: int = 0
    inferred_pressures_count: int = 0
    evaluation_timestamp: str
