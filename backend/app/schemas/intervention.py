"""Pydantic schemas for Ecological Interventions and Recommendation Engine (Phase 10).

Defines structured models for candidate interventions, biophysical suitability rules,
directional metric effects, grounded evidence citations, and ranked recommendation sets.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

from backend.app.schemas.environmental_state import EnvironmentalState, SpatialContext
from backend.app.schemas.ecological_findings import (
    EcologicalFinding,
    ConflictReport,
    ObservationSource,
)
from backend.app.schemas.scientific_rag import EvidenceChunkPacket, EvidenceStrength


class DirectionOfChange(str, Enum):
    """Directional trend for impacted environmental metrics."""

    INCREASE = "increase"
    DECREASE = "decrease"
    IMPROVE = "improve"
    REDUCE = "reduce"
    MAINTAIN = "maintain"
    STABILIZE = "stabilize"
    RESTORE = "restore"


class TimeHorizon(str, Enum):
    """Temporal horizon required for ecological impacts to manifest."""

    SHORT_TERM = "short_term (<2 yrs)"
    MEDIUM_TERM = "medium_term (2-5 yrs)"
    LONG_TERM = "long_term (>5 yrs)"
    MULTI_DECADAL = "multi_decadal (>10 yrs)"


class InterventionCategory(str, Enum):
    """Broad categorization of ecological remediation actions."""

    NATIVE_RESTORATION = "native_restoration"
    HABITAT_CONNECTIVITY = "habitat_connectivity"
    AGROECOLOGY = "agroecology"
    WATER_AND_RIPARIAN = "water_and_riparian"
    WETLAND_HYDROLOGICAL = "wetland_hydrological"
    LANDSCAPE_HETEROGENEITY = "landscape_heterogeneity"
    SOIL_CONSERVATION = "soil_conservation"
    EROSION_CONTROL = "erosion_control"
    SPECIES_MANAGEMENT = "species_management"


class ExpectedMetricEffect(BaseModel):
    """Directional and evidence-backed effect of an intervention on an environmental metric."""

    model_config = ConfigDict(extra="forbid")

    metric_id: str = Field(description="Target metric identifier (e.g. 'soil.organic_carbon')")
    metric_name: str = Field(description="Human-readable metric name")
    expected_direction: DirectionOfChange = Field(description="Direction of change: increase, decrease, improve, reduce, maintain")
    quantitative_estimate: Optional[str] = Field(
        default=None,
        description="Quantitative estimate range ONLY if substantiated by retrieved evidence (e.g. '+15-25 mm/m water holding capacity')",
    )
    is_quantified: bool = Field(
        default=False,
        description="True only if supported by explicit evidence citation with numbers; False indicates directional-only",
    )
    time_to_detectable_impact_years: Optional[float] = Field(
        default=None,
        ge=0.0,
        description="Estimated lag time in years before significant change is measurable",
    )
    confidence: float = Field(default=0.85, ge=0.0, le=1.0, description="Confidence in this metric effect")


class FeasibilityConstraint(BaseModel):
    """Implementation, biophysical, or socio-economic constraint."""

    model_config = ConfigDict(extra="forbid")

    constraint_type: str = Field(description="biophysical | hydrological | agronomic | land_tenure | labor | climatic")
    description: str = Field(description="Specific detail of the constraint")
    severity: str = Field(default="medium", description="critical | high | medium | low")


class BiophysicalSuitabilityRules(BaseModel):
    """Biophysical envelope and exclusion boundaries for an intervention."""

    model_config = ConfigDict(extra="forbid")

    min_rainfall_mm: Optional[float] = Field(default=None, description="Minimum annual rainfall required")
    max_rainfall_mm: Optional[float] = Field(default=None, description="Maximum annual rainfall tolerated")
    min_soil_ph: Optional[float] = Field(default=None, description="Minimum soil pH supported")
    max_soil_ph: Optional[float] = Field(default=None, description="Maximum soil pH supported")
    min_soil_moisture_pct: Optional[float] = Field(default=None, description="Minimum soil moisture required")
    max_temperature_c: Optional[float] = Field(default=None, description="Maximum ambient temperature tolerated")
    applicable_land_uses: List[str] = Field(default_factory=list, description="Permissible land uses (e.g. 'cropland', 'pasture', 'degraded')")
    excluded_land_uses: List[str] = Field(default_factory=list, description="Explicitly forbidden land uses (e.g. 'intact_primary_forest', 'urban_paved')")
    applicable_ecosystems: List[str] = Field(default_factory=list, description="Compatible ecosystems")
    excluded_ecosystems: List[str] = Field(default_factory=list, description="Incompatible ecosystems")
    required_context_conditions: List[str] = Field(default_factory=list, description="Contextual prerequisites (e.g. 'surface_waterway_present')")


class InterventionDefinition(BaseModel):
    """Curated canonical definition of an ecological intervention in the Knowledge Base."""

    model_config = ConfigDict(extra="forbid")

    id: str = Field(description="Unique identifier (e.g. 'INT_AGROFORESTRY_ALLEY_CROPPING')")
    name: str = Field(description="Standard scientific title of the intervention")
    category: InterventionCategory = Field(description="Intervention category classification")
    target_pressures: List[str] = Field(
        default_factory=list,
        description="List of ecological pressures/findings this directly mitigates (e.g. 'monoculture_simplification', 'soil_water_stress')",
    )
    suitability_rules: BiophysicalSuitabilityRules = Field(description="Biophysical envelope and exclusions")
    what_to_do_template: str = Field(description="Operational guidance on specific actions to take")
    why_it_works_template: str = Field(description="Ecological justification of why the action resolves the pressure")
    ecological_mechanism: str = Field(description="In-depth biophysical/trophic causal mechanism")
    time_horizon: TimeHorizon = Field(description="Expected time horizon for impact")
    target_metrics: List[str] = Field(default_factory=list, description="Key environmental metrics altered by this intervention")
    expected_metric_effects: List[ExpectedMetricEffect] = Field(default_factory=list, description="Directional and quantitative metric impacts")
    evidence_ids: List[str] = Field(default_factory=list, description="IDs of authoritative peer-reviewed citations")
    constraints: List[FeasibilityConstraint] = Field(default_factory=list, description="Biophysical and operational constraints")
    tradeoffs: List[str] = Field(default_factory=list, description="Ecological, resource, and economic trade-offs")
    limitations: List[str] = Field(default_factory=list, description="Conditions under which intervention fails or underperforms")


class RecommendationConfidenceBasis(BaseModel):
    """Transparent scientific justification for confidence scoring."""

    model_config = ConfigDict(extra="forbid")

    overall_confidence: float = Field(ge=0.0, le=1.0, description="Calibrated confidence score [0.0 - 1.0]")
    evidence_grade: str = Field(description="Consensus | Strong | Moderate | Preliminary | Insufficient")
    pressure_relevance_score: float = Field(ge=0.0, le=1.0, description="How directly intervention addresses observed pressures")
    biophysical_suitability_score: float = Field(ge=0.0, le=1.0, description="Degree of match with site environmental envelope")
    data_completeness_factor: float = Field(ge=0.0, le=1.0, description="Ratio of verified observed metrics vs unknown metrics")
    conflict_uncertainty_penalty: float = Field(ge=0.0, le=1.0, description="Deduction applied for conflicting or mismatched metrics")
    justification_summary: str = Field(description="Human-readable explanation of confidence basis")


class ExplanationChainModel(BaseModel):
    """Structured explanation chain: Observed conditions -> Ecological pressure -> Ecological mechanism -> Intervention -> Expected metric effects -> Scientific evidence."""

    model_config = ConfigDict(extra="forbid")

    observed_facts: List[str] = Field(default_factory=list, description="Verified observed facts distinguishing raw data from inference")
    inferred_reasoning: List[str] = Field(default_factory=list, description="Inferred pressures and causal reasoning links")
    ecological_pressure: str = Field(description="Primary ecological pressure being addressed")
    ecological_mechanism: str = Field(description="Biophysical or trophic mechanism")
    intervention_action: str = Field(description="Actionable intervention directives")
    expected_metric_effects: List[ExpectedMetricEffect] = Field(default_factory=list, description="Expected metric changes")
    scientific_evidence_summary: List[str] = Field(default_factory=list, description="Summarized scientific evidence backing this chain")


class FeasibilityEvaluationModel(BaseModel):
    """Comprehensive feasibility assessment evaluating site biophysical and climatic compatibility."""

    model_config = ConfigDict(extra="forbid")

    status: str = Field(description="'Suitable' | 'Conditionally suitable' | 'Insufficient information' | 'Not currently suitable'")
    reason: str = Field(description="Concise justification for feasibility status")
    evaluations: Dict[str, str] = Field(
        default_factory=dict,
        description="Detailed evaluations covering climate suitability, rainfall, temperature, soil conditions, moisture, land use, land cover, water availability, space requirements, ecosystem compatibility, and known ecological constraints"
    )


class ValidatedClaimModel(BaseModel):
    """Programmatically validated scientific or quantitative claim."""

    model_config = ConfigDict(extra="forbid")

    claim_text: str = Field(description="The scientific or quantitative claim statement")
    claim_type: str = Field(description="'scientific' | 'quantitative' | 'causal'")
    is_supported: bool = Field(description="True if supported by retrieved scientific evidence")
    evidence_backed: bool = Field(description="True if backed by explicit literature evidence chunks")
    uncertainty_preserved: bool = Field(description="True if uncertainty and site-conditional bounds are maintained")
    validation_status: str = Field(description="'Validated' | 'Softened due to uncertainty' | 'Removed (unsupported)'")
    justification: str = Field(description="Validation rationale based on evidence corpus and state")


class ScientificValidationPacket(BaseModel):
    """Comprehensive scientific claim validation and risk assessment packet."""

    model_config = ConfigDict(extra="forbid")

    validated_claims: List[ValidatedClaimModel] = Field(default_factory=list, description="Validated claims list")
    evidence_support_summary: str = Field(description="Summary of literature support and consensus")
    uncertainty_statement: str = Field(description="Explicit statement of study limitations and site contingencies")
    conflict_resolution_notes: List[str] = Field(default_factory=list, description="Notes on how conflicting evidence or data discrepancies were handled")
    context_specific_tradeoffs: List[str] = Field(default_factory=list, description="Context-specific trade-offs based on state and resources")
    limitations: List[str] = Field(default_factory=list, description="Operational and ecological failure modes")


class InterventionRecommendation(BaseModel):
    """Complete, context-specific, evidence-backed recommendation with structured explainability and feasibility."""

    model_config = ConfigDict(extra="forbid")

    recommendation_id: str = Field(description="Unique recommendation ID, e.g. 'REC_AGROFORESTRY_001'")
    intervention_id: str = Field(description="Parent intervention ID")
    recommendation: str = Field(description="Action-oriented summary recommendation text")
    title: str = Field(description="Action-oriented recommendation title")
    category: InterventionCategory = Field(description="Intervention category")
    addressed_findings: List[str] = Field(default_factory=list, description="IDs of ecological findings directly targeted")
    addressed_pressures: List[str] = Field(default_factory=list, description="List of ecological pressures resolved")
    what_to_do: str = Field(description="Actionable operational directives tailored to context")
    why_it_works: str = Field(description="Functional ecological rationale")
    ecological_mechanism: str = Field(description="Detailed biophysical, chemical, or trophic mechanism")
    target_metrics: List[str] = Field(default_factory=list, description="Canonical metric IDs affected")
    impacted_metrics: List[ExpectedMetricEffect] = Field(default_factory=list, description="Relevant impacted metrics with direction")
    expected_metric_effects: List[ExpectedMetricEffect] = Field(default_factory=list, description="Directional and substantiated quantitative changes")
    explanation_chain: ExplanationChainModel = Field(description="Structured explanation chain from conditions to evidence")
    feasibility: FeasibilityEvaluationModel = Field(description="Detailed site feasibility assessment")
    validation: ScientificValidationPacket = Field(description="Scientific claim validation and risk assessment packet")
    time_horizon: str = Field(description="short_term (<2 yrs) | medium_term (2-5 yrs) | long_term (>5 yrs)")
    evidence_ids: List[str] = Field(default_factory=list, description="Citations supporting this intervention")
    evidence_references: List[EvidenceChunkPacket] = Field(default_factory=list, description="Retrieved scientific text snippets from corpus")
    evidence: List[EvidenceChunkPacket] = Field(default_factory=list, description="Alias for evidence references")
    confidence_basis: RecommendationConfidenceBasis = Field(description="Structured scientific confidence evaluation")
    confidence: RecommendationConfidenceBasis = Field(description="Alias for confidence basis")
    constraints: List[str] = Field(default_factory=list, description="Operational and biophysical prerequisites")
    tradeoffs: List[str] = Field(default_factory=list, description="Ecological, resource, and land-use trade-offs")
    limitations: List[str] = Field(default_factory=list, description="Known operational failure modes and boundaries")
    relevance_rank: int = Field(ge=1, description="Rank ordering by contextual relevance and evidence support")


class RecommendationSetResponse(BaseModel):
    """Ranked set of contextual intervention recommendations."""

    model_config = ConfigDict(extra="forbid")

    recommendations: List[InterventionRecommendation] = Field(default_factory=list, description="Ranked list of suitable recommendations")
    total_recommendations: int = Field(description="Count of recommended interventions")
    targeted_findings_count: int = Field(description="Count of ecological findings addressed")
    unaddressed_findings: List[str] = Field(default_factory=list, description="Findings with no suitable intervention in this context")
    excluded_interventions: Dict[str, str] = Field(
        default_factory=dict,
        description="Interventions evaluated but disqualified with explicit biophysical/contextual reason",
    )
    overall_confidence: float = Field(ge=0.0, le=1.0, description="Aggregate confidence score across all recommendations")
    evidence_coverage_ratio: float = Field(ge=0.0, le=1.0, description="Proportion of claims directly backed by retrieved literature")
    evaluation_timestamp: str = Field(description="ISO timestamp of evaluation")


class InterventionEngineRequest(BaseModel):
    """Request payload for the scientific intervention engine."""

    model_config = ConfigDict(extra="forbid")

    state: EnvironmentalState = Field(description="Canonical EnvironmentalState for biophysical filtering")
    findings: List[EcologicalFinding] = Field(default_factory=list, description="Identified ecological findings from reasoning pipeline")
    conflicts: List[ConflictReport] = Field(default_factory=list, description="Detected data discrepancies and uncertainty flags")
    spatial_context: Optional[SpatialContext] = Field(default=None, description="Spatial and biome context")
    max_recommendations: int = Field(default=5, ge=1, le=15, description="Maximum number of recommendations to return")
    min_confidence_threshold: float = Field(default=0.40, ge=0.0, le=1.0, description="Minimum confidence score required")
    allow_experimental: bool = Field(default=False, description="Include interventions with preliminary or moderate evidence")

