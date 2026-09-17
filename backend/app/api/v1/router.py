"""Centralized v1 API router aggregating all resource sub-routers."""

from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    health,
    environmental_state,
    geo,
    knowledge,
    reasoning,
    corpus,
    risk,
    datasets,
    interventions,
    conversation,
    performance,
    guardrails,
)

api_router = APIRouter()

# Health and diagnostic routes
api_router.include_router(health.router, prefix="/health", tags=["Health"])

# System Performance & Resource Monitoring routes
api_router.include_router(
    performance.router,
    prefix="/performance",
    tags=["System Performance"],
)

# Canonical Environmental State routes
api_router.include_router(
    environmental_state.router,
    prefix="/environmental-state",
    tags=["Environmental State"],
)

# Geographic Context & Spatial Resolution routes (Phase 2)
api_router.include_router(
    geo.router,
    prefix="/geo",
    tags=["Geographic Context"],
)

# Ecological Knowledge Base routes (Phase 3)
api_router.include_router(
    knowledge.router,
    prefix="/knowledge",
    tags=["Ecological Knowledge Base"],
)

# Deterministic Ecological Reasoning Engine routes (Phase 3 & 5)
api_router.include_router(
    reasoning.router,
    prefix="/reasoning",
    tags=["Ecological Reasoning Engine"],
)

# Scientific Corpus & RAG Retrieval routes (Phase 4)
api_router.include_router(
    corpus.router,
    prefix="/corpus",
    tags=["Scientific Corpus & RAG"],
)

# Nature Risk Profile Diagnostic routes (Phase 6)
api_router.include_router(
    risk.router,
    prefix="/risk",
    tags=["Nature Risk Profile"],
)

# Authoritative Environmental Datasets & Ingestion Pipeline routes (Phase 7)
api_router.include_router(
    datasets.router,
    prefix="/datasets",
    tags=["Environmental Datasets"],
)

# Scientific Ecological Intervention Engine routes (Phase 10)
api_router.include_router(
    interventions.router,
    prefix="/interventions",
    tags=["Ecological Interventions"],
)

# Multi-Turn Conversational Environmental Intelligence routes (Phase 13)
api_router.include_router(
    conversation.router,
    prefix="/conversation",
    tags=["Conversational Intelligence"],
)

# AI Safety, Scientific Guardrails & Abuse Resistance routes (Phase 16.5)
api_router.include_router(
    guardrails.router,
    prefix="/guardrails",
    tags=["AI Safety & Guardrails"],
)


