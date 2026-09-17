"""Multi-Turn Conversational Environmental Intelligence Engine (Phase 13).

Manages session memory, parameter extraction, contradiction detection,
clarification generation, and multi-turn ecological reasoning.
"""

from datetime import datetime, timezone
import re
from typing import Any, Dict, List, Optional, Tuple

from backend.app.core.logging import logger
from backend.app.schemas.conversation import (
    EnvironmentalMemory,
    ParameterProvenance,
    ConversationChatResponse,
)
from backend.app.schemas.environmental_state import (
    EnvironmentalState,
    SoilMetrics,
    LandMetrics,
    ClimateMetrics,
    BiodiversityMetrics,
    HumanImpactMetrics,
    SpatialContext,
)
from backend.app.schemas.intervention import InterventionEngineRequest
from backend.app.knowledge.intervention_engine import get_intervention_engine
from backend.app.knowledge.risk_engine import get_risk_engine
from backend.app.intelligence.llm import get_llm_provider
from backend.app.guardrails.service import get_guardrail_service
from backend.app.guardrails.models import GuardrailAction, GuardrailSeverity


class ConversationSession:
    """In-memory session container storing environmental memory and history."""
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.memory = EnvironmentalMemory()
        self.history: List[Dict[str, str]] = []
        self.last_recommendations: List[Any] = []
        self.last_risk_profile: Optional[Dict[str, Any]] = None
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = self.created_at


class ConversationEngine:
    """Engine managing multi-turn conversational environmental intelligence."""

    def __init__(self):
        self._sessions: Dict[str, ConversationSession] = {}

    def get_session(self, session_id: str) -> ConversationSession:
        if session_id not in self._sessions:
            self._sessions[session_id] = ConversationSession(session_id)
        return self._sessions[session_id]

    def reset_session(self, session_id: str) -> ConversationSession:
        self._sessions[session_id] = ConversationSession(session_id)
        return self._sessions[session_id]

    def process_message(
        self,
        session_id: str,
        message: str,
        state_overrides: Optional[Dict[str, Any]] = None,
    ) -> ConversationChatResponse:
        session = self.get_session(session_id)
        session.updated_at = datetime.now(timezone.utc).isoformat()
        guardrails = get_guardrail_service()

        # Add user message to history
        session.history.append({"role": "user", "content": message})

        # 0. Prompt-Injection and Adversarial Security Defense
        injection_scan = guardrails.llm_rules.scan_input_for_injections(message)
        if injection_scan.threat_detected:
            adversarial_reply = (
                "I operate strictly as an evidence-backed biodiversity intelligence system governed by deterministic "
                "scientific verification and security guardrails. I cannot override scientific rules, fabricate citations, "
                "or disclose internal system configurations."
            )
            session.history.append({"role": "assistant", "content": adversarial_reply})
            return ConversationChatResponse(
                session_id=session_id,
                conversational_response=adversarial_reply,
                environmental_memory=session.memory,
                needs_clarification=False,
                clarification_questions=[],
                detected_conflicts=["Adversarial instruction or system override attempt detected and blocked."],
                recommendations=[],
                active_risk_profile=session.last_risk_profile,
            )

        # 1. Extract environmental parameters from message (and state overrides)
        extracted_params, detected_conflicts = self._extract_and_validate_parameters(
            message, session.memory, state_overrides
        )

        # Validate extracted parameters with Input Guardrails
        input_summary = guardrails.input_rules.validate_raw_input_dict(extracted_params)
        for res in input_summary:
            if res.severity == GuardrailSeverity.BLOCK:
                detected_conflicts.append(f"Input validation error: {res.message}")

        # 2. Update environmental memory with rule enforcement (override, zero vs unknown, provenance)
        self._update_memory(session.memory, extracted_params)

        # 3. Check for required clarification context
        clarification_questions, needs_clarification = self._evaluate_clarification_needs(
            session.memory, message
        )

        recommendations = []
        risk_profile = None

        # 4. If no severe conflicts and sufficient context, run deterministic engines
        if not detected_conflicts and not needs_clarification:
            env_state = self._memory_to_environmental_state(session.memory)
            try:
                intervention_response = get_intervention_engine().generate_recommendations(
                    InterventionEngineRequest(state=env_state, max_recommendations=3)
                )
                raw_recs = intervention_response.recommendations
                # Apply recommendation & quantitative claim softening guardrails
                guarded_recs, rec_summary = guardrails.guard_recommendation_pipeline(
                    recommendations=raw_recs,
                    state=env_state,
                    evidence_packets=[],
                )
                recommendations = guarded_recs
                session.last_recommendations = recommendations
            except Exception as e:
                logger.error(f"Error generating recommendations in conversation engine: {e}")

            try:
                risk_res = get_risk_engine().diagnose(env_state)
                risk_profile = risk_res.model_dump()
                session.last_risk_profile = risk_profile
            except Exception as e:
                logger.error(f"Error diagnosing risk profile in conversation engine: {e}")

        # 5. Formulate conversational response
        conversational_response = self._generate_conversational_response(
            message, session.memory, recommendations, clarification_questions, detected_conflicts
        )

        session.history.append({"role": "assistant", "content": conversational_response})

        return ConversationChatResponse(
            session_id=session_id,
            conversational_response=conversational_response,
            environmental_memory=session.memory,
            needs_clarification=needs_clarification,
            clarification_questions=clarification_questions,
            detected_conflicts=detected_conflicts,
            recommendations=recommendations,
            active_risk_profile=risk_profile,
        )

    def _extract_and_validate_parameters(
        self,
        message: str,
        current_memory: EnvironmentalMemory,
        state_overrides: Optional[Dict[str, Any]] = None,
    ) -> Tuple[Dict[str, Any], List[str]]:
        extracted: Dict[str, Any] = {}
        conflicts: List[str] = []

        if state_overrides:
            for k, v in state_overrides.items():
                if v is not None:
                    extracted[k] = v

        msg_lower = message.lower()

        # Regex heuristics for parameter extraction
        # Rainfall e.g. "rainfall is 520mm", "rain 450 mm", "precipitation 600"
        rain_match = re.search(r'(?:rainfall|rain|precipitation)\D{0,15}(\d+(?:\.\d+)?)', msg_lower)
        if rain_match:
            val = float(rain_match.group(1))
            extracted['rainfall'] = val

        # Soil pH e.g. "ph 5.5", "soil ph of 6.2"
        ph_match = re.search(r'(?:soil\s*)?ph\D{0,10}(\d+(?:\.\d+)?)', msg_lower)
        if ph_match:
            val = float(ph_match.group(1))
            extracted['soil_ph'] = val

        # Soil organic carbon e.g. "organic carbon 0.42%", "carbon 1.2"
        soc_match = re.search(r'(?:organic\s*carbon|soc|carbon)\D{0,10}(\d+(?:\.\d+)?)', msg_lower)
        if soc_match:
            val = float(soc_match.group(1))
            extracted['soil_organic_carbon'] = val

        # Soil moisture e.g. "moisture 15%"
        moist_match = re.search(r'(?:soil\s*)?moisture\D{0,10}(\d+(?:\.\d+)?)', msg_lower)
        if moist_match:
            val = float(moist_match.group(1))
            extracted['soil_moisture'] = val

        # Land use e.g. "land use is cropland", "agricultural land", "pasture", "degraded forest"
        if "cropland" in msg_lower or "agriculture" in msg_lower or "farm" in msg_lower:
            extracted['land_use'] = "cropland"
        elif "forest" in msg_lower:
            extracted['land_use'] = "degraded_forest" if "degraded" in msg_lower else "forest"
        elif "pasture" in msg_lower or "grazing" in msg_lower:
            extracted['land_use'] = "pasture"
        elif "urban" in msg_lower:
            extracted['land_use'] = "urban"

        # Habitat diversity e.g. "habitat diversity is low", "low habitat diversity"
        if "low habitat" in msg_lower or "biodiversity is declining" in msg_lower or "poor biodiversity" in msg_lower:
            extracted['habitat_diversity'] = "low"
        elif "high habitat" in msg_lower or "rich biodiversity" in msg_lower:
            extracted['habitat_diversity'] = "high"

        # Check for contradictions against current memory
        for k, v in extracted.items():
            current_val = getattr(current_memory, k, None)
            if current_val is not None and current_val != v:
                # Potential conflict if numerical delta is large or categorical mismatch
                if isinstance(current_val, (int, float)) and isinstance(v, (int, float)):
                    delta_pct = abs(current_val - v) / (abs(current_val) + 1e-6)
                    if delta_pct > 0.30:  # >30% discrepancy
                        conflicts.append(f"Contradictory value for {k}: stated {v} conflicts with previous session value {current_val}.")
                elif isinstance(current_val, str) and isinstance(v, str) and current_val != v:
                    conflicts.append(f"Contradictory value for {k}: stated '{v}' conflicts with previous session value '{current_val}'.")

        return extracted, conflicts

    def _update_memory(self, memory: EnvironmentalMemory, extracted: Dict[str, Any]):
        timestamp = datetime.now(timezone.utc).isoformat()
        for k, v in extracted.items():
            if v is not None:  # New missing/None values do not erase existing values
                setattr(memory, k, v)
                memory.provenance[k] = ParameterProvenance(
                    source="user_explicit",
                    timestamp=timestamp,
                    confidence=1.0,
                )

    def _evaluate_clarification_needs(
        self, memory: EnvironmentalMemory, message: str
    ) -> Tuple[List[str], bool]:
        questions: List[str] = []
        msg_lower = message.lower()

        # If user is asking a broad question without land_use or rainfall/climate context
        missing_critical = []
        if memory.land_use is None:
            missing_critical.append("land-use type (e.g. cropland, pasture, forest)")
        if memory.rainfall is None:
            missing_critical.append("annual rainfall or water availability (mm/year)")
        if memory.soil_organic_carbon is None and memory.soil_ph is None:
            missing_critical.append("soil health indicator (such as organic carbon % or pH)")

        # Only ask clarification if query is general/diagnostic and critical info is missing
        is_diagnostic_query = any(w in msg_lower for w in ["biodiversity", "degrading", "help", "recommend", "improve", "problem", "restoration"])
        if is_diagnostic_query and len(missing_critical) >= 2:
            for item in missing_critical:
                questions.append(f"Could you please specify your {item}?")

        return questions, len(questions) > 0

    def _memory_to_environmental_state(self, memory: EnvironmentalMemory) -> EnvironmentalState:
        return EnvironmentalState(
            soil=SoilMetrics(
                ph=memory.soil_ph,
                organic_carbon=memory.soil_organic_carbon,
                moisture=memory.soil_moisture,
            ),
            land=LandMetrics(
                land_use=memory.land_use,
                land_cover=memory.land_cover,
            ),
            climate=ClimateMetrics(
                temperature=memory.temperature,
                rainfall=memory.rainfall,
            ),
            biodiversity=BiodiversityMetrics(
                species_richness=memory.species_richness,
                habitat_diversity=70.0 if memory.habitat_diversity == "high" else (30.0 if memory.habitat_diversity == "low" else None),
            ),
            human_impact=HumanImpactMetrics(
                deforestation=memory.deforestation,
                pollution=memory.pollution,
            ),
            spatial_context=SpatialContext(ecosystem=memory.ecosystem) if memory.ecosystem else SpatialContext(),
        )

    def _generate_conversational_response(
        self,
        message: str,
        memory: EnvironmentalMemory,
        recommendations: List[Any],
        clarification_questions: List[str],
        detected_conflicts: List[str],
    ) -> str:
        if detected_conflicts:
            conflict_str = " ".join(detected_conflicts)
            return f"I noticed a potential contradiction in your statements: {conflict_str} Could you please clarify which value is correct so I can provide accurate scientific recommendations?"

        if clarification_questions:
            questions_str = " ".join(clarification_questions)
            return f"To tailor scientifically rigorous interventions for your site, I need a little more context. {questions_str}"

        if recommendations:
            top_rec = recommendations[0]
            memory_summary = f"Based on your profile (land use: {memory.land_use or 'unspecified'}, rainfall: {memory.rainfall or 'unspecified'}mm, soil carbon: {memory.soil_organic_carbon or 'unspecified'}%):"
            return f"{memory_summary} I recommend **{top_rec.title}**. {top_rec.what_to_do} This addresses your ecological pressures with strong scientific backing."

        return f"I have updated your environmental profile. How else can I assist with ecological reasoning, risk analysis, or intervention planning?"


# Singleton factory
_conversation_engine: Optional[ConversationEngine] = None


def get_conversation_engine() -> ConversationEngine:
    global _conversation_engine
    if _conversation_engine is None:
        _conversation_engine = ConversationEngine()
    return _conversation_engine
