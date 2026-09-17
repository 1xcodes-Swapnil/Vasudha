import React from 'react';
import { ArrowRight, BookOpen, Compass, CheckCircle, Network, FileText, BarChart3, ShieldCheck } from 'lucide-react';
import { PipelineStageInfo } from '../types';

const PIPELINE_STAGES: PipelineStageInfo[] = [
  { key: 'input', label: '1. User Input', description: 'Query, coordinates, or environmental observations', phase: 'Phase 0 (Foundation)', status: 'ready' },
  { key: 'environmental_state', label: '2. Environmental State', description: 'Soil (pH, carbon, moisture), climate, biodiversity, land use', phase: 'Phase 1 (Knowledge/Data)', status: 'ready' },
  { key: 'geo_context', label: '3. Geo Context', description: 'Biome, ecoregion, elevation, regional ecological baselines', phase: 'Phase 1 (Knowledge/Data)', status: 'ready' },
  { key: 'multi_metric_reasoning', label: '4. Multi-Metric Reasoning', description: 'Structured ecological relationships across ≥3 variables', phase: 'Phase 2 (Reasoning)', status: 'ready' },
  { key: 'scientific_rag', label: '5. Scientific RAG', description: 'Hybrid vector + structured retrieval (IPCC, IPBES, FAO, UNEP)', phase: 'Phase 4 (RAG & Corpus)', status: 'ready' },
  { key: 'nature_risk_profile', label: '6. Nature Risk Profile', description: 'Degradation vectors, tipping points, biodiversity loss risk', phase: 'Phase 6 (Risk Diagnosis)', status: 'ready' },
  { key: 'intervention_engine', label: '7. Intervention Engine', description: 'Ecological interventions tailored to specific biome constraints', phase: 'Phase 7 (Interventions)', status: 'pending' },
  { key: 'feasibility_check', label: '8. Feasibility Check', description: 'Resource, climatic, seasonal, and land-use constraints', phase: 'Phase 3 (Interventions)', status: 'pending' },
  { key: 'evidence_mapping', label: '9. Evidence Mapping', description: 'Direct citations & quantitative backing for all proposed actions', phase: 'Phase 3 (Interventions)', status: 'pending' },
  { key: 'claim_validation', label: '10. Claim Validation', description: 'Guardrail ensuring LLM does not hallucinate scientific claims', phase: 'Phase 3 (Interventions)', status: 'pending' },
  { key: 'explanation', label: '11. Explanation ("Why")', description: 'Observed conditions → Mechanism → Intervention → Metric effects', phase: 'Phase 3 (Interventions)', status: 'pending' },
  { key: 'trade_offs', label: '12. Trade-offs', description: 'Ecological, resource, land-use, and implementation trade-offs', phase: 'Phase 3 (Interventions)', status: 'pending' },
  { key: 'response', label: '13. Response Synthesis', description: 'Rigorous, evidence-backed actionable intelligence report', phase: 'Phase 4 (UI/E2E)', status: 'pending' },
];

export const ArchitecturePipelineView: React.FC = () => {
  return (
    <div className="bg-white border border-stone-200 rounded-sm p-6 shadow-xs">
      <div className="flex items-center justify-between pb-3 border-b border-stone-100 mb-5">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-stone-700">
            End-to-End Ecological Reasoning Pipeline
          </h2>
          <p className="text-xs text-stone-500 mt-0.5">
            Strict pipeline architecture ensuring the LLM is never the ungrounded scientific source of truth.
          </p>
        </div>
        <span className="text-xs font-mono px-2 py-0.5 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-sm">
          Stage 0: Pipeline Configured
        </span>
      </div>

      {/* Layer Architecture Breakdown */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-3 mb-6 text-xs">
        <div className="p-3 border border-stone-200 rounded-sm bg-stone-50">
          <div className="flex items-center gap-1.5 font-semibold text-stone-800 mb-1">
            <Compass className="w-3.5 h-3.5 text-stone-600" />
            Presentation Layer
          </div>
          <p className="text-stone-500">React + TypeScript UI with interactive map and explainability chain views.</p>
        </div>

        <div className="p-3 border border-stone-200 rounded-sm bg-stone-50">
          <div className="flex items-center gap-1.5 font-semibold text-stone-800 mb-1">
            <Network className="w-3.5 h-3.5 text-stone-600" />
            Application/API Layer
          </div>
          <p className="text-stone-500">FastAPI routers, Pydantic validation, centralized logging, and error handling.</p>
        </div>

        <div className="p-3 border border-stone-200 rounded-sm bg-stone-50">
          <div className="flex items-center gap-1.5 font-semibold text-stone-800 mb-1">
            <BarChart3 className="w-3.5 h-3.5 text-stone-600" />
            Intelligence Layer
          </div>
          <p className="text-stone-500">Multi-metric reasoning, risk assessment, intervention engine, claim validation.</p>
        </div>

        <div className="p-3 border border-stone-200 rounded-sm bg-stone-50">
          <div className="flex items-center gap-1.5 font-semibold text-stone-800 mb-1">
            <BookOpen className="w-3.5 h-3.5 text-stone-600" />
            Knowledge Layer
          </div>
          <p className="text-stone-500">Scientific evidence store (IPCC, IPBES, FAO), ecological rules, local embeddings.</p>
        </div>

        <div className="p-3 border border-stone-200 rounded-sm bg-stone-50">
          <div className="flex items-center gap-1.5 font-semibold text-stone-800 mb-1">
            <ShieldCheck className="w-3.5 h-3.5 text-stone-600" />
            Data Layer
          </div>
          <p className="text-stone-500">PostgreSQL + pgvector for high-dimensional semantic search and structured datasets.</p>
        </div>
      </div>

      {/* Pipeline Sequence Grid */}
      <h3 className="text-xs font-mono uppercase tracking-wider text-stone-500 mb-3">
        13-Stage Pipeline Sequence
      </h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-2.5">
        {PIPELINE_STAGES.map((stage, idx) => (
          <div
            key={stage.key}
            className={`p-3 rounded-sm border text-xs flex flex-col justify-between ${
              stage.status === 'ready'
                ? 'bg-emerald-50/40 border-emerald-300 text-stone-800'
                : 'bg-white border-stone-200 text-stone-600'
            }`}
          >
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="font-semibold text-stone-900">{stage.label}</span>
                {stage.status === 'ready' ? (
                  <span className="text-[10px] font-mono text-emerald-700 bg-emerald-100 px-1 rounded-xs">
                    Phase 0 Setup
                  </span>
                ) : (
                  <span className="text-[10px] font-mono text-stone-400">
                    {stage.phase.split(' ')[0]}
                  </span>
                )}
              </div>
              <p className="text-stone-500 leading-relaxed text-[11px]">{stage.description}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
