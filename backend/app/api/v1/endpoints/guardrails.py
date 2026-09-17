"""FastAPI router for VASUDHA AI Safety and Scientific Guardrails diagnostics and validation."""

from typing import Any, Dict
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.app.schemas.environmental_state import EnvironmentalState
from backend.app.guardrails.models import (
    GuardrailEvaluationSummary,
    PromptInjectionScanResult,
)
from backend.app.guardrails.service import get_guardrail_service

router = APIRouter()


class InputValidationRequest(BaseModel):
    """Raw input payload for guardrail screening."""
    data: Dict[str, Any] = Field(..., description="Key-value dictionary of environmental parameters")


class PromptScanRequest(BaseModel):
    """Text string to scan for prompt injections or instruction overrides."""
    prompt: str = Field(..., description="Untrusted user input or document chunk")


@router.get("/status", summary="Guardrail Engine Status & Active Policies")
def get_guardrail_status():
    """Retrieve active scientific guardrail policies and system health."""
    return {
        "status": "active",
        "framework": "VASUDHA AI Safety, Scientific Guardrails & Abuse Resistance",
        "phase": "16.5",
        "policies": {
            "input_boundary_enforcement": "active",
            "unknown_vs_zero_preservation": "active",
            "observation_conflict_detection": "active",
            "multi_metric_reasoning_guard": "active (min 3 variables)",
            "evidence_traceability": "active (IPCC/IPBES/FAO/CBD curated corpus)",
            "anti_citation_fabrication": "active",
            "quantitative_claim_softening": "active",
            "biophysical_water_safety": "active",
            "invasive_species_prevention": "active",
            "prompt_injection_defense": "active",
            "credential_leak_redaction": "active",
        },
    }


@router.post("/validate-input", response_model=GuardrailEvaluationSummary, summary="Validate Raw Input Dictionary")
def validate_raw_input(request: InputValidationRequest):
    """Screen arbitrary raw input dictionary against physical and scientific bounds."""
    service = get_guardrail_service()
    return service.validate_incoming_raw_input(request.data)


@router.post("/validate-state", response_model=GuardrailEvaluationSummary, summary="Validate Canonical Environmental State")
def validate_state(state: EnvironmentalState):
    """Run ecological plausibility, zero vs unknown, and multi-metric reasoning checks."""
    service = get_guardrail_service()
    return service.validate_environmental_state(state)


@router.post("/scan-prompt", response_model=PromptInjectionScanResult, summary="Scan Prompt for Injections")
def scan_prompt(request: PromptScanRequest):
    """Scan untrusted user prompt or document text for adversarial injection attempts."""
    service = get_guardrail_service()
    return service.llm_rules.scan_input_for_injections(request.prompt)
