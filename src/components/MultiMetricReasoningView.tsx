import React, { useState, useEffect } from 'react';
import {
  AlertTriangle,
  BookOpen,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  ExternalLink,
  Layers,
  Link2,
  RefreshCw,
  Search,
  ShieldAlert,
  Sparkles,
  Info,
} from 'lucide-react';
import { EnvironmentalState, MultiMetricAnalysisResponse, NaturePressure } from '../types';
import { analyzeMultiMetricReasoning } from '../services/api';

interface MultiMetricReasoningViewProps {
  state: EnvironmentalState;
}

export const MultiMetricReasoningView: React.FC<MultiMetricReasoningViewProps> = ({ state }) => {
  const [loading, setLoading] = useState<boolean>(false);
  const [analysisResult, setAnalysisResult] = useState<MultiMetricAnalysisResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedPressureId, setSelectedPressureId] = useState<string | null>(null);
  const [expandedChains, setExpandedChains] = useState<Record<string, boolean>>({});

  const executeAnalysis = async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeMultiMetricReasoning(state);
      setAnalysisResult(result);
      if (result.pressures.length > 0 && !selectedPressureId) {
        setSelectedPressureId(result.pressures[0].pressure_id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Multi-metric analysis failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    executeAnalysis();
  }, [
    state.soil.ph,
    state.soil.organic_carbon,
    state.soil.moisture,
    state.climate.rainfall,
    state.climate.temperature,
    state.land.land_use,
    state.land.land_cover,
    state.biodiversity.species_richness,
    state.biodiversity.habitat_diversity,
    state.human_impact.deforestation,
    state.human_impact.pollution,
    state.spatial_context.ecosystem,
    state.spatial_context.region,
  ]);

  const toggleChain = (chainId: string) => {
    setExpandedChains((prev) => ({ ...prev, [chainId]: !prev[chainId] }));
  };

  const selectedPressure = analysisResult?.pressures.find(
    (p) => p.pressure_id === selectedPressureId
  );

  const getSeverityBadge = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
        return (
          <span className="px-2 py-0.5 text-2xs font-mono uppercase font-semibold bg-rose-100 text-rose-800 border border-rose-200 rounded-sm">
            Critical Severity
          </span>
        );
      case 'high':
        return (
          <span className="px-2 py-0.5 text-2xs font-mono uppercase font-semibold bg-amber-100 text-amber-800 border border-amber-200 rounded-sm">
            High Severity
          </span>
        );
      case 'medium':
        return (
          <span className="px-2 py-0.5 text-2xs font-mono uppercase font-semibold bg-blue-100 text-blue-800 border border-blue-200 rounded-sm">
            Medium Severity
          </span>
        );
      default:
        return (
          <span className="px-2 py-0.5 text-2xs font-mono uppercase font-semibold bg-stone-100 text-stone-700 border border-stone-200 rounded-sm">
            Low / Baseline
          </span>
        );
    }
  };

  const getApplicabilityBadge = (app: string) => {
    switch (app) {
      case 'globally_relevant':
        return (
          <span className="px-1.5 py-0.5 text-3xs font-mono uppercase bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-sm">
            Globally Relevant
          </span>
        );
      case 'ecosystem_specific':
        return (
          <span className="px-1.5 py-0.5 text-3xs font-mono uppercase bg-purple-50 text-purple-800 border border-purple-200 rounded-sm">
            Ecosystem Specific
          </span>
        );
      case 'regionally_relevant':
        return (
          <span className="px-1.5 py-0.5 text-3xs font-mono uppercase bg-cyan-50 text-cyan-800 border border-cyan-200 rounded-sm">
            Regionally Relevant
          </span>
        );
      default:
        return (
          <span className="px-1.5 py-0.5 text-3xs font-mono uppercase bg-amber-50 text-amber-800 border border-amber-200 rounded-sm">
            Biome Context Alert
          </span>
        );
    }
  };

  return (
    <div className="bg-white border border-stone-200 rounded-sm p-6 shadow-xs space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between pb-4 border-b border-stone-100 gap-3">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-stone-800">
              Multi-Metric Ecological Reasoning & Scientific RAG
            </h2>
            <span className="text-2xs font-mono px-2 py-0.5 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-sm font-medium">
              Phase 4 & 5 Active
            </span>
          </div>
          <p className="text-xs text-stone-500 mt-1 max-w-3xl">
            Deterministic forward-chaining across ≥3 environmental variables coupled with two-stage
            semantic vector retrieval from IPCC, IPBES, FAO, UNEP, and peer-reviewed literature.
          </p>
        </div>

        <button
          onClick={executeAnalysis}
          disabled={loading}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-stone-700 bg-stone-50 hover:bg-stone-100 border border-stone-300 rounded-sm shadow-2xs transition-colors disabled:opacity-50 self-start md:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin text-emerald-600' : ''}`} />
          {loading ? 'Evaluating Knowledge & RAG...' : 'Re-Evaluate State'}
        </button>
      </div>

      {error && (
        <div className="p-3 bg-rose-50 border border-rose-200 rounded-sm text-xs text-rose-800 flex items-start gap-2">
          <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold">Reasoning Evaluation Error</p>
            <p className="mt-0.5 text-rose-700">{error}</p>
          </div>
        </div>
      )}

      {/* Metric Observations Bar */}
      {analysisResult && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-stone-50 p-3 border border-stone-200 rounded-sm text-xs">
          <div>
            <span className="text-stone-500 text-3xs font-mono uppercase block">Observed Metrics</span>
            <span className="text-sm font-semibold text-stone-800 font-mono">
              {analysisResult.observed_metrics_count} variables
            </span>
          </div>
          <div>
            <span className="text-stone-500 text-3xs font-mono uppercase block">Unknown / Missing</span>
            <span className="text-sm font-semibold text-amber-700 font-mono">
              {analysisResult.unknown_metrics_count} variables
            </span>
          </div>
          <div>
            <span className="text-stone-500 text-3xs font-mono uppercase block">Inferred Pressures</span>
            <span className="text-sm font-semibold text-rose-700 font-mono">
              {analysisResult.pressures.length} detected
            </span>
          </div>
          <div>
            <span className="text-stone-500 text-3xs font-mono uppercase block">Evidence Chunks Attached</span>
            <span className="text-sm font-semibold text-emerald-700 font-mono">
              {analysisResult.total_evidence_chunks_attached} verified
            </span>
          </div>
        </div>
      )}

      {/* Main Analysis Body */}
      {analysisResult && (
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Column: List of Detected Pressures */}
          <div className="lg:col-span-5 space-y-3">
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-stone-600 flex items-center justify-between">
              <span>Nature Pressure Profiles</span>
              <span className="text-stone-400 font-normal">({analysisResult.pressures.length})</span>
            </h3>

            {analysisResult.pressures.length === 0 ? (
              <div className="p-4 bg-emerald-50/50 border border-emerald-200 rounded-sm text-xs text-emerald-900">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 mb-1" />
                <p className="font-semibold">No Critical Pressures Inferred</p>
                <p className="mt-1 text-emerald-700 text-2xs">
                  Observed environmental indicators fall within healthy baseline boundaries.
                </p>
              </div>
            ) : (
              <div className="space-y-2">
                {analysisResult.pressures.map((pressure, pIdx) => {
                  const isSelected = pressure.pressure_id === selectedPressureId;
                  return (
                    <div
                      key={`${pressure.pressure_id}-${pIdx}`}
                      onClick={() => setSelectedPressureId(pressure.pressure_id)}
                      className={`p-3.5 border rounded-sm cursor-pointer transition-all ${
                        isSelected
                          ? 'border-emerald-500 bg-emerald-50/20 shadow-xs ring-1 ring-emerald-400/50'
                          : 'border-stone-200 bg-white hover:border-stone-300 hover:bg-stone-50/50'
                      }`}
                    >
                      <div className="flex items-start justify-between gap-2 mb-1.5">
                        <span className="text-xs font-semibold text-stone-800 leading-snug">
                          {pressure.name}
                        </span>
                        {getSeverityBadge(pressure.severity)}
                      </div>

                      <div className="flex flex-wrap gap-1 mt-2">
                        {pressure.contributing_metrics.map((metric, mIdx) => (
                          <span
                            key={`${metric}-${mIdx}`}
                            className="px-1.5 py-0.5 text-3xs font-mono bg-stone-100 text-stone-700 border border-stone-200 rounded-2xs"
                          >
                            {metric}
                          </span>
                        ))}
                      </div>

                      <div className="mt-2.5 flex items-center justify-between text-3xs text-stone-500 pt-2 border-t border-stone-100">
                        <span className="flex items-center gap-1">
                          <BookOpen className="w-3 h-3 text-emerald-600" />
                          {pressure.evidence_packet.length} Evidence Chunks
                        </span>
                        <span className="font-mono text-stone-400">
                          Certainty: {(pressure.confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Right Column: Deep Explainability & Scientific Evidence Chunks */}
          <div className="lg:col-span-7">
            {selectedPressure ? (
              <div className="border border-stone-200 rounded-sm bg-stone-50/40 p-4 space-y-5">
                {/* Pressure Header */}
                <div>
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-3xs font-mono uppercase text-stone-500">
                      Pressure Inspection: {selectedPressure.pressure_id}
                    </span>
                    {getSeverityBadge(selectedPressure.severity)}
                  </div>
                  <h3 className="text-sm font-bold text-stone-900">{selectedPressure.name}</h3>
                </div>

                {/* Observed Trigger Conditions */}
                <div className="bg-white p-3 border border-stone-200 rounded-sm">
                  <h4 className="text-2xs font-mono uppercase font-semibold text-stone-600 mb-2 flex items-center gap-1.5">
                    <Layers className="w-3 h-3 text-stone-500" />
                    Observed Trigger Conditions (≥3 Variables)
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                    {Object.entries(selectedPressure.observed_conditions).map(([metric, val]) => (
                      <div key={metric} className="p-2 bg-stone-50 border border-stone-100 rounded-2xs">
                        <span className="text-3xs font-mono text-stone-500 block">{metric}</span>
                        <span className="font-mono font-medium text-stone-800 text-2xs">
                          {String(val)}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Biophysical Mechanisms */}
                <div className="bg-white p-3 border border-stone-200 rounded-sm space-y-2">
                  <h4 className="text-2xs font-mono uppercase font-semibold text-stone-600 flex items-center gap-1.5">
                    <Info className="w-3 h-3 text-stone-500" />
                    Biophysical Ecological Mechanisms
                  </h4>
                  <ul className="space-y-1.5 text-xs text-stone-700">
                    {selectedPressure.inferred_mechanisms.map((mech, idx) => (
                      <li key={idx} className="flex items-start gap-2">
                        <span className="text-emerald-600 font-bold text-xs mt-0.5">•</span>
                        <span>{mech}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Causal Reasoning Chain */}
                {selectedPressure.reasoning_chain && (
                  <div className="bg-white p-3 border border-stone-200 rounded-sm">
                    <div
                      className="flex items-center justify-between cursor-pointer"
                      onClick={() => toggleChain(selectedPressure.reasoning_chain!.chain_id)}
                    >
                      <h4 className="text-2xs font-mono uppercase font-semibold text-stone-600 flex items-center gap-1.5">
                        <Link2 className="w-3 h-3 text-emerald-600" />
                        Causal Reasoning Chain
                      </h4>
                      {expandedChains[selectedPressure.reasoning_chain.chain_id] ? (
                        <ChevronDown className="w-3.5 h-3.5 text-stone-400" />
                      ) : (
                        <ChevronRight className="w-3.5 h-3.5 text-stone-400" />
                      )}
                    </div>

                    <p className="text-xs text-stone-600 mt-2 italic bg-emerald-50/40 p-2.5 rounded-2xs border border-emerald-100">
                      "{selectedPressure.reasoning_chain.narrative_summary}"
                    </p>

                    {expandedChains[selectedPressure.reasoning_chain.chain_id] && (
                      <div className="mt-3 space-y-2 pt-2 border-t border-stone-100">
                        {selectedPressure.reasoning_chain.links.map((link, linkIdx) => (
                          <div
                            key={`${link.relationship_id}-${link.step}-${linkIdx}`}
                            className="p-2.5 bg-stone-50 border border-stone-200 rounded-2xs text-xs space-y-1"
                          >
                            <div className="flex items-center justify-between text-3xs font-mono text-stone-500">
                              <span>Step {link.step}: [{link.relationship_type.toUpperCase()}]</span>
                              <span className="text-emerald-700">{link.relationship_id}</span>
                            </div>
                            <div className="font-semibold text-stone-800 text-2xs">
                              {link.from_concept} → <span className="text-rose-700">{link.to_concept}</span>
                            </div>
                            <p className="text-stone-600 text-3xs">{link.ecological_mechanism}</p>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                {/* Attached Scientific Evidence Packets (RAG) */}
                <div className="bg-white p-3 border border-stone-200 rounded-sm space-y-3">
                  <div className="flex items-center justify-between">
                    <h4 className="text-2xs font-mono uppercase font-semibold text-stone-700 flex items-center gap-1.5">
                      <BookOpen className="w-3.5 h-3.5 text-emerald-700" />
                      Retrieved Scientific Evidence Packets ({selectedPressure.evidence_packet.length})
                    </h4>
                    {getApplicabilityBadge(selectedPressure.geographic_applicability)}
                  </div>

                  <div className="space-y-3">
                    {selectedPressure.evidence_packet.map((chunk, cIdx) => (
                      <div
                        key={`${chunk.chunk_id}-${cIdx}`}
                        className="p-3 bg-stone-50/70 border border-stone-200 rounded-2xs text-xs space-y-2"
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div>
                            <span className="text-2xs font-bold text-stone-800 block">
                              {chunk.title}
                            </span>
                            <span className="text-3xs text-stone-500 font-mono">
                              {chunk.authors} ({chunk.year}) • {chunk.organization}
                            </span>
                          </div>
                          <span className="px-1.5 py-0.5 text-3xs font-mono bg-emerald-100 text-emerald-900 border border-emerald-200 rounded-2xs shrink-0">
                            Score: {(chunk.relevance_score * 100).toFixed(0)}%
                          </span>
                        </div>

                        <p className="text-2xs text-stone-700 bg-white p-2.5 rounded-2xs border border-stone-200/80 leading-relaxed font-serif">
                          "{chunk.content}"
                        </p>

                        <div className="flex flex-wrap items-center justify-between gap-2 text-3xs text-stone-500 pt-1 border-t border-stone-200/60 font-mono">
                          <span className="truncate max-w-sm" title={chunk.citation}>
                            {chunk.citation}
                          </span>
                          {chunk.doi && (
                            <span className="text-emerald-700">DOI: {chunk.doi}</span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Uncertainty & Limitations */}
                {selectedPressure.uncertainty_and_limitations.length > 0 && (
                  <div className="p-3 bg-amber-50/60 border border-amber-200 rounded-sm text-xs text-amber-900 space-y-1">
                    <span className="font-semibold text-2xs uppercase tracking-wider block font-mono">
                      Ecological Constraints & Boundary Sensitivity
                    </span>
                    <ul className="list-disc list-inside space-y-0.5 text-2xs text-amber-800">
                      {selectedPressure.uncertainty_and_limitations.map((lim, i) => (
                        <li key={i}>{lim}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ) : (
              <div className="p-8 border border-dashed border-stone-200 rounded-sm text-center text-xs text-stone-500">
                Select a nature pressure profile from the left column to inspect its biophysical
                mechanisms, causal reasoning chain, and attached scientific RAG evidence packets.
              </div>
            )}
          </div>
        </div>
      )}

      {/* System Scientific Integrity Guarantee */}
      {analysisResult?.system_limitations && (
        <div className="p-3 bg-stone-50 border border-stone-200 rounded-sm text-3xs text-stone-500 space-y-1 font-mono">
          <span className="font-bold uppercase text-stone-700 block">Scientific Integrity Directives:</span>
          {analysisResult.system_limitations.map((lim, idx) => (
            <p key={idx}>• {lim}</p>
          ))}
        </div>
      )}
    </div>
  );
};
