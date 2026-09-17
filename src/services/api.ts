/**
 * API client service for the Biodiversity Intelligence Backend
 */

import { SystemHealth } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api/v1';

export async function fetchHealthStatus(): Promise<SystemHealth> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 5000);

  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      signal: controller.signal,
      headers: {
        'Accept': 'application/json',
      },
    });

    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`Health check returned status ${response.status}: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    clearTimeout(timeoutId);
    // Return structured offline/fallback state if backend is starting or unreachable
    return {
      status: 'degraded',
      service: 'VASUDHA Biodiversity Intelligence API (Pending Local Connect)',
      version: '0.1.0',
      environment: 'development',
      timestamp: new Date().toISOString(),
      database: {
        status: 'disconnected',
        pgvector_enabled: false,
        error: error instanceof Error ? error.message : 'Backend unreachable',
      },
      ai_providers: {
        llm: 'gemini',
        embeddings: 'local (all-MiniLM-L6-v2)',
      },
    };
  }
}

// ==============================================================================
// ENVIRONMENTAL STATE API CLIENT (PHASE 1)
// ==============================================================================

import {
  EnvironmentalProfileResponse,
  EnvironmentalStateCreatePayload,
  EnvironmentalStateUpdatePayload,
  EnvironmentalState,
} from '../types';

export async function createEnvironmentalProfile(
  payload: EnvironmentalStateCreatePayload
): Promise<EnvironmentalProfileResponse> {
  const response = await fetch(`${API_BASE_URL}/environmental-state`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to create profile (${response.status})`);
  }

  return await response.json();
}

export async function getEnvironmentalProfile(
  profileId: string
): Promise<EnvironmentalProfileResponse> {
  const response = await fetch(`${API_BASE_URL}/environmental-state/${profileId}`, {
    headers: {
      'Accept': 'application/json',
    },
  });

  if (!response.ok) {
    throw new Error(`Profile not found (${response.status})`);
  }

  return await response.json();
}

export async function updateEnvironmentalProfile(
  profileId: string,
  payload: EnvironmentalStateUpdatePayload
): Promise<EnvironmentalProfileResponse> {
  const response = await fetch(`${API_BASE_URL}/environmental-state/${profileId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to update profile (${response.status})`);
  }

  return await response.json();
}

export async function listEnvironmentalProfiles(): Promise<EnvironmentalProfileResponse[]> {
  const response = await fetch(`${API_BASE_URL}/environmental-state`, {
    headers: {
      'Accept': 'application/json',
    },
  });

  if (!response.ok) {
    return [];
  }

  return await response.json();
}

export async function validateEnvironmentalState(
  state: EnvironmentalState
): Promise<{ valid: boolean; metrics_count: number; is_empty: boolean }> {
  const response = await fetch(`${API_BASE_URL}/environmental-state/validate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(state),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Validation failed (${response.status})`);
  }

  return await response.json();
}

// ==============================================================================
// GEOGRAPHIC CONTEXT API CLIENT (PHASE 2)
// ==============================================================================

import {
  GeoLookupRequest,
  GeoContextResult,
  GeoStateSyncRequest,
  GeoStateSyncResponse,
  GeoProviderInfo,
} from '../types';

export async function lookupGeoContext(
  request: GeoLookupRequest
): Promise<GeoContextResult> {
  const response = await fetch(`${API_BASE_URL}/geo/lookup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Geospatial lookup failed (${response.status})`);
  }

  return await response.json();
}

export async function syncSpatialState(
  request: GeoStateSyncRequest
): Promise<GeoStateSyncResponse> {
  const response = await fetch(`${API_BASE_URL}/geo/sync-state`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Spatial sync failed (${response.status})`);
  }

  return await response.json();
}

export async function listGeoProviders(): Promise<GeoProviderInfo[]> {
  const response = await fetch(`${API_BASE_URL}/geo/providers`, {
    headers: {
      'Accept': 'application/json',
    },
  });

  if (!response.ok) {
    return [];
  }

  return await response.json();
}

// ==============================================================================
// ECOLOGICAL KNOWLEDGE BASE & REASONING API CLIENT (PHASE 3)
// ==============================================================================

import {
  EnvironmentalMetric,
  EvidenceSource,
  EcologicalRelationship,
  ReasoningEvaluationResult,
} from '../types';

export async function fetchMetrics(domain?: string): Promise<EnvironmentalMetric[]> {
  const url = domain
    ? `${API_BASE_URL}/knowledge/metrics?domain=${encodeURIComponent(domain)}`
    : `${API_BASE_URL}/knowledge/metrics`;

  const response = await fetch(url, {
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    return [];
  }
  return await response.json();
}

export async function fetchRelationships(
  sourceMetric?: string,
  targetMetric?: string
): Promise<EcologicalRelationship[]> {
  const params = new URLSearchParams();
  if (sourceMetric) params.append('source_metric', sourceMetric);
  if (targetMetric) params.append('target_metric', targetMetric);

  const query = params.toString() ? `?${params.toString()}` : '';
  const response = await fetch(`${API_BASE_URL}/knowledge/relationships${query}`, {
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    return [];
  }
  return await response.json();
}

export async function fetchEvidence(): Promise<EvidenceSource[]> {
  const response = await fetch(`${API_BASE_URL}/knowledge/evidence`, {
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    return [];
  }
  return await response.json();
}

export async function evaluateReasoning(
  state: EnvironmentalState
): Promise<ReasoningEvaluationResult> {
  const response = await fetch(`${API_BASE_URL}/reasoning/evaluate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(state),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Reasoning evaluation failed (${response.status})`);
  }

  return await response.json();
}

export async function explainRelationship(
  relationshipId: string
): Promise<EcologicalRelationship> {
  const response = await fetch(`${API_BASE_URL}/reasoning/explain/${relationshipId}`, {
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Relationship '${relationshipId}' not found (${response.status})`);
  }

  return await response.json();
}

// ==============================================================================
// SCIENTIFIC CORPUS & RAG API CLIENT (PHASE 4)
// ==============================================================================

import {
  ScientificDocument,
  ScientificChunk,
  ScientificSearchQuery,
  EvidencePacketResponse,
  MultiMetricAnalysisResponse,
} from '../types';

export async function fetchCorpusDocuments(
  organization?: string,
  sourceType?: string,
  metric?: string
): Promise<ScientificDocument[]> {
  const params = new URLSearchParams();
  if (organization) params.append('organization', organization);
  if (sourceType) params.append('source_type', sourceType);
  if (metric) params.append('metric', metric);

  const query = params.toString() ? `?${params.toString()}` : '';
  const response = await fetch(`${API_BASE_URL}/corpus/documents${query}`, {
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    return [];
  }
  return await response.json();
}

export async function fetchDocumentDetail(
  documentId: string
): Promise<ScientificDocument> {
  const response = await fetch(`${API_BASE_URL}/corpus/documents/${documentId}`, {
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Document '${documentId}' not found (${response.status})`);
  }
  return await response.json();
}

export async function fetchDocumentChunks(
  documentId: string
): Promise<ScientificChunk[]> {
  const response = await fetch(`${API_BASE_URL}/corpus/documents/${documentId}/chunks`, {
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    return [];
  }
  return await response.json();
}

export async function searchScientificEvidence(
  query: ScientificSearchQuery
): Promise<EvidencePacketResponse> {
  const response = await fetch(`${API_BASE_URL}/corpus/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(query),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Evidence search failed (${response.status})`);
  }
  return await response.json();
}

// ==============================================================================
// MULTI-METRIC ECOLOGICAL REASONING + RAG API CLIENT (PHASE 5)
// ==============================================================================

export async function analyzeMultiMetricReasoning(
  state: EnvironmentalState
): Promise<MultiMetricAnalysisResponse> {
  const response = await fetch(`${API_BASE_URL}/reasoning/multi-metric-analysis`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(state),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Multi-metric analysis failed (${response.status})`);
  }
  return await response.json();
}

// ==============================================================================
// NATURE RISK PROFILE API CLIENT (PHASE 6)
// ==============================================================================

import { NatureRiskProfile, RiskDimensionMetadata } from '../types';

export async function fetchNatureRiskProfile(
  state: EnvironmentalState
): Promise<NatureRiskProfile> {
  const response = await fetch(`${API_BASE_URL}/risk/profile`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(state),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Nature risk profile evaluation failed (${response.status})`);
  }
  return await response.json();
}

export async function fetchRiskDimensions(): Promise<RiskDimensionMetadata[]> {
  const response = await fetch(`${API_BASE_URL}/risk/dimensions`, {
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    return [];
  }
  return await response.json();
}

// ==============================================================================
// AUTHORITATIVE ENVIRONMENTAL DATASETS & INGESTION (PHASE 7)
// ==============================================================================

import {
  DatasetMetadata,
  PointQueryResult,
  StateEnrichmentRequest,
  StateEnrichmentResponse,
} from '../types';

export async function fetchDatasetRegistry(): Promise<DatasetMetadata[]> {
  const response = await fetch(`${API_BASE_URL}/datasets/registry`, {
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to fetch dataset registry (${response.status})`);
  }
  return await response.json();
}

export async function queryAuthoritativeDatasets(
  latitude: number,
  longitude: number,
  allowSynthetic: boolean = false
): Promise<PointQueryResult> {
  const url = `${API_BASE_URL}/datasets/query-point?latitude=${encodeURIComponent(latitude)}&longitude=${encodeURIComponent(longitude)}&allow_synthetic=${allowSynthetic}`;
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Point dataset query failed (${response.status})`);
  }
  return await response.json();
}

export async function enrichEnvironmentalState(
  payload: StateEnrichmentRequest
): Promise<StateEnrichmentResponse> {
  const response = await fetch(`${API_BASE_URL}/datasets/enrich-state`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `State enrichment failed (${response.status})`);
  }
  return await response.json();
}

export async function ingestDatasetObservation(
  observation: {
    dataset_id: string;
    latitude: number;
    longitude: number;
    raw_payload: Record<string, any>;
    is_synthetic?: boolean;
  },
  region?: string,
  ecosystem?: string
): Promise<any> {
  let url = `${API_BASE_URL}/datasets/ingest`;
  const params = new URLSearchParams();
  if (region) params.append('region', region);
  if (ecosystem) params.append('ecosystem', ecosystem);
  if (params.toString()) {
    url += `?${params.toString()}`;
  }

  const response = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(observation),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Observation ingestion failed (${response.status})`);
  }
  return await response.json();
}

// ==============================================================================
// ECOLOGICAL FINDINGS & PIPELINE CLIENT (PHASE 9)
// ==============================================================================

import {
  EcologicalFindingsRequest,
  EcologicalFindingsResponse,
} from '../types';

export async function fetchEcologicalFindings(
  payload: EcologicalFindingsRequest
): Promise<EcologicalFindingsResponse> {
  const response = await fetch(`${API_BASE_URL}/reasoning/ecological-findings`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Ecological reasoning pipeline failed (${response.status})`);
  }
  return await response.json();
}

export async function extractStateFromText(
  text: string
): Promise<{ state: EnvironmentalState; extracted_variables: Record<string, any>; variables_count: number }> {
  const response = await fetch(`${API_BASE_URL}/reasoning/extract-state`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify({ text }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `State text extraction failed (${response.status})`);
  }
  return await response.json();
}

// ==============================================================================
// INTERVENTION & CONVERSATION API CLIENT (PHASES 10-14)
// ==============================================================================

import {
  RecommendationSetResponse,
  ConversationChatResponse,
  EnvironmentalMemory,
} from '../types';

export async function generateInterventions(payload: {
  state: EnvironmentalState;
  findings?: any[];
  conflicts?: any[];
  max_recommendations?: number;
}): Promise<RecommendationSetResponse> {
  const response = await fetch(`${API_BASE_URL}/interventions/recommendations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify(payload),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Failed to generate recommendations (${response.status})`);
  }
  return await response.json();
}

export async function sendConversationMessage(
  sessionId: string,
  message: string,
  stateOverrides?: Record<string, any> | null
): Promise<ConversationChatResponse> {
  const response = await fetch(`${API_BASE_URL}/conversation/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify({
      session_id: sessionId,
      message,
      state_overrides: stateOverrides || null,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Conversation chat failed (${response.status})`);
  }
  return await response.json();
}

export async function getSessionMemory(sessionId: string): Promise<EnvironmentalMemory> {
  const response = await fetch(`${API_BASE_URL}/conversation/${sessionId}`, {
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Failed to fetch session memory (${response.status})`);
  }
  return await response.json();
}

export async function resetSessionMemory(sessionId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/conversation/${sessionId}`, {
    method: 'DELETE',
    headers: { 'Accept': 'application/json' },
  });

  if (!response.ok) {
    throw new Error(`Failed to reset session (${response.status})`);
  }
}






