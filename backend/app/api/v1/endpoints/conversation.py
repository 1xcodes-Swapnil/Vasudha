"""FastAPI router for Multi-Turn Conversational Environmental Intelligence (Phase 13)."""

from fastapi import APIRouter, HTTPException, status
from backend.app.schemas.conversation import (
    ConversationChatRequest,
    ConversationChatResponse,
    EnvironmentalMemory,
)
from backend.app.knowledge.conversation_engine import get_conversation_engine

router = APIRouter()


@router.post("/chat", response_model=ConversationChatResponse, summary="Process multi-turn conversational message and environmental state")
def chat_endpoint(payload: ConversationChatRequest):
    if not payload.message or not payload.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Message cannot be empty.",
        )
    engine = get_conversation_engine()
    try:
        response = engine.process_message(
            session_id=payload.session_id,
            message=payload.message,
            state_overrides=payload.state_overrides,
        )
        return response
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing conversational message: {str(e)}",
        )


@router.get("/{session_id}", response_model=EnvironmentalMemory, summary="Retrieve session environmental memory")
def get_session_memory(session_id: str):
    engine = get_conversation_engine()
    session = engine.get_session(session_id)
    return session.memory


@router.delete("/{session_id}", status_code=status.HTTP_200_OK, summary="Reset/restart session memory")
def reset_session(session_id: str):
    engine = get_conversation_engine()
    engine.reset_session(session_id)
    return {"status": "success", "message": f"Session {session_id} successfully reset."}
