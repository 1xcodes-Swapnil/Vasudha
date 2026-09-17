"""Schemas for Phase 13 Multi-Turn Conversational Environmental Intelligence Assistant."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ParameterProvenance(BaseModel):
    """Provenance tracking for environmental memory parameters."""
    source: str = Field(description="'user_explicit' | 'derived' | 'dataset' | 'default'")
    timestamp: str = Field(description="ISO timestamp when parameter was set or updated")
    confidence: float = Field(default=1.0, description="Confidence score [0.0 - 1.0]")


class EnvironmentalMemory(BaseModel):
    """Compact structured environmental memory profile per session."""
    land_use: Optional[str] = Field(default=None, description="Current land use type (e.g. 'cropland', 'degraded_forest')")
    land_cover: Optional[str] = Field(default=None, description="Land cover description")
    rainfall: Optional[float] = Field(default=None, description="Annual rainfall in mm (distinguish zero from unknown)")
    temperature: Optional[float] = Field(default=None, description="Mean annual temperature in °C")
    soil_organic_carbon: Optional[float] = Field(default=None, description="Soil organic carbon percentage (%)")
    soil_ph: Optional[float] = Field(default=None, description="Soil pH level")
    soil_moisture: Optional[float] = Field(default=None, description="Soil moisture percentage (%)")
    habitat_diversity: Optional[str] = Field(default=None, description="Habitat diversity description or index ('low', 'moderate', 'high')")
    species_richness: Optional[float] = Field(default=None, description="Species richness index")
    deforestation: Optional[float] = Field(default=None, description="Deforestation rate or percentage")
    pollution: Optional[float] = Field(default=None, description="Pollution index or level")
    ecosystem: Optional[str] = Field(default=None, description="Ecosystem or biome type")
    
    # Provenance mapping per parameter
    provenance: Dict[str, ParameterProvenance] = Field(default_factory=dict, description="Metadata tracking source of each parameter")


class ConversationChatRequest(BaseModel):
    """Request payload for multi-turn conversational chat endpoint."""
    session_id: str = Field(description="Unique session identifier")
    message: str = Field(description="User natural language message or query")
    state_overrides: Optional[Dict[str, Any]] = Field(default=None, description="Optional explicit state overrides")


class ConversationChatResponse(BaseModel):
    """Response payload for multi-turn conversational chat endpoint."""
    session_id: str = Field(description="Session identifier")
    conversational_response: str = Field(description="AI conversational response explaining reasoning and recommendations")
    environmental_memory: EnvironmentalMemory = Field(description="Updated compact environmental memory profile")
    needs_clarification: bool = Field(default=False, description="True if critical missing context requires user clarification")
    clarification_questions: List[str] = Field(default_factory=list, description="Clarification questions if context is incomplete")
    detected_conflicts: List[str] = Field(default_factory=list, description="Any detected contradictory statements requiring user resolution")
    recommendations: List[Any] = Field(default_factory=list, description="Deterministic intervention recommendations if sufficient context exists")
    active_risk_profile: Optional[Dict[str, Any]] = Field(default=None, description="Current risk diagnostic summary if available")
