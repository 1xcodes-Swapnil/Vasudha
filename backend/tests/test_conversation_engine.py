"""Unit tests for Phase 13 Multi-Turn Conversational Environmental Intelligence Engine."""

import pytest
from backend.app.knowledge.conversation_engine import ConversationEngine, get_conversation_engine
from backend.app.schemas.conversation import ConversationChatRequest


@pytest.fixture
def conv_engine():
    return ConversationEngine()


def test_conversation_initialization(conv_engine):
    """Test session creation and initial empty memory."""
    session_id = "test_sess_01"
    session = conv_engine.get_session(session_id)
    assert session.session_id == session_id
    assert session.memory.land_use is None
    assert session.memory.rainfall is None


def test_multi_turn_state_updates_and_carry_over(conv_engine):
    """Test multi-turn state updates and memory carry-over."""
    session_id = "test_sess_02"
    
    # Turn 1: Provide land use and rainfall
    res1 = conv_engine.process_message(session_id, "My land use is cropland and annual rainfall is 520mm.")
    assert res1.environmental_memory.land_use == "cropland"
    assert res1.environmental_memory.rainfall == 520.0
    
    # Turn 2: Provide soil organic carbon in follow-up
    res2 = conv_engine.process_message(session_id, "My soil organic carbon is 0.42%.")
    assert res2.environmental_memory.land_use == "cropland"  # Carry over
    assert res2.environmental_memory.rainfall == 520.0       # Carry over
    assert res2.environmental_memory.soil_organic_carbon == 0.42


def test_value_overrides(conv_engine):
    """Test latest explicit value overrides older value."""
    session_id = "test_sess_03"
    conv_engine.process_message(session_id, "Rainfall is 400mm on cropland.")
    res2 = conv_engine.process_message(session_id, "Actually, rainfall is 850mm now.")
    assert res2.environmental_memory.rainfall == 850.0


def test_missing_values_do_not_erase_existing(conv_engine):
    """Test new missing values do not erase existing memory."""
    session_id = "test_sess_04"
    conv_engine.process_message(session_id, "Rainfall is 600mm and soil pH is 6.5.")
    res2 = conv_engine.process_message(session_id, "Biodiversity is declining.")
    assert res2.environmental_memory.rainfall == 600.0
    assert res2.environmental_memory.soil_ph == 6.5


def test_clarification_trigger(conv_engine):
    """Test clarification trigger when missing critical info for diagnostic query."""
    session_id = "test_sess_05"
    res = conv_engine.process_message(session_id, "My biodiversity is declining and soil is degrading.")
    assert res.needs_clarification is True
    assert len(res.clarification_questions) >= 1


def test_contradictory_statements(conv_engine):
    """Test contradiction detection and conflict reporting."""
    session_id = "test_sess_06"
    conv_engine.process_message(session_id, "Rainfall is 1000mm.")
    res2 = conv_engine.process_message(session_id, "Rainfall is 200mm.")
    assert len(res2.detected_conflicts) >= 1
    assert "Contradictory" in res2.detected_conflicts[0]


def test_session_persistence_and_reset(conv_engine):
    """Test session memory retrieval and reset."""
    session_id = "test_sess_07"
    conv_engine.process_message(session_id, "Soil pH is 5.5.")
    memory = conv_engine.get_session(session_id).memory
    assert memory.soil_ph == 5.5

    conv_engine.reset_session(session_id)
    reset_memory = conv_engine.get_session(session_id).memory
    assert reset_memory.soil_ph is None
