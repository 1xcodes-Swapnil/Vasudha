/**
 * VASUDHA — Biodiversity Intelligence
 * Phase 9: Data Integration & Ecological Reasoning Pipeline View
 */

import React, { useState, useEffect } from 'react';
import {
  Sparkles,
  AlertTriangle,
  BookOpen,
  Layers,
  Database,
  Search,
  CheckCircle2,
  RefreshCw,
  HelpCircle,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  MapPin,
  Compass,
  FileText,
  ShieldCheck,
  Zap,
} from 'lucide-react';
import {
  EnvironmentalState,
  EcologicalFinding,
  EcologicalFindingsResponse,
  ConflictReport,
  VariableFindingDetail,
} from '../types';
import { fetchEcologicalFindings } from '../services/api';

interface Props {
  currentState: EnvironmentalState;
  onStateSynced?: (newState: EnvironmentalState) => void;
}

const PRESET_SCENARIOS = [
  {
    name: 'Western Ghats Acidic Degradation',
    text: 'Degraded agricultural plot in Western Ghats at lat 12.5, lon 75.4. Soil pH 5.0, rainfall 2200mm, organic carbon 0.9%, temperature 31°C, deforestation 18%, pollution 42.',
    lat: 12.5,
    lon: 75.4,
  },
  {
    name: 'Serengeti Thermal-Hydro Drought',
    text: 'Semi-arid savanna site at lat -2.5, lon 34.8. Soil moisture 8%, organic carbon 1.1%, rainfall 380mm, temperature 34°C, species richness 14, habitat diversity 20%.',
    lat: -2.5,
    lon: 34.8,
  },
  {
    name: 'Amazon Forest Fragmentation Border',
    text: 'Deforested forest edge at lat -3.5, lon -60.2 with 24% deforestation, chemical pollution index 38, monoculture cropland, species richness 22.',
    lat: -3.5,
    lon: -60.2,
  },
  {
    name: 'Fennoscandia Peatland Historical Acidic Podzol',
    text: 'Boreal histosol site at lat 62.5, lon 18.2 with pH 4.4, soil organic carbon 6.8%, moisture 45%, temperature 12°C, rainfall 650mm.',
    lat: 62.5,
    lon: 18.2,
  },
];

export const EcologicalFindingsPipelineView: React.FC<Props> = ({
  currentState,
  onStateSynced,
}) => {
  const [inputText, setInputText] = useState(
    'Monoculture cropland at lat 12.5, lon 75.4 with soil pH 5.1, organic carbon 0.95%, rainfall 520mm, temperature 32.5°C, deforestation 16%.'
  );
  const [enrichFromDatasets, setEnrichFromDatasets] = useState(true);
  const [overwriteUserValues, setOverwriteUserValues] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [response, setResponse] = useState<EcologicalFindingsResponse | null>(null);
  const [expandedFindings, setExpandedFindings] = useState<Record<string, boolean>>({});

  const handleRunPipeline = async (overrideText?: string, lat?: number, lon?: number) => {
    setLoading(true);
    setError(null);
    try {
      const textToUse = overrideText !== undefined ? overrideText : inputText;
      const res = await fetchEcologicalFindings({
        text_description: textToUse,
        latitude: lat,
        longitude: lon,
        state: currentState,
        enrich_from_datasets: enrichFromDatasets,
        overwrite_user_values: overwriteUserValues,
        allow_synthetic_fallback: true,
        top_k_evidence: 5,
      });
      setResponse(res);
      // Auto-expand first finding
      if (res.findings && res.findings.length > 0) {
        setExpandedFindings({ [res.findings[0].finding_id]: true });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ecological reasoning pipeline failed.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleRunPipeline();
  }, []);

  const toggleExpand = (findingId: string) => {
    setExpandedFindings((prev) => ({
      ...prev,
      [findingId]: !prev[findingId],
    }));
  };

  const getSeverityBadgeClass = (sev: string) => {
    switch (sev?.toLowerCase()) {
      case 'critical':
        return 'bg-red-100 text-red-900 border-red-300';
      case 'high':
        return 'bg-amber-100 text-amber-900 border-amber-300';
      case 'medium':
        return 'bg-yellow-100 text-yellow-900 border-yellow-300';
      default:
        return 'bg-emerald-100 text-emerald-900 border-emerald-300';
    }
  };

  const getSourceBadge = (source: string) => {
    switch (source) {
      case 'user_supplied':
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-mono px-1.5 py-0.5 rounded bg-emerald-100 text-emerald-800 border border-emerald-200">
            <CheckCircle2 className="w-2.5 h-2.5" />
            User Observed
          </span>
        );
      case 'dataset_derived':
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-mono px-1.5 py-0.5 rounded bg-sky-100 text-sky-800 border border-sky-200">
            <Database className="w-2.5 h-2.5" />
            Dataset Derived
          </span>
        );
      case 'inferred':
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-mono px-1.5 py-0.5 rounded bg-purple-100 text-purple-800 border border-purple-200">
            <Sparkles className="w-2.5 h-2.5" />
            Inferred
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 text-[10px] font-mono px-1.5 py-0.5 rounded bg-stone-100 text-stone-600 border border-stone-200">
            <HelpCircle className="w-2.5 h-2.5" />
            Unknown
          </span>
        );
    }
  };

  return (
    <div className="bg-white rounded-xl border border-stone-200 shadow-sm overflow-hidden">
      {/* Header Banner */}
      <div className="bg-stone-900 text-white p-5 border-b border-stone-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 text-[11px] font-mono font-semibold bg-emerald-600 text-white rounded">
              Phase 9
            </span>
            <h2 className="text-lg font-semibold tracking-tight">
              Data Integration & Multi-Metric Ecological Reasoning Pipeline
            </h2>
          </div>
          <p className="text-xs text-stone-300 mt-1 max-w-3xl">
            Transforms user input, geographic context, and authoritative dataset observations into multi-metric
            ecological reasoning grounded in peer-reviewed scientific literature (RAG).
          </p>
        </div>

        <div className="flex items-center gap-2">
          {response && onStateSynced && (
            <button
              onClick={() => onStateSynced(response.canonical_state)}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-emerald-700 hover:bg-emerald-600 text-white border border-emerald-500 transition-colors shadow-sm"
              title="Apply enriched state to global environmental state"
            >
              <Zap className="w-3.5 h-3.5" />
              Sync Enriched State
            </button>
          )}
          <button
            onClick={() => handleRunPipeline()}
            disabled={loading}
            className="inline-flex items-center gap-1.5 px-4 py-1.5 text-xs font-medium rounded-lg bg-emerald-500 hover:bg-emerald-400 text-stone-950 font-semibold transition-colors disabled:opacity-50 shadow-sm"
          >
            {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <Sparkles className="w-3.5 h-3.5" />}
            {loading ? 'Evaluating...' : 'Run Pipeline'}
          </button>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Natural Language & Scenario Controls */}
        <div className="bg-stone-50 border border-stone-200 rounded-lg p-4 space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
            <label className="text-xs font-mono font-bold uppercase tracking-wider text-stone-700 flex items-center gap-1.5">
              <FileText className="w-3.5 h-3.5 text-emerald-600" />
              Site Notes / Natural Language Environmental Description
            </label>
            <div className="flex items-center gap-4 text-xs">
              <label className="flex items-center gap-1.5 cursor-pointer text-stone-600">
                <input
                  type="checkbox"
                  checked={enrichFromDatasets}
                  onChange={(e) => setEnrichFromDatasets(e.target.checked)}
                  className="rounded border-stone-300 text-emerald-600 focus:ring-emerald-500"
                />
                Enrich from Datasets
              </label>
              <label className="flex items-center gap-1.5 cursor-pointer text-stone-600">
                <input
                  type="checkbox"
                  checked={overwriteUserValues}
                  onChange={(e) => setOverwriteUserValues(e.target.checked)}
                  className="rounded border-stone-300 text-emerald-600 focus:ring-emerald-500"
                />
                Overwrite User Values
              </label>
            </div>
          </div>

          <textarea
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            rows={2}
            className="w-full text-xs font-sans p-2.5 bg-white border border-stone-300 rounded-md focus:ring-2 focus:ring-emerald-500 focus:border-emerald-500 text-stone-800"
            placeholder="Describe site conditions (e.g. soil pH 5.2, organic carbon 1.1%, rainfall 480mm, deforestation 14%)..."
          />

          {/* Preset Buttons */}
          <div className="flex flex-wrap items-center gap-1.5 pt-1">
            <span className="text-[11px] font-mono text-stone-500 mr-1">Preset Scenarios:</span>
            {PRESET_SCENARIOS.map((scen, idx) => (
              <button
                key={idx}
                onClick={() => {
                  setInputText(scen.text);
                  handleRunPipeline(scen.text, scen.lat, scen.lon);
                }}
                className="text-[11px] px-2.5 py-1 rounded bg-stone-200/80 hover:bg-stone-300 text-stone-800 font-medium transition-colors"
              >
                {scen.name}
              </button>
            ))}
          </div>
        </div>

        {error && (
          <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-800 text-xs flex items-start gap-2">
            <AlertTriangle className="w-4 h-4 text-red-600 mt-0.5 shrink-0" />
            <div>
              <strong>Pipeline Execution Failed:</strong> {error}
            </div>
          </div>
        )}

        {/* Pipeline Summary Metrics Banner */}
        {response && (
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
            <div className="bg-stone-50 p-3 rounded-lg border border-stone-200">
              <span className="text-[10px] font-mono text-stone-500 uppercase block">User Observed</span>
              <span className="text-xl font-bold text-emerald-700">{response.observed_user_metrics_count}</span>
              <span className="text-[10px] text-stone-500 block">Direct site inputs</span>
            </div>
            <div className="bg-stone-50 p-3 rounded-lg border border-stone-200">
              <span className="text-[10px] font-mono text-stone-500 uppercase block">Dataset Derived</span>
              <span className="text-xl font-bold text-sky-700">{response.dataset_derived_metrics_count}</span>
              <span className="text-[10px] text-stone-500 block">Authoritative sources</span>
            </div>
            <div className="bg-stone-50 p-3 rounded-lg border border-stone-200">
              <span className="text-[10px] font-mono text-stone-500 uppercase block">Unknown / Null</span>
              <span className="text-xl font-bold text-stone-600">{response.unknown_metrics_count}</span>
              <span className="text-[10px] text-stone-500 block">Unmeasured variables</span>
            </div>
            <div className="bg-stone-50 p-3 rounded-lg border border-stone-200">
              <span className="text-[10px] font-mono text-stone-500 uppercase block">Total Findings</span>
              <span className="text-xl font-bold text-stone-900">{response.total_findings_count}</span>
              <span className="text-[10px] text-stone-500 block">Identified pressures</span>
            </div>
            <div className="bg-stone-50 p-3 rounded-lg border border-stone-200">
              <span className="text-[10px] font-mono text-stone-500 uppercase block">Mean Confidence</span>
              <span className="text-xl font-bold text-purple-700">{Math.round(response.overall_confidence_score * 100)}%</span>
              <span className="text-[10px] text-stone-500 block">Penalized for conflicts</span>
            </div>
          </div>
        )}

        {/* Conflicts and Discrepancies Section */}
        {response && response.conflicts_detected && response.conflicts_detected.length > 0 && (
          <div className="bg-amber-50 border border-amber-200 rounded-lg p-4 space-y-2">
            <div className="flex items-center gap-2 text-amber-900 font-semibold text-xs">
              <AlertTriangle className="w-4 h-4 text-amber-600" />
              <span>Data Discrepancies & Geographic Uncertainty Detected ({response.conflicts_detected.length})</span>
            </div>
            <div className="space-y-2">
              {response.conflicts_detected.map((conf: ConflictReport, idx: number) => (
                <div key={idx} className="bg-white/80 p-2.5 rounded border border-amber-200 text-xs space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="font-mono font-bold text-stone-800">{conf.conflict_id}</span>
                    <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-100 text-amber-800 border border-amber-300">
                      -{Math.round(conf.uncertainty_penalty * 100)}% Confidence Penalty
                    </span>
                  </div>
                  <p className="text-stone-700">{conf.message}</p>
                  <div className="text-[11px] text-stone-500 font-mono">
                    Strategy: <span className="text-stone-700">{conf.resolution_strategy}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Structured Ecological Findings List */}
        {response && (
          <div className="space-y-4">
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-stone-700 flex items-center gap-2">
              <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
              Structured Multi-Metric Ecological Findings ({response.findings.length})
            </h3>

            <div className="space-y-3">
              {response.findings.map((finding: EcologicalFinding) => {
                const isExpanded = !!expandedFindings[finding.finding_id];
                return (
                  <div
                    key={finding.finding_id}
                    className="border border-stone-200 rounded-lg bg-stone-50/50 hover:bg-stone-50 transition-colors overflow-hidden"
                  >
                    {/* Finding Header */}
                    <div
                      onClick={() => toggleExpand(finding.finding_id)}
                      className="p-4 cursor-pointer flex flex-col sm:flex-row sm:items-center justify-between gap-3"
                    >
                      <div className="space-y-1">
                        <div className="flex flex-wrap items-center gap-2">
                          <span
                            className={`px-2 py-0.5 text-[10px] font-mono font-bold uppercase rounded border ${getSeverityBadgeClass(
                              finding.severity
                            )}`}
                          >
                            {finding.severity}
                          </span>
                          <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-stone-200 text-stone-700">
                            {finding.domain}
                          </span>
                          <span className="text-xs font-semibold text-stone-900">{finding.title}</span>
                        </div>
                        <div className="flex flex-wrap items-center gap-1.5 text-[11px] text-stone-500">
                          <span>Contributing Metrics ({finding.contributing_variables.length}):</span>
                          {finding.variable_details.map((vd: VariableFindingDetail, vIdx: number) => (
                            <span
                              key={vIdx}
                              className="inline-flex items-center gap-1 bg-white px-2 py-0.5 rounded border border-stone-200 text-[11px] text-stone-700 font-mono"
                            >
                              <strong>{vd.name}:</strong> {vd.value !== null ? `${vd.value} ${vd.unit || ''}` : 'Unknown'}
                              {getSourceBadge(vd.source)}
                            </span>
                          ))}
                        </div>
                      </div>

                      <div className="flex items-center gap-3 shrink-0">
                        <div className="text-right">
                          <span className="text-xs font-bold text-stone-800">{Math.round(finding.confidence * 100)}%</span>
                          <span className="text-[10px] text-stone-500 block">Confidence</span>
                        </div>
                        {isExpanded ? (
                          <ChevronUp className="w-4 h-4 text-stone-500" />
                        ) : (
                          <ChevronDown className="w-4 h-4 text-stone-500" />
                        )}
                      </div>
                    </div>

                    {/* Expanded Detail Pane */}
                    {isExpanded && (
                      <div className="p-4 bg-white border-t border-stone-200 space-y-4">
                        {/* Biophysical Mechanism */}
                        <div>
                          <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-stone-700 mb-1">
                            Biophysical Mechanism & Ecological Driver
                          </h4>
                          <p className="text-xs text-stone-700 leading-relaxed bg-stone-50 p-3 rounded border border-stone-200">
                            {finding.ecological_mechanism}
                          </p>
                        </div>

                        {/* Step-by-Step Reasoning Chain */}
                        {finding.reasoning_chain && finding.reasoning_chain.links && (
                          <div>
                            <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-stone-700 mb-1">
                              Deterministic Causal Reasoning Chain
                            </h4>
                            <div className="space-y-1.5">
                              {finding.reasoning_chain.links.map((link, lIdx) => (
                                <div
                                  key={lIdx}
                                  className="flex items-start gap-2 text-xs bg-stone-50/70 p-2 rounded border border-stone-200 font-mono"
                                >
                                  <span className="w-5 h-5 flex items-center justify-center rounded-full bg-emerald-100 text-emerald-800 text-[10px] font-bold shrink-0">
                                    {link.step}
                                  </span>
                                  <div>
                                    <span className="text-stone-900 font-semibold">{link.from_concept}</span>
                                    <span className="text-emerald-700 mx-1.5">--[{link.relationship_type}]--&gt;</span>
                                    <span className="text-stone-900 font-semibold">{link.to_concept}</span>
                                    <p className="text-[11px] text-stone-600 font-sans mt-0.5">
                                      {link.ecological_mechanism}
                                    </p>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Scientific RAG Evidence Chunks */}
                        <div>
                          <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-stone-700 mb-1 flex items-center gap-1.5">
                            <BookOpen className="w-3.5 h-3.5 text-emerald-600" />
                            Grounded Scientific Evidence ({finding.evidence_references.length} peer-reviewed & institutional chunks)
                          </h4>
                          <div className="space-y-2">
                            {finding.evidence_references.map((ev, eIdx) => (
                              <div
                                key={eIdx}
                                className="bg-stone-50/80 p-3 rounded-lg border border-stone-200 text-xs space-y-1"
                              >
                                <div className="flex flex-wrap items-center justify-between gap-1">
                                  <span className="font-semibold text-stone-900">{ev.title}</span>
                                  <span className="font-mono text-[10px] text-stone-500 bg-stone-200 px-1.5 py-0.5 rounded">
                                    Relevance: {(ev.relevance_score * 100).toFixed(1)}% • Grade: {ev.confidence_grade}
                                  </span>
                                </div>
                                <div className="text-[11px] text-stone-600 font-mono">
                                  {ev.authors} ({ev.year}) • {ev.organization}
                                  {ev.doi && ` • DOI: ${ev.doi}`}
                                </div>
                                <p className="text-stone-700 leading-relaxed italic text-[11px] bg-white p-2 rounded border border-stone-200">
                                  "{ev.content}"
                                </p>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Uncertainty & Limitations */}
                        {finding.uncertainty_factors && finding.uncertainty_factors.length > 0 && (
                          <div className="text-xs text-stone-600 bg-stone-50 p-2.5 rounded border border-stone-200 space-y-1">
                            <span className="font-mono font-bold text-stone-700 block">
                              Uncertainty Factors & Regional Applicability:
                            </span>
                            <ul className="list-disc list-inside space-y-0.5 text-[11px] text-stone-600">
                              {finding.uncertainty_factors.map((uf, uIdx) => (
                                <li key={uIdx}>{uf}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
