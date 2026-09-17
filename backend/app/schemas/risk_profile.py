"""Pydantic schemas for the Nature Risk Profile (Phase 6).

Intermediate diagnosis layer between environmental observation and intervention selection.
Deterministic, multi-metric, explainable, and scientific evidence-backed.
No arbitrary numerical scores.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from backend.app.schemas.knowledge import EvidenceStrength, ReasoningChain
from backend.app.schemas.scientific_rag import (
    EvidenceChunkPacket,
    GeographicApplicability,
)


class RiskLevel(str, Enum):
    """Discrete risk severity levels. Numerical scoring is strictly prohibited."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    UNKNOWN = "unknown"


class ExplainabilityChainStep(BaseModel):
    """Machine-readable step in the causal explainability chain.
    
    Structure: Observed Conditions -> Ecological Drivers -> Mechanism -> Nature Pressure -> Evidence
    """

    stage: str = Field(..., description="observed_conditions, ecological_drivers, mechanism, nature_pressure, evidence")
    description: str = Field(..., description="Human- and machine-readable explanation of this stage")
    details: Dict[str, Any] = Field(default_factory=dict, description="Structured attributes for this stage")


class ExplainabilityChain(BaseModel):
    """Complete 5-stage causal explainability chain for a risk dimension."""

    dimension: str
    observed_conditions: Dict[str, Any]
    ecological_drivers: List[str]
    biophysical_mechanism: str
    nature_pressure: str
    evidence_citations: List[str]
    steps: List[ExplainabilityChainStep] = Field(default_factory=list)


class RiskDimension(BaseModel):
    """Evaluation of a specific ecological risk dimension."""

    dimension_id: str = Field(..., description="e.g., 'water_stress', 'habitat_pressure'")
    name: str = Field(..., description="Human-readable title, e.g. 'Hydrologic & Water Stress'")
    level: RiskLevel = Field(..., description="Discrete level: low, medium, high, unknown")
    contributing_metrics: List[str] = Field(
        default_factory=list,
        description="Observed or missing metrics evaluated for this dimension"
    )
    observed_conditions: Dict[str, Any] = Field(
        default_factory=dict,
        description="Concrete observed metric values relevant to this dimension"
    )
    inferred_drivers: List[str] = Field(
        default_factory=list,
        description="Key biophysical stressors driving this risk level"
    )
    ecological_reasoning_chain: Optional[ReasoningChain] = Field(
        None,
        description="Full causal forward-chaining reasoning path if inferred"
    )
    explainability_chain: Optional[ExplainabilityChain] = Field(
        None,
        description="Formal 5-stage explainability chain (Observed -> Drivers -> Mechanism -> Pressure -> Evidence)"
    )
    evidence_ids: List[str] = Field(
        default_factory=list,
        description="Unique IDs of cited scientific documents and evidence"
    )
    evidence_chunks: List[EvidenceChunkPacket] = Field(
        default_factory=list,
        description="Verified scientific passages retrieved via RAG"
    )
    evidence_strength: EvidenceStrength = Field(
        EvidenceStrength.STRONG,
        description="Evidence tier backing this assessment"
    )
    geographic_applicability: GeographicApplicability = Field(
        GeographicApplicability.GLOBALLY_RELEVANT,
        description="Geographic/biome alignment of backing evidence"
    )
    uncertainty: str = Field(
        ...,
        description="Statement of uncertainty, boundary conditions, or data gap sensitivity"
    )
    limitations: List[str] = Field(
        default_factory=list,
        description="Specific constraints, missing variables, or ecological assumptions"
    )


class NatureRiskProfile(BaseModel):
    """Complete diagnostic Nature Risk Profile for an environmental state."""

    water_stress: RiskDimension
    habitat_pressure: RiskDimension
    biodiversity_pressure: RiskDimension
    climate_exposure: RiskDimension
    human_disturbance: RiskDimension
    overall_limitations: List[str] = Field(
        default_factory=list,
        description="System-wide limitations and missing data warnings"
    )
    missing_important_variables: List[str] = Field(
        default_factory=list,
        description="Important ecological variables that were not observed"
    )
    evidence_summary: List[EvidenceChunkPacket] = Field(
        default_factory=list,
        description="Deduplicated list of all attached scientific evidence packets across dimensions"
    )
    evaluation_timestamp: str = Field(..., description="ISO 8601 evaluation timestamp")
