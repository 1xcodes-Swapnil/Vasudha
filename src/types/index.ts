/**
 * Types and Interfaces for VASUDHA — Biodiversity Intelligence
 */

export interface SystemHealth {
  status: 'ok' | 'degraded' | 'error';
  service: string;
  version: string;
  environment: string;
  timestamp: string;
  database: {
    status: 'connected' | 'disconnected';
    dialect?: string;
    pgvector_enabled: boolean;
    error?: string;
  };
  ai_providers: {
    llm: string;
    embeddings: string;
    embedding_model?: string;
  };
}

export type PipelineStageKey =
  | 'input'
  | 'environmental_state'
  | 'geo_context'
  | 'multi_metric_reasoning'
  | 'scientific_rag'
  | 'nature_risk_profile'
  | 'intervention_engine'
  | 'feasibility_check'
  | 'evidence_mapping'
  | 'claim_validation'
  | 'explanation'
  | 'trade_offs'
  | 'response';

export interface PipelineStageInfo {
  key: PipelineStageKey;
  label: string;
  description: string;
  phase: string;
  status: 'ready' | 'pending' | 'in_progress';
}

// ==============================================================================
// CANONICAL ENVIRONMENTAL STATE INTERFACES (PHASE 1)
// ==============================================================================

export interface SoilState {
  ph?: number | null;
  organic_carbon?: number | null;
  moisture?: number | null;
}

export interface LandState {
  land_use?: string | null;
  land_cover?: string | null;
}

export interface BiodiversityState {
  species_richness?: number | null;
  habitat_diversity?: number | null;
}

export interface ClimateState {
  temperature?: number | null;
  rainfall?: number | null;
}

export interface HumanImpactState {
  pollution?: number | string | null;
  deforestation?: number | null;
}

export interface SpatialContext {
  latitude?: number | null;
  longitude?: number | null;
  region?: string | null;
  ecosystem?: string | null;
}

export interface EnvironmentalState {
  soil: SoilState;
  land: LandState;
  biodiversity: BiodiversityState;
  climate: ClimateState;
  human_impact: HumanImpactState;
  spatial_context: SpatialContext;
}

export interface EnvironmentalProfileResponse {
  id: string;
  name?: string | null;
  description?: string | null;
  state: EnvironmentalState;
  metrics_count: number;
  created_at: string;
  updated_at: string;
}

export interface EnvironmentalStateCreatePayload {
  name?: string | null;
  description?: string | null;
  state: EnvironmentalState;
}

export interface EnvironmentalStateUpdatePayload {
  name?: string | null;
  description?: string | null;
  soil?: Partial<SoilState> | null;
  land?: Partial<LandState> | null;
  biodiversity?: Partial<BiodiversityState> | null;
  climate?: Partial<ClimateState> | null;
  human_impact?: Partial<HumanImpactState> | null;
  spatial_context?: Partial<SpatialContext> | null;
}

// ==============================================================================
// GEOGRAPHIC CONTEXT & INTERACTIVE MAP INTERFACES (PHASE 2)
// ==============================================================================

export interface GeoLookupRequest {
  latitude: number;
  longitude: number;
}

export interface GeoContextResult {
  latitude: number;
  longitude: number;
  region?: string | null;
  ecosystem?: string | null;
  biome_code?: string | null;
  elevation_estimate_m?: number | null;
  confidence: number;
  provider_name: string;
  degraded: boolean;
}

export interface GeoStateSyncRequest {
  state: EnvironmentalState;
  latitude?: number | null;
  longitude?: number | null;
  region?: string | null;
  ecosystem?: string | null;
  auto_enrich?: boolean;
  clear_location?: boolean;
}

export interface GeoStateSyncResponse {
  state: EnvironmentalState;
  spatial_context: SpatialContext;
  metrics_count: number;
  enrichment_status: string;
  provider: string;
}

export interface GeoProviderInfo {
  name: string;
  description: string;
  is_active: boolean;
  requires_api_key: boolean;
  status: string;
  capabilities: Record<string, any>;
}

// ==============================================================================
// ECOLOGICAL KNOWLEDGE BASE & REASONING INTERFACES (PHASE 3)
// ==============================================================================

export interface EnvironmentalMetric {
  id: string;
  domain: string;
  name: string;
  unit?: string | null;
  data_type: string;
  description: string;
  canonical_min?: number | null;
  canonical_max?: number | null;
  optimal_min?: number | null;
  optimal_max?: number | null;
  allowed_categories?: string[] | null;
}

export interface EvidenceSource {
  id: string;
  title: string;
  institution: string;
  year: number;
  citation: string;
  doi_or_url?: string | null;
  evidence_type: string;
  confidence_grade: 'high' | 'moderate' | 'preliminary';
  summary?: string | null;
}

export interface EcologicalRelationship {
  id: string;
  name: string;
  source_metric: string;
  operator: string;
  threshold_value: any;
  target_metric: string;
  target_state: string;
  relationship_type: string;
  direction: string;
  ecological_mechanism: string;
  evidence_ids: string[];
  evidence_strength: string;
  confidence: number;
  ecosystem_context?: string | null;
}

export interface VariableStatus {
  metric_id: string;
  domain: string;
  name: string;
  status: 'observed' | 'inferred' | 'unknown';
  observed_value?: any;
}

export interface InferredPressure {
  pressure_id: string;
  name: string;
  target_metric: string;
  inferred_state: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  triggering_metric: string;
  triggering_value?: any;
  condition_matched: string;
  ecological_mechanism: string;
  evidence_ids: string[];
  confidence: number;
  chain_depth: number;
}

export interface MultiMetricCompoundPressure {
  compound_id: string;
  name: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  participating_metrics: string[];
  triggering_conditions: Record<string, string>;
  synergistic_mechanism: string;
  evidence_ids: string[];
  confidence: number;
}

export interface ReasoningChainLink {
  step: number;
  from_concept: string;
  to_concept: string;
  relationship_id: string;
  relationship_type: string;
  ecological_mechanism: string;
  evidence_ids: string[];
}

export interface ReasoningChain {
  chain_id: string;
  root_observed_metric: string;
  root_observed_value?: any;
  final_pressure: string;
  links: ReasoningChainLink[];
  narrative_summary: string;
}

export interface ReasoningEvaluationResult {
  observed_metrics: Record<string, any>;
  variables_status: VariableStatus[];
  inferred_pressures: InferredPressure[];
  compound_pressures: MultiMetricCompoundPressure[];
  reasoning_chains: ReasoningChain[];
  unknown_metrics_count: number;
  observed_metrics_count: number;
  inferred_pressures_count: number;
}

// ==============================================================================
// SCIENTIFIC CORPUS & RAG INTERFACES (PHASE 4)
// ==============================================================================

export interface ScientificDocument {
  id: string;
  title: string;
  authors: string;
  organization: string;
  year: number;
  source_type: 'global_assessment' | 'systematic_review' | 'meta_analysis' | 'peer_reviewed_journal' | 'institutional_report';
  citation: string;
  url?: string | null;
  doi?: string | null;
  geographic_scope: string;
  ecosystem: string;
  topics: string[];
  environmental_metrics: string[];
  evidence_strength: string;
  abstract?: string | null;
  chunk_count: number;
  created_at?: string | null;
}

export interface ScientificChunk {
  id: string;
  document_id: string;
  chunk_index: number;
  content: string;
  section?: string | null;
  metrics: string[];
  ecosystem: string;
  geographic_scope: string;
  evidence_strength: string;
  confidence_grade: string;
  citation: string;
  doi?: string | null;
  url?: string | null;
}

export interface ScientificSearchQuery {
  query: string;
  metrics?: string[] | null;
  ecosystem?: string | null;
  geographic_scope?: string | null;
  min_evidence_strength?: string | null;
  top_k?: number;
}

export interface EvidenceChunkPacket {
  chunk_id: string;
  document_id: string;
  title: string;
  authors: string;
  organization: string;
  year: number;
  citation: string;
  doi?: string | null;
  url?: string | null;
  content: string;
  relevance_score: number;
  evidence_strength: string;
  confidence_grade: string;
  geographic_scope: string;
  ecosystem: string;
  matched_metrics: string[];
  geographic_applicability: 'globally_relevant' | 'regionally_relevant' | 'ecosystem_specific' | 'geographically_mismatched';
}

export interface EvidencePacketResponse {
  query: string;
  total_found: number;
  selected_count: number;
  evidence_chunks: EvidenceChunkPacket[];
  insufficient_evidence: boolean;
  geographic_context_summary?: string | null;
  contradiction_notes?: string | null;
}

// ==============================================================================
// MULTI-METRIC REASONING & NATURE PRESSURE INTERFACES (PHASE 5)
// ==============================================================================

export interface NaturePressure {
  pressure_id: string;
  pressure_type: string;
  name: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'unknown';
  contributing_metrics: string[];
  observed_conditions: Record<string, any>;
  inferred_mechanisms: string[];
  reasoning_chain?: ReasoningChain | null;
  evidence_packet: EvidenceChunkPacket[];
  evidence_strength: string;
  confidence: number;
  geographic_applicability: 'globally_relevant' | 'regionally_relevant' | 'ecosystem_specific' | 'geographically_mismatched';
  contradictory_evidence_notes?: string | null;
  uncertainty_and_limitations: string[];
}

export interface MultiMetricAnalysisResponse {
  observed_conditions: Record<string, any>;
  variables_status: VariableStatus[];
  pressures: NaturePressure[];
  multi_metric_synergies: MultiMetricCompoundPressure[];
  reasoning_chains: ReasoningChain[];
  total_evidence_chunks_attached: number;
  observed_metrics_count: number;
  unknown_metrics_count: number;
  system_limitations: string[];
  evaluation_timestamp: string;
}

// ==============================================================================
// NATURE RISK PROFILE INTERFACES (PHASE 6)
// ==============================================================================

export type RiskLevel = 'low' | 'medium' | 'high' | 'unknown';

export interface ExplainabilityChainStep {
  stage: string;
  description: string;
  details: Record<string, any>;
}

export interface ExplainabilityChain {
  dimension: string;
  observed_conditions: Record<string, any>;
  ecological_drivers: string[];
  biophysical_mechanism: string;
  nature_pressure: string;
  evidence_citations: string[];
  steps: ExplainabilityChainStep[];
}

export interface RiskDimension {
  dimension_id: string;
  name: string;
  level: RiskLevel;
  contributing_metrics: string[];
  observed_conditions: Record<string, any>;
  inferred_drivers: string[];
  ecological_reasoning_chain?: ReasoningChain | null;
  explainability_chain?: ExplainabilityChain | null;
  evidence_ids: string[];
  evidence_chunks: EvidenceChunkPacket[];
  evidence_strength: string;
  geographic_applicability: string;
  uncertainty: string;
  limitations: string[];
}

export interface NatureRiskProfile {
  water_stress: RiskDimension;
  habitat_pressure: RiskDimension;
  biodiversity_pressure: RiskDimension;
  climate_exposure: RiskDimension;
  human_disturbance: RiskDimension;
  overall_limitations: string[];
  missing_important_variables: string[];
  evidence_summary: EvidenceChunkPacket[];
  evaluation_timestamp: string;
}

export interface RiskDimensionMetadata {
  dimension_id: string;
  name: string;
  evaluates: string[];
  biophysical_basis: string;
  levels: string[];
  evidence_sources: string[];
}

// ==============================================================================
// AUTHORITATIVE ENVIRONMENTAL DATASETS & PROVENANCE (PHASE 7)
// ==============================================================================

export type QualitySeverity = 'info' | 'warning' | 'error';

export interface DataQualityCheck {
  metric_name: string;
  flag_type: string;
  severity: QualitySeverity;
  message: string;
  original_value?: any;
  transformed_value?: any;
  applied_rule?: string | null;
}

export interface VariableProvenance {
  variable_name: string;
  dataset_id: string;
  dataset_name: string;
  source_organization: string;
  source_url: string;
  license: string;
  raw_value?: any;
  raw_unit?: string | null;
  canonical_value?: any;
  canonical_unit: string;
  spatial_resolution: string;
  temporal_coverage: string;
  retrieval_date: string;
  is_synthetic: boolean;
  known_limitations: string[];
}

export interface DatasetMetadata {
  id: string;
  name: string;
  source_organization: string;
  source_url: string;
  license: string;
  domain: string;
  variables: string[];
  raw_units: Record<string, string>;
  canonical_units: Record<string, string>;
  geographic_coverage: string;
  temporal_coverage: string;
  spatial_resolution: string;
  retrieval_date: string;
  provenance: string;
  known_limitations: string[];
  is_authoritative: boolean;
}

export interface DataQualityReport {
  total_checks: number;
  passed_checks: number;
  warnings_count: number;
  errors_count: number;
  is_valid: boolean;
  checks: DataQualityCheck[];
  missing_variables: string[];
  zero_variables: string[];
  synthetic_count: number;
}

export interface PointQueryResult {
  latitude: number;
  longitude: number;
  canonical_state: EnvironmentalState;
  provenance_records: Record<string, VariableProvenance>;
  quality_report: DataQualityReport;
  datasets_queried: string[];
  is_fully_authoritative: boolean;
  has_synthetic_data: boolean;
}

export interface StateEnrichmentRequest {
  state: EnvironmentalState;
  latitude?: number | null;
  longitude?: number | null;
  overwrite_existing?: boolean;
  allow_synthetic_fallback?: boolean;
}

export interface StateEnrichmentResponse {
  enriched_state: EnvironmentalState;
  metrics_added_count: number;
  metrics_preserved_count: number;
  provenance_records: Record<string, VariableProvenance>;
  quality_report: DataQualityReport;
}

// ==============================================================================
// ECOLOGICAL FINDINGS & PIPELINE INTERFACES (PHASE 9)
// ==============================================================================

export type ObservationSource = 'user_supplied' | 'dataset_derived' | 'inferred' | 'unknown';

export type ConflictType =
  | 'user_dataset_discrepancy'
  | 'geographic_mismatch'
  | 'temporal_outdated'
  | 'conflicting_evidence'
  | 'missing_key_variables'
  | 'insufficient_evidence';

export interface ConflictReport {
  conflict_id: string;
  conflict_type: ConflictType;
  variables_involved: string[];
  user_value?: any;
  dataset_value?: any;
  delta_percentage?: number | null;
  message: string;
  resolution_strategy: string;
  uncertainty_penalty: number;
}

export interface VariableFindingDetail {
  variable_id: string;
  name: string;
  value?: any;
  unit?: string | null;
  source: ObservationSource;
  dataset_id?: string | null;
  is_synthetic: boolean;
  confidence: number;
}

export interface EcologicalFinding {
  finding_id: string;
  title: string;
  domain: string;
  severity: 'critical' | 'high' | 'medium' | 'low' | 'unknown';
  contributing_variables: string[];
  variable_details: VariableFindingDetail[];
  inferred_pressure: string;
  ecological_mechanism: string;
  supporting_relationships: string[];
  reasoning_chain?: ReasoningChain | null;
  uncertainty_level: 'low' | 'medium' | 'high';
  uncertainty_factors: string[];
  conflict_flags: string[];
  confidence: number;
  evidence_references: EvidenceChunkPacket[];
  geographic_relevance: string;
}

export interface EcologicalFindingsRequest {
  text_description?: string | null;
  state?: EnvironmentalState | null;
  latitude?: number | null;
  longitude?: number | null;
  region?: string | null;
  ecosystem?: string | null;
  enrich_from_datasets?: boolean;
  overwrite_user_values?: boolean;
  allow_synthetic_fallback?: boolean;
  top_k_evidence?: number;
}

export interface EcologicalFindingsResponse {
  canonical_state: EnvironmentalState;
  provenance_map: Record<string, VariableProvenance>;
  variables_status: VariableStatus[];
  observed_user_metrics_count: number;
  dataset_derived_metrics_count: number;
  unknown_metrics_count: number;
  findings: EcologicalFinding[];
  total_findings_count: number;
  conflicts_detected: ConflictReport[];
  has_conflicts: boolean;
  overall_confidence_score: number;
  system_limitations: string[];
  evaluation_timestamp: string;
}

// ==============================================================================
// INTERVENTION & CONVERSATIONAL INTELLIGENCE INTERFACES (PHASES 10-14)
// ==============================================================================

export interface ExpectedMetricEffect {
  metric_id: string;
  metric_name: string;
  direction: 'increase' | 'decrease' | 'stabilize' | 'mitigate';
  magnitude: 'high' | 'moderate' | 'low';
  quantitative_estimate?: string | null;
}

export interface ExplanationChainModel {
  observed_facts: string[];
  inferred_reasoning: string[];
  ecological_pressure: string;
  ecological_mechanism: string;
  intervention_action: string;
  expected_metric_effects: ExpectedMetricEffect[];
  scientific_evidence_summary: string[];
}

export interface FeasibilityEvaluationModel {
  status: 'Suitable' | 'Conditionally suitable' | 'Insufficient information' | 'Not currently suitable';
  reason: string;
  evaluations: Record<string, string>;
}

export interface ValidatedClaimModel {
  claim_text: string;
  claim_type: string;
  is_supported: boolean;
  evidence_backed: boolean;
  uncertainty_preserved: boolean;
  validation_status: string;
  justification: string;
}

export interface ScientificValidationPacket {
  validated_claims: ValidatedClaimModel[];
  evidence_support_summary: string;
  uncertainty_statement: string;
  conflict_resolution_notes: string[];
  context_specific_tradeoffs: string[];
  limitations: string[];
}

export interface RecommendationConfidenceBasis {
  overall_confidence: number;
  evidence_grade: string;
  pressure_relevance_score: number;
  biophysical_suitability_score: number;
  data_completeness_factor: number;
  conflict_uncertainty_penalty: number;
  justification_summary: string;
}

export interface InterventionRecommendation {
  recommendation_id: string;
  intervention_id: string;
  recommendation: string;
  title: string;
  category: string;
  addressed_findings: string[];
  addressed_pressures: string[];
  what_to_do: string;
  why_it_works: string;
  ecological_mechanism: string;
  target_metrics: string[];
  impacted_metrics: ExpectedMetricEffect[];
  expected_metric_effects: ExpectedMetricEffect[];
  explanation_chain: ExplanationChainModel;
  feasibility: FeasibilityEvaluationModel;
  validation: ScientificValidationPacket;
  time_horizon: string;
  evidence_ids: string[];
  evidence_references: EvidenceChunkPacket[];
  confidence_basis: RecommendationConfidenceBasis;
  constraints: string[];
  tradeoffs: string[];
  limitations: string[];
  relevance_rank: number;
}

export interface RecommendationSetResponse {
  recommendations: InterventionRecommendation[];
  total_recommendations: number;
  parameters_evaluated: number;
  evaluation_timestamp: string;
}

export interface ParameterProvenance {
  source: string;
  timestamp: string;
  confidence: number;
}

export interface EnvironmentalMemory {
  land_use?: string | null;
  land_cover?: string | null;
  rainfall?: number | null;
  temperature?: number | null;
  soil_organic_carbon?: number | null;
  soil_ph?: number | null;
  soil_moisture?: number | null;
  habitat_diversity?: string | null;
  species_richness?: number | null;
  deforestation?: number | null;
  pollution?: number | null;
  ecosystem?: string | null;
  provenance: Record<string, ParameterProvenance>;
}

export interface ClarificationQuestionObject {
  question_id?: string;
  question_text: string;
  context?: string;
  target_variable?: string;
  suggested_answers?: string[];
}

export type ClarificationQuestionItem = string | ClarificationQuestionObject;

export interface ConversationChatResponse {
  session_id: string;
  conversational_response: string;
  environmental_memory: EnvironmentalMemory;
  needs_clarification: boolean;
  clarification_questions: ClarificationQuestionItem[];
  detected_conflicts: string[];
  recommendations: InterventionRecommendation[];
  active_risk_profile?: Record<string, any> | null;
}

export interface ModelMemoryInfo {
  provider: string;
  model_name: string;
  estimated_memory_mb: number;
  cache_entries: number;
  status: string;
}

export interface DatabasePerformanceInfo {
  status: string;
  dialect: string;
  pgvector_enabled: boolean;
  fallback_active: boolean;
  pool_size: number;
  connection_latency_ms: number;
}

export interface SystemPerformanceResponse {
  timestamp: string;
  average_api_latency_ms: number;
  database: DatabasePerformanceInfo;
  models: Record<string, ModelMemoryInfo>;
  system_resources: Record<string, any>;
}





