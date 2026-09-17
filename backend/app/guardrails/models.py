"""Domain models and types for the centralized VASUDHA guardrail framework."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, ConfigDict


class GuardrailSeverity(str, Enum):
    """Severity classification for guardrail evaluation results."""
    INFO = "INFO"
    WARNING = "WARNING"
    BLOCK = "BLOCK"


class GuardrailAction(str, Enum):
    """Action dictated by the guardrail evaluation."""
    ALLOW = "ALLOW"
    ALLOW_WITH_WARNING = "ALLOW_WITH_WARNING"
    REQUEST_CLARIFICATION = "REQUEST_CLARIFICATION"
    BLOCK = "BLOCK"


class GeographicRelevanceGrade(str, Enum):
    """Geographic and ecosystem transferability grading."""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW_MISMATCH = "LOW_MISMATCH"


class GuardrailResult(BaseModel):
    """Individual rule evaluation outcome within the guardrail layer."""
    model_config = ConfigDict(extra="forbid")

    passed: bool = Field(description="Whether the evaluated check passed without violation")
    severity: GuardrailSeverity = Field(description="Severity classification")
    code: str = Field(description="Unique machine-readable guardrail rule code")
    message: str = Field(description="Human-readable explanation of the validation result")
    details: Dict[str, Any] = Field(default_factory=dict, description="Structured evaluation metadata")
    action: GuardrailAction = Field(default=GuardrailAction.ALLOW, description="Recommended downstream action")


class GuardrailEvaluationSummary(BaseModel):
    """Aggregated evaluation response across multiple guardrail checks."""
    model_config = ConfigDict(extra="forbid")

    overall_passed: bool = Field(description="True if no BLOCK or critical failure occurred")
    action: GuardrailAction = Field(description="Overall action to take")
    results: List[GuardrailResult] = Field(default_factory=list, description="All rule evaluation records")
    sanitized_output: Optional[Any] = Field(default=None, description="Sanitized or softened output")
    clarification_prompt: Optional[str] = Field(default=None, description="Targeted clarification question if needed")
    warnings: List[str] = Field(default_factory=list, description="User-facing scientific warnings or caveats")


class QuantitativeClaimValidation(BaseModel):
    """Validation report for a specific numerical / statistical claim."""
    model_config = ConfigDict(extra="forbid")

    original_claim: str
    metric_id: str
    extracted_quantity: Optional[str] = None
    is_supported: bool
    evidence_id: Optional[str] = None
    softened_claim: str
    action_taken: str  # e.g., 'preserved', 'softened_to_qualitative', 'stripped'


class PromptInjectionScanResult(BaseModel):
    """Result of untrusted input and prompt-injection screening."""
    model_config = ConfigDict(extra="forbid")

    is_safe: bool
    threat_detected: bool
    detected_patterns: List[str] = Field(default_factory=list)
    sanitized_input: str
