import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  HelpCircle,
  BookOpen,
  ArrowRight,
  ExternalLink,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Info,
  Layers,
  Activity,
  CheckCircle2,
  FileText,
  Compass,
} from 'lucide-react';
import {
  EnvironmentalState,
  NatureRiskProfile,
  RiskDimension,
  RiskLevel,
  RiskDimensionMetadata,
  EvidenceChunkPacket,
} from '../types';
import { fetchNatureRiskProfile, fetchRiskDimensions } from '../services/api';

interface NatureRiskProfileViewProps {
  currentState: EnvironmentalState;
  onRefresh?: () => void;
}

export const NatureRiskProfileView: React.FC<NatureRiskProfileViewProps> = ({
  currentState,
  onRefresh,
}) => {
  const [profile, setProfile] = useState<NatureRiskProfile | null>(null);
  const [dimensionsMeta, setDimensionsMeta] = useState<RiskDimensionMetadata[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedDimensionId, setSelectedDimensionId] = useState<string>('water_stress');
  const [expandedChunkId, setExpandedChunkId] = useState<string | null>(null);
  const [showAllEvidence, setShowAllEvidence] = useState<boolean>(false);

  const loadProfile = async () => {
    setLoading(true);
    setError(null);
    try {
      const [profileData, metaData] = await Promise.all([
        fetchNatureRiskProfile(currentState),
        fetchRiskDimensions(),
      ]);
      setProfile(profileData);
      setDimensionsMeta(metaData);
    } catch (err: any) {
      console.error('Error fetching Nature Risk Profile:', err);
      setError(err.message || 'Failed to diagnose Nature Risk Profile');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProfile();
  }, [currentState]);

  const getRiskBadge = (level: RiskLevel) => {
    switch (level) {
      case 'high':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-rose-50 text-rose-700 border border-rose-200">
            <ShieldAlert className="w-3.5 h-3.5 text-rose-600" />
            High Risk
          </span>
        );
      case 'medium':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-50 text-amber-700 border border-amber-200">
            <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
            Medium Risk
          </span>
        );
      case 'low':
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
            Low Risk
          </span>
        );
      case 'unknown':
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-600 border border-slate-200">
            <HelpCircle className="w-3.5 h-3.5 text-slate-500" />
            Unknown (Missing Data)
          </span>
        );
    }
  };

  const getDimensionIcon = (id: string) => {
    switch (id) {
      case 'water_stress':
        return <Activity className="w-4 h-4 text-blue-600" />;
      case 'habitat_pressure':
        return <Layers className="w-4 h-4 text-emerald-600" />;
      case 'biodiversity_pressure':
        return <Compass className="w-4 h-4 text-purple-600" />;
      case 'climate_exposure':
        return <AlertTriangle className="w-4 h-4 text-amber-600" />;
      case 'human_disturbance':
        return <ShieldAlert className="w-4 h-4 text-rose-600" />;
      default:
        return <FileText className="w-4 h-4 text-slate-600" />;
    }
  };

  const getDimensionById = (id: string): RiskDimension | undefined => {
    if (!profile) return undefined;
    switch (id) {
      case 'water_stress':
        return profile.water_stress;
      case 'habitat_pressure':
        return profile.habitat_pressure;
      case 'biodiversity_pressure':
        return profile.biodiversity_pressure;
      case 'climate_exposure':
        return profile.climate_exposure;
      case 'human_disturbance':
        return profile.human_disturbance;
      default:
        return undefined;
    }
  };

  const selectedDimension = getDimensionById(selectedDimensionId);

  const dimensionList = [
    { id: 'water_stress', name: 'Water Stress', obj: profile?.water_stress },
    { id: 'habitat_pressure', name: 'Habitat Pressure', obj: profile?.habitat_pressure },
    { id: 'biodiversity_pressure', name: 'Biodiversity Pressure', obj: profile?.biodiversity_pressure },
    { id: 'climate_exposure', name: 'Climate Exposure', obj: profile?.climate_exposure },
    { id: 'human_disturbance', name: 'Human Disturbance', obj: profile?.human_disturbance },
  ];

  return (
    <div className="space-y-6">
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-white p-5 rounded-xl border border-slate-200 shadow-xs">
        <div>
          <div className="flex items-center gap-2">
            <span className="px-2 py-0.5 rounded text-[11px] font-bold tracking-wider uppercase bg-emerald-100 text-emerald-800">
              Phase 6 Diagnostic Layer
            </span>
            <span className="text-xs text-slate-500">Deterministic • Zero Arbitrary Scores</span>
          </div>
          <h2 className="text-xl font-bold text-slate-900 mt-1">
            Nature Risk Profile (Diagnosis Layer)
          </h2>
          <p className="text-sm text-slate-600 mt-0.5">
            Evidence-aware ecological vulnerability diagnosis across 5 core environmental dimensions.
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowAllEvidence(!showAllEvidence)}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg border border-slate-200 bg-white text-slate-700 hover:bg-slate-50 transition-colors"
          >
            <BookOpen className="w-3.5 h-3.5 text-emerald-600" />
            {showAllEvidence ? 'Hide Evidence Matrix' : `Evidence Matrix (${profile?.evidence_summary.length || 0})`}
          </button>
          <button
            onClick={loadProfile}
            disabled={loading}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium rounded-lg bg-emerald-600 text-white hover:bg-emerald-700 disabled:opacity-50 transition-colors shadow-xs"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} />
            Re-diagnose
          </button>
        </div>
      </div>

      {loading && (
        <div className="flex flex-col items-center justify-center p-12 bg-white rounded-xl border border-slate-200">
          <RefreshCw className="w-8 h-8 text-emerald-600 animate-spin mb-3" />
          <p className="text-sm font-medium text-slate-800">Evaluating 5-Dimension Nature Risk Profile...</p>
          <p className="text-xs text-slate-500 mt-1">Cross-referencing multi-metric pressures with scientific corpus</p>
        </div>
      )}

      {error && (
        <div className="p-4 bg-rose-50 border border-rose-200 rounded-xl text-sm text-rose-800 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-rose-600 shrink-0 mt-0.5" />
          <div>
            <p className="font-semibold">Diagnostic Evaluation Error</p>
            <p className="text-xs text-rose-700 mt-0.5">{error}</p>
          </div>
        </div>
      )}

      {profile && !loading && (
        <>
          {/* Dimension Cards Summary Grid */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-3">
            {dimensionList.map((dim) => {
              const isSelected = selectedDimensionId === dim.id;
              const level = dim.obj?.level || 'unknown';
              return (
                <button
                  key={dim.id}
                  onClick={() => setSelectedDimensionId(dim.id)}
                  className={`flex flex-col text-left p-4 rounded-xl border transition-all ${
                    isSelected
                      ? 'bg-slate-900 text-white border-slate-900 shadow-md ring-2 ring-emerald-500/20'
                      : 'bg-white text-slate-800 border-slate-200 hover:border-slate-300 hover:bg-slate-50/50 shadow-xs'
                  }`}
                >
                  <div className="flex items-center justify-between w-full mb-2">
                    <div className="p-1.5 rounded-lg bg-slate-100 dark:bg-slate-800">
                      {getDimensionIcon(dim.id)}
                    </div>
                    {getRiskBadge(level)}
                  </div>
                  <h3 className={`font-semibold text-sm ${isSelected ? 'text-white' : 'text-slate-900'}`}>
                    {dim.name}
                  </h3>
                  <p className={`text-xs mt-1 line-clamp-2 ${isSelected ? 'text-slate-300' : 'text-slate-500'}`}>
                    {dim.obj?.inferred_drivers?.[0] || 'Awaiting metric evaluation'}
                  </p>
                  <div className="mt-3 pt-2 border-t border-slate-100/10 flex items-center justify-between text-[11px]">
                    <span className={isSelected ? 'text-emerald-400' : 'text-slate-500'}>
                      {dim.obj?.evidence_chunks.length || 0} studies cited
                    </span>
                    <ArrowRight className={`w-3 h-3 ${isSelected ? 'text-emerald-400' : 'text-slate-400'}`} />
                  </div>
                </button>
              );
            })}
          </div>

          {/* Selected Dimension Detail View */}
          {selectedDimension && (
            <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
              <div className="p-6 border-b border-slate-100 flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-slate-50/50">
                <div className="flex items-center gap-3">
                  <div className="p-2.5 rounded-xl bg-white border border-slate-200 shadow-xs">
                    {getDimensionIcon(selectedDimension.dimension_id)}
                  </div>
                  <div>
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-bold text-slate-900">{selectedDimension.name}</h3>
                      {getRiskBadge(selectedDimension.level)}
                    </div>
                    <p className="text-xs text-slate-500 mt-0.5">
                      Evaluated metrics: {selectedDimension.contributing_metrics.join(', ') || 'None provided'}
                    </p>
                  </div>
                </div>

                <div className="flex items-center gap-3 text-xs">
                  <div className="px-3 py-1.5 rounded-lg bg-white border border-slate-200">
                    <span className="text-slate-500">Evidence Tier: </span>
                    <span className="font-semibold text-slate-800 capitalize">
                      {selectedDimension.evidence_strength.replace('_', ' ')}
                    </span>
                  </div>
                  <div className="px-3 py-1.5 rounded-lg bg-white border border-slate-200">
                    <span className="text-slate-500">Scope: </span>
                    <span className="font-semibold text-slate-800 capitalize">
                      {selectedDimension.geographic_applicability.replace('_', ' ')}
                    </span>
                  </div>
                </div>
              </div>

              <div className="p-6 space-y-6">
                {/* 1. Inferred Drivers & Observed Conditions */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2.5 flex items-center gap-1.5">
                      <Activity className="w-3.5 h-3.5 text-slate-500" />
                      Observed Baseline Conditions
                    </h4>
                    {Object.keys(selectedDimension.observed_conditions).length > 0 ? (
                      <div className="space-y-1.5">
                        {Object.entries(selectedDimension.observed_conditions).map(([key, val]) => (
                          <div key={key} className="flex justify-between items-center text-xs py-1 px-2 rounded bg-white border border-slate-100">
                            <span className="font-mono text-slate-600">{key}</span>
                            <span className="font-semibold text-slate-900">{String(val)}</span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-xs text-slate-500 italic">No direct measurements recorded for this domain.</p>
                    )}
                  </div>

                  <div className="p-4 rounded-xl bg-slate-50 border border-slate-200/80">
                    <h4 className="text-xs font-bold uppercase tracking-wider text-slate-700 mb-2.5 flex items-center gap-1.5">
                      <ShieldAlert className="w-3.5 h-3.5 text-amber-600" />
                      Inferred Ecological Drivers
                    </h4>
                    {selectedDimension.inferred_drivers.length > 0 ? (
                      <ul className="space-y-1.5 text-xs text-slate-700">
                        {selectedDimension.inferred_drivers.map((driver, idx) => (
                          <li key={idx} className="flex items-start gap-2">
                            <span className="w-1.5 h-1.5 rounded-full bg-amber-500 mt-1.5 shrink-0" />
                            <span>{driver}</span>
                          </li>
                        ))}
                      </ul>
                    ) : (
                      <p className="text-xs text-slate-500 italic">No significant drivers inferred.</p>
                    )}
                  </div>
                </div>

                {/* 2. Formal 5-Stage Explainability Chain */}
                {selectedDimension.explainability_chain && (
                  <div className="border border-slate-200 rounded-xl p-5 bg-white">
                    <h4 className="text-sm font-bold text-slate-900 mb-1 flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-emerald-500" />
                      5-Stage Explainability Chain (Observed → Drivers → Mechanism → Pressure → Evidence)
                    </h4>
                    <p className="text-xs text-slate-500 mb-4">
                      Deterministic mechanistic pathway translating baseline observation into diagnosed nature pressure.
                    </p>

                    <div className="grid grid-cols-1 md:grid-cols-5 gap-3 relative">
                      {selectedDimension.explainability_chain.steps.map((step, idx) => (
                        <div
                          key={idx}
                          className="p-3.5 rounded-lg border border-slate-200 bg-slate-50/50 flex flex-col justify-between"
                        >
                          <div>
                            <div className="flex items-center justify-between mb-1.5">
                              <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-700 bg-emerald-50 px-1.5 py-0.5 rounded border border-emerald-200">
                                Step {idx + 1}
                              </span>
                              <span className="text-[10px] text-slate-400 capitalize">
                                {step.stage.replace('_', ' ')}
                              </span>
                            </div>
                            <p className="text-xs text-slate-800 leading-relaxed">
                              {step.description}
                            </p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* 3. Scientific Grounding & Evidence Packets */}
                <div>
                  <h4 className="text-sm font-bold text-slate-900 mb-3 flex items-center gap-2">
                    <BookOpen className="w-4 h-4 text-emerald-600" />
                    Cited Peer-Reviewed Evidence & Meta-Analyses ({selectedDimension.evidence_chunks.length})
                  </h4>

                  {selectedDimension.evidence_chunks.length > 0 ? (
                    <div className="space-y-3">
                      {selectedDimension.evidence_chunks.map((chunk, cIdx) => {
                        const isExpanded = expandedChunkId === chunk.chunk_id;
                        return (
                          <div
                            key={`${chunk.chunk_id}-${cIdx}`}
                            className="border border-slate-200 rounded-xl p-4 bg-white hover:border-slate-300 transition-all shadow-xs"
                          >
                            <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-2 mb-2">
                              <div>
                                <span className="text-xs font-bold text-slate-900">{chunk.title}</span>
                                <span className="text-xs text-slate-500 ml-2">({chunk.year})</span>
                              </div>
                              <div className="flex items-center gap-1.5">
                                <span className="px-2 py-0.5 rounded text-[10px] font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 uppercase">
                                  {chunk.organization}
                                </span>
                                <span className="px-2 py-0.5 rounded text-[10px] font-medium bg-slate-100 text-slate-600">
                                  {chunk.evidence_strength}
                                </span>
                              </div>
                            </div>

                            <p className="text-xs text-slate-700 bg-slate-50 p-3 rounded-lg border border-slate-100 leading-relaxed font-serif">
                              "{isExpanded ? chunk.content : `${chunk.content.substring(0, 180)}...`}"
                            </p>

                            <div className="flex justify-between items-center mt-3 pt-2 border-t border-slate-100 text-xs">
                              <span className="text-[11px] text-slate-500">
                                Citation: <span className="italic">{chunk.citation}</span>
                              </span>
                              <div className="flex items-center gap-3">
                                {chunk.doi && (
                                  <a
                                    href={`https://doi.org/${chunk.doi}`}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="inline-flex items-center gap-1 text-[11px] text-emerald-700 hover:text-emerald-800 underline"
                                  >
                                    DOI <ExternalLink className="w-3 h-3" />
                                  </a>
                                )}
                                <button
                                  onClick={() => setExpandedChunkId(isExpanded ? null : chunk.chunk_id)}
                                  className="inline-flex items-center gap-1 text-slate-600 hover:text-slate-900 font-medium"
                                >
                                  {isExpanded ? (
                                    <>
                                      Less <ChevronUp className="w-3.5 h-3.5" />
                                    </>
                                  ) : (
                                    <>
                                      Full Passage <ChevronDown className="w-3.5 h-3.5" />
                                    </>
                                  )}
                                </button>
                              </div>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  ) : (
                    <div className="p-4 rounded-xl bg-slate-50 border border-slate-200 text-xs text-slate-600">
                      No specific evidence chunks attached for this dimension under current baseline.
                    </div>
                  )}
                </div>

                {/* 4. Uncertainty & Limitations */}
                <div className="p-4 rounded-xl bg-amber-50/50 border border-amber-200/80 space-y-2">
                  <div className="flex items-center gap-2 text-xs font-bold text-amber-900">
                    <Info className="w-4 h-4 text-amber-700" />
                    Uncertainty Bounds & Ecological Constraints
                  </div>
                  <p className="text-xs text-amber-900/90 leading-relaxed">
                    {selectedDimension.uncertainty}
                  </p>
                  {selectedDimension.limitations.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-amber-200/50">
                      <span className="text-[11px] font-bold text-amber-800 uppercase tracking-wider">
                        Domain Limitations:
                      </span>
                      <ul className="list-disc list-inside text-xs text-amber-900/80 mt-1 space-y-0.5">
                        {selectedDimension.limitations.map((lim, idx) => (
                          <li key={idx}>{lim}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Missing Ecological Variables Warning */}
          {profile.missing_important_variables.length > 0 && (
            <div className="p-5 rounded-xl bg-slate-900 text-white shadow-xs">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <HelpCircle className="w-4 h-4 text-amber-400" />
                  <h4 className="text-sm font-bold">
                    Missing Important Variables ({profile.missing_important_variables.length})
                  </h4>
                </div>
                <span className="text-xs text-slate-400">Preserved as Unknown</span>
              </div>
              <p className="text-xs text-slate-300 mb-3">
                The Nature Risk Profile distinguishes unknown from zero. The following variables were not provided and therefore were not assumed to be low:
              </p>
              <div className="flex flex-wrap gap-2">
                {profile.missing_important_variables.map((v, idx) => (
                  <span
                    key={idx}
                    className="px-2.5 py-1 rounded-md text-xs font-medium bg-slate-800 text-amber-300 border border-slate-700"
                  >
                    {v}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* System Limitations */}
          <div className="p-4 rounded-xl bg-white border border-slate-200 text-xs text-slate-600 space-y-1.5">
            <h4 className="font-bold text-slate-900 flex items-center gap-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
              Scientific Diagnostic Integrity Rules
            </h4>
            <ul className="list-disc list-inside space-y-1 text-slate-600">
              {profile.overall_limitations.map((lim, idx) => (
                <li key={idx}>{lim}</li>
              ))}
            </ul>
          </div>
        </>
      )}
    </div>
  );
};
