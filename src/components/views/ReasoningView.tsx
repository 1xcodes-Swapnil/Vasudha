import React, { useState } from 'react';
import {
  Brain,
  Layers,
  ArrowDown,
  CheckCircle2,
  AlertTriangle,
  Info,
  Network,
  ShieldAlert,
  GitBranch,
  ChevronRight,
  Sparkles,
  BookOpen,
  TrendingUp,
  Compass,
} from 'lucide-react';
import { EnvironmentalState } from '../../types';
import { MultiMetricReasoningView } from '../MultiMetricReasoningView';
import { NatureRiskProfileView } from '../NatureRiskProfileView';
import { EcologicalFindingsPipelineView } from '../EcologicalFindingsPipelineView';

interface ReasoningViewProps {
  state: EnvironmentalState;
}

type ReasoningSubTab = 'causal_flow' | 'multi_metric' | 'risk_profile' | 'findings';

export const ReasoningView: React.FC<ReasoningViewProps> = ({ state }) => {
  const [activeSubTab, setActiveSubTab] = useState<ReasoningSubTab>('causal_flow');

  // Compute live signals from state
  const signals = [
    {
      name: 'Annual Rainfall',
      value: state.climate.rainfall !== null && state.climate.rainfall !== undefined ? `${state.climate.rainfall} mm/yr` : 'Unknown',
      trend: state.climate.rainfall !== null && state.climate.rainfall < 600 ? '↓ Deficit' : '→ Baseline',
      status: state.climate.rainfall !== null ? 'Observed' : 'Unknown',
      statusType: state.climate.rainfall !== null ? 'observed' : 'unknown',
      severity: state.climate.rainfall !== null && state.climate.rainfall < 600 ? 'high' : 'normal',
    },
    {
      name: 'Soil Moisture',
      value: state.soil.moisture !== null && state.soil.moisture !== undefined ? `${state.soil.moisture}% vol` : 'Unknown',
      trend: state.soil.moisture !== null && state.soil.moisture < 18 ? '↓ Low' : '→ Adequate',
      status: state.soil.moisture !== null ? 'Observed' : 'Unknown',
      statusType: state.soil.moisture !== null ? 'observed' : 'unknown',
      severity: state.soil.moisture !== null && state.soil.moisture < 18 ? 'high' : 'normal',
    },
    {
      name: 'Soil Organic Carbon',
      value: state.soil.organic_carbon !== null && state.soil.organic_carbon !== undefined ? `${state.soil.organic_carbon}% wt` : 'Unknown',
      trend: state.soil.organic_carbon !== null && state.soil.organic_carbon < 1.5 ? '↓ Depleted' : '→ Stable',
      status: state.soil.organic_carbon !== null ? 'Observed' : 'Unknown',
      statusType: state.soil.organic_carbon !== null ? 'observed' : 'unknown',
      severity: state.soil.organic_carbon !== null && state.soil.organic_carbon < 1.5 ? 'high' : 'normal',
    },
    {
      name: 'Mean Temperature',
      value: state.climate.temperature !== null && state.climate.temperature !== undefined ? `${state.climate.temperature} °C` : 'Unknown',
      trend: state.climate.temperature !== null && state.climate.temperature > 28 ? '↑ Elevated' : '→ Moderate',
      status: state.climate.temperature !== null ? 'Observed' : 'Unknown',
      statusType: state.climate.temperature !== null ? 'observed' : 'unknown',
      severity: state.climate.temperature !== null && state.climate.temperature > 28 ? 'medium' : 'normal',
    },
    {
      name: 'Habitat Diversity',
      value: state.biodiversity.habitat_diversity !== null && state.biodiversity.habitat_diversity !== undefined ? `${state.biodiversity.habitat_diversity}` : 'Unknown',
      trend: state.biodiversity.habitat_diversity !== null && state.biodiversity.habitat_diversity < 35 ? '↓ Fragmented' : '→ Heterogeneous',
      status: state.biodiversity.habitat_diversity !== null ? 'Observed' : 'Inferred',
      statusType: state.biodiversity.habitat_diversity !== null ? 'observed' : 'inferred',
      severity: state.biodiversity.habitat_diversity !== null && state.biodiversity.habitat_diversity < 35 ? 'high' : 'normal',
    },
    {
      name: 'Deforestation Pressure',
      value: state.human_impact.deforestation !== null && state.human_impact.deforestation !== undefined ? `${state.human_impact.deforestation}%` : 'Unknown',
      trend: state.human_impact.deforestation !== null && state.human_impact.deforestation > 10 ? '↑ High Loss' : '→ Low',
      status: state.human_impact.deforestation !== null ? 'Observed' : 'Unknown',
      statusType: state.human_impact.deforestation !== null ? 'observed' : 'unknown',
      severity: state.human_impact.deforestation !== null && state.human_impact.deforestation > 10 ? 'high' : 'normal',
    },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-12">
      {/* Top Switcher */}
      <div className="bg-white border border-stone-200 rounded-2xl p-3 sm:p-4 shadow-2xs flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-emerald-700" />
          <div>
            <h2 className="text-xs font-mono font-bold uppercase tracking-wider text-stone-900">
              Auditable Ecological Reasoning Pipeline
            </h2>
            <p className="text-[11px] text-stone-500">
              Explicit multi-variable causal flow from observed signals to biological mechanisms.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1.5 p-1 bg-stone-100 rounded-xl overflow-x-auto text-xs font-medium">
          <button
            onClick={() => setActiveSubTab('causal_flow')}
            className={`px-3 py-1.5 rounded-lg transition-colors whitespace-nowrap ${
              activeSubTab === 'causal_flow'
                ? 'bg-white text-stone-900 font-semibold shadow-2xs'
                : 'text-stone-600 hover:text-stone-900'
            }`}
          >
            Causal Flow & Signals
          </button>
          <button
            onClick={() => setActiveSubTab('multi_metric')}
            className={`px-3 py-1.5 rounded-lg transition-colors whitespace-nowrap ${
              activeSubTab === 'multi_metric'
                ? 'bg-white text-stone-900 font-semibold shadow-2xs'
                : 'text-stone-600 hover:text-stone-900'
            }`}
          >
            Multi-Metric Matrix
          </button>
          <button
            onClick={() => setActiveSubTab('risk_profile')}
            className={`px-3 py-1.5 rounded-lg transition-colors whitespace-nowrap ${
              activeSubTab === 'risk_profile'
                ? 'bg-white text-stone-900 font-semibold shadow-2xs'
                : 'text-stone-600 hover:text-stone-900'
            }`}
          >
            Nature Risk Profile
          </button>
          <button
            onClick={() => setActiveSubTab('findings')}
            className={`px-3 py-1.5 rounded-lg transition-colors whitespace-nowrap ${
              activeSubTab === 'findings'
                ? 'bg-white text-stone-900 font-semibold shadow-2xs'
                : 'text-stone-600 hover:text-stone-900'
            }`}
          >
            Findings Pipeline
          </button>
        </div>
      </div>

      {/* SUB-VIEW 1: CAUSAL FLOW & SIGNALS */}
      {activeSubTab === 'causal_flow' && (
        <div className="space-y-4">
          {/* STEP 1: OBSERVED SIGNALS */}
          <div className="bg-white border border-stone-200 rounded-2xl p-5 shadow-2xs">
            <div className="flex items-center justify-between mb-3 border-b border-stone-100 pb-2">
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center text-xs font-bold font-mono">
                  1
                </span>
                <h3 className="text-xs font-bold font-mono uppercase tracking-wider text-stone-900">
                  Observed Biophysical Signals
                </h3>
              </div>
              <span className="text-[11px] font-mono text-stone-500">Measured / Canonical Inputs</span>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {signals.map((sig, idx) => (
                <div
                  key={idx}
                  className={`p-3 rounded-xl border ${
                    sig.severity === 'high'
                      ? 'bg-amber-50/40 border-amber-200/80'
                      : 'bg-stone-50/60 border-stone-200/70'
                  }`}
                >
                  <div className="flex items-center justify-between text-[11px] font-mono mb-1">
                    <span className="font-semibold text-stone-800">{sig.name}</span>
                    <span
                      className={`px-1.5 py-0.2 rounded-xs text-[10px] uppercase font-bold ${
                        sig.statusType === 'observed'
                          ? 'bg-emerald-100 text-emerald-800'
                          : sig.statusType === 'inferred'
                          ? 'bg-blue-100 text-blue-800'
                          : 'bg-stone-200 text-stone-600'
                      }`}
                    >
                      {sig.status}
                    </span>
                  </div>
                  <div className="flex items-baseline justify-between mt-1">
                    <span className="text-xs font-bold text-stone-900 font-mono">{sig.value}</span>
                    <span
                      className={`text-[11px] font-mono font-medium ${
                        sig.severity === 'high' ? 'text-amber-700' : 'text-stone-500'
                      }`}
                    >
                      {sig.trend}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* STEP CONNECTOR */}
          <div className="flex justify-center -my-1">
            <div className="w-8 h-8 rounded-full bg-stone-100 border border-stone-300 flex items-center justify-center text-stone-600 shadow-2xs">
              <ArrowDown className="w-4 h-4" />
            </div>
          </div>

          {/* STEP 2: ECOLOGICAL PRESSURES */}
          <div className="bg-white border border-amber-200 rounded-2xl p-5 shadow-2xs bg-amber-50/20">
            <div className="flex items-center justify-between mb-3 border-b border-amber-200/60 pb-2">
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-amber-100 text-amber-800 flex items-center justify-center text-xs font-bold font-mono">
                  2
                </span>
                <h3 className="text-xs font-bold font-mono uppercase tracking-wider text-amber-900">
                  Synthesized Ecological Pressures
                </h3>
              </div>
              <span className="text-[11px] font-mono text-amber-800 font-semibold bg-amber-100 px-2 py-0.5 rounded-full">
                Multi-Variable Trigger
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              <div className="p-3 bg-white rounded-xl border border-amber-200 shadow-2xs space-y-1">
                <div className="flex items-center justify-between text-[11px] font-mono">
                  <span className="font-bold text-rose-800">Water Deficit Stress</span>
                  <span className="text-rose-700 font-bold">Critical</span>
                </div>
                <p className="text-[11px] text-stone-600">
                  Driven by Rainfall deficit (&lt;600mm) + Soil moisture exhaustion (&lt;18%).
                </p>
              </div>

              <div className="p-3 bg-white rounded-xl border border-amber-200 shadow-2xs space-y-1">
                <div className="flex items-center justify-between text-[11px] font-mono">
                  <span className="font-bold text-amber-800">Soil Degradation Strain</span>
                  <span className="text-amber-700 font-bold">High</span>
                </div>
                <p className="text-[11px] text-stone-600">
                  Driven by Depleted organic carbon (&lt;1.5%) + intensive agricultural exposure.
                </p>
              </div>

              <div className="p-3 bg-white rounded-xl border border-amber-200 shadow-2xs space-y-1">
                <div className="flex items-center justify-between text-[11px] font-mono">
                  <span className="font-bold text-amber-800">Habitat Fragmentation</span>
                  <span className="text-amber-700 font-bold">High</span>
                </div>
                <p className="text-[11px] text-stone-600">
                  Driven by Low structural diversity (&lt;35) + canopy disruption (&gt;10% loss).
                </p>
              </div>
            </div>
          </div>

          {/* STEP CONNECTOR */}
          <div className="flex justify-center -my-1">
            <div className="w-8 h-8 rounded-full bg-stone-100 border border-stone-300 flex items-center justify-center text-stone-600 shadow-2xs">
              <ArrowDown className="w-4 h-4" />
            </div>
          </div>

          {/* STEP 3: MECHANISM */}
          <div className="bg-white border border-stone-200 rounded-2xl p-5 shadow-2xs">
            <div className="flex items-center justify-between mb-3 border-b border-stone-100 pb-2">
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-blue-100 text-blue-800 flex items-center justify-center text-xs font-bold font-mono">
                  3
                </span>
                <h3 className="text-xs font-bold font-mono uppercase tracking-wider text-stone-900">
                  Biological & Ecological Mechanisms
                </h3>
              </div>
              <span className="text-[11px] font-mono text-blue-700 font-semibold">
                Physiological Causality
              </span>
            </div>

            <div className="p-4 rounded-xl bg-blue-50/40 border border-blue-200/80 text-xs text-blue-950 space-y-2">
              <p className="leading-relaxed">
                <strong>Hydrological-Biophysical Coupling:</strong> Low soil moisture combined with prolonged thermal exposure restricts stomatal conductance in vegetation, triggering xylem cavitation and leaf shedding.
              </p>
              <p className="leading-relaxed">
                <strong>Rhizosphere & Microbial Feedback:</strong> Depleted organic carbon inhibits mycorrhizal hyphal networks and soil aggregate stability, drastically reducing infiltration rates during intense precipitation pulses and exacerbating surface erosion.
              </p>
            </div>
          </div>

          {/* STEP CONNECTOR */}
          <div className="flex justify-center -my-1">
            <div className="w-8 h-8 rounded-full bg-stone-100 border border-stone-300 flex items-center justify-center text-stone-600 shadow-2xs">
              <ArrowDown className="w-4 h-4" />
            </div>
          </div>

          {/* STEP 4: BIODIVERSITY IMPLICATIONS */}
          <div className="bg-white border border-stone-200 rounded-2xl p-5 shadow-2xs">
            <div className="flex items-center justify-between mb-3 border-b border-stone-100 pb-2">
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-teal-100 text-teal-800 flex items-center justify-center text-xs font-bold font-mono">
                  4
                </span>
                <h3 className="text-xs font-bold font-mono uppercase tracking-wider text-stone-900">
                  Biodiversity & Ecosystem Implications
                </h3>
              </div>
              <span className="text-[11px] font-mono text-teal-800 font-semibold">
                Species & Niche Persistence
              </span>
            </div>

            <div className="p-4 rounded-xl bg-teal-50/40 border border-teal-200/80 text-xs text-teal-950 space-y-2">
              <p className="leading-relaxed">
                <strong>Niche Contraction:</strong> Structural simplification limits vertical avian nesting strata, subterranean macroinvertebrate refuge, and pollinator floral resource availability across dry seasons.
              </p>
              <p className="leading-relaxed">
                <strong>Tipping Point Risk:</strong> Without targeted intervention (such as multi-strata agroforestry and contour swales), prolonged deficit risks irreversible shift toward xerophytic shrubland with permanent loss of native biodiversity richness.
              </p>
            </div>
          </div>

          {/* STEP CONNECTOR */}
          <div className="flex justify-center -my-1">
            <div className="w-8 h-8 rounded-full bg-stone-100 border border-stone-300 flex items-center justify-center text-stone-600 shadow-2xs">
              <ArrowDown className="w-4 h-4" />
            </div>
          </div>

          {/* STEP 5: POTENTIAL ACTION / INTERVENTION */}
          <div className="bg-white border border-emerald-200 rounded-2xl p-5 shadow-2xs bg-emerald-50/20">
            <div className="flex items-center justify-between mb-3 border-b border-emerald-200/60 pb-2">
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center text-xs font-bold font-mono">
                  5
                </span>
                <h3 className="text-xs font-bold font-mono uppercase tracking-wider text-emerald-900">
                  Prescribed Ecological Interventions
                </h3>
              </div>
              <span className="text-[11px] font-mono text-emerald-800 font-semibold bg-emerald-100 px-2 py-0.5 rounded-full flex items-center gap-1">
                <Compass className="w-3 h-3" />
                Context-Appropriate
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-xs">
              <div className="p-3 bg-white rounded-xl border border-emerald-200 shadow-2xs space-y-1">
                <div className="font-bold text-emerald-900 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                  Multistrata Agroforestry
                </div>
                <p className="text-[11px] text-stone-600 leading-relaxed">
                  Integrate native deep-rooting leguminous trees along field contours to restore soil organic carbon, provide microclimate shade, and re-establish hydraulic lift.
                </p>
              </div>

              <div className="p-3 bg-white rounded-xl border border-emerald-200 shadow-2xs space-y-1">
                <div className="font-bold text-emerald-900 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                  Cover Cropping & Residue Mulch
                </div>
                <p className="text-[11px] text-stone-600 leading-relaxed">
                  Seed mixed native cover crops during dry fallow and eliminate tillage to protect topsoil from thermal baking and enhance macro-aggregate stability.
                </p>
              </div>

              <div className="p-3 bg-white rounded-xl border border-emerald-200 shadow-2xs space-y-1">
                <div className="font-bold text-emerald-900 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-500"></span>
                  Riparian Buffer Corridors
                </div>
                <p className="text-[11px] text-stone-600 leading-relaxed">
                  Plant 20–30m native vegetative buffer strips along seasonal streams and field edges to filter runoff and connect fragmented habitat patches.
                </p>
              </div>
            </div>
          </div>

          {/* STEP CONNECTOR */}
          <div className="flex justify-center -my-1">
            <div className="w-8 h-8 rounded-full bg-stone-100 border border-stone-300 flex items-center justify-center text-stone-600 shadow-2xs">
              <ArrowDown className="w-4 h-4" />
            </div>
          </div>

          {/* STEP 6: EXPECTED METRIC DIRECTION */}
          <div className="bg-white border border-stone-200 rounded-2xl p-5 shadow-2xs">
            <div className="flex items-center justify-between mb-3 border-b border-stone-100 pb-2">
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-indigo-100 text-indigo-800 flex items-center justify-center text-xs font-bold font-mono">
                  6
                </span>
                <h3 className="text-xs font-bold font-mono uppercase tracking-wider text-stone-900">
                  Expected Biophysical Metric Direction
                </h3>
              </div>
              <span className="text-[11px] font-mono text-indigo-700 font-semibold flex items-center gap-1">
                <TrendingUp className="w-3 h-3" />
                Directional Trajectory
              </span>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-stone-50 border border-stone-200 text-center">
                <div className="text-emerald-700 font-mono font-bold text-sm">↑ Positive</div>
                <div className="font-bold text-stone-800 mt-0.5 text-xs">Soil Organic Carbon</div>
                <div className="text-[10px] text-stone-500 mt-1">Humus stabilization</div>
              </div>
              <div className="p-3 rounded-xl bg-stone-50 border border-stone-200 text-center">
                <div className="text-emerald-700 font-mono font-bold text-sm">↑ Increased</div>
                <div className="font-bold text-stone-800 mt-0.5 text-xs">Infiltration Rate</div>
                <div className="text-[10px] text-stone-500 mt-1">Macro-porosity restored</div>
              </div>
              <div className="p-3 rounded-xl bg-stone-50 border border-stone-200 text-center">
                <div className="text-emerald-700 font-mono font-bold text-sm">↑ Expanded</div>
                <div className="font-bold text-stone-800 mt-0.5 text-xs">Habitat Diversity</div>
                <div className="text-[10px] text-stone-500 mt-1">Structural niches added</div>
              </div>
              <div className="p-3 rounded-xl bg-stone-50 border border-stone-200 text-center">
                <div className="text-emerald-700 font-mono font-bold text-sm">↓ Reduced</div>
                <div className="font-bold text-stone-800 mt-0.5 text-xs">Thermal Peak Stress</div>
                <div className="text-[10px] text-stone-500 mt-1">Canopy microclimate buffer</div>
              </div>
            </div>
          </div>

          {/* STEP CONNECTOR */}
          <div className="flex justify-center -my-1">
            <div className="w-8 h-8 rounded-full bg-stone-100 border border-stone-300 flex items-center justify-center text-stone-600 shadow-2xs">
              <ArrowDown className="w-4 h-4" />
            </div>
          </div>

          {/* STEP 7: GROUNDED SCIENTIFIC EVIDENCE */}
          <div className="bg-white border border-stone-200 rounded-2xl p-5 shadow-2xs bg-stone-50/50">
            <div className="flex items-center justify-between mb-3 border-b border-stone-200/80 pb-2">
              <div className="flex items-center gap-2">
                <span className="w-5 h-5 rounded-full bg-amber-100 text-amber-900 flex items-center justify-center text-xs font-bold font-mono">
                  7
                </span>
                <h3 className="text-xs font-bold font-mono uppercase tracking-wider text-stone-900">
                  Grounded Scientific Evidence & Literature Consensus
                </h3>
              </div>
              <span className="text-[11px] font-mono text-stone-600 font-semibold flex items-center gap-1">
                <BookOpen className="w-3 h-3" />
                Tier 1 Consensus
              </span>
            </div>

            <div className="space-y-2 text-xs">
              <div className="p-3 rounded-xl bg-white border border-stone-200 flex items-start gap-2.5">
                <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-stone-100 text-stone-800 shrink-0">IPCC AR6 WGII</span>
                <p className="text-stone-700 leading-relaxed text-[11px]">
                  <strong>Chapter 2 (Terrestrial Ecosystems):</strong> Agroforestry practices and vegetative soil cover sequester carbon, reduce erosion rates, and enhance infiltration in semi-arid drylands, buffering vegetation against rainfall anomalies (Pörtner et al., 2022).
                </p>
              </div>

              <div className="p-3 rounded-xl bg-white border border-stone-200 flex items-start gap-2.5">
                <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-stone-100 text-stone-800 shrink-0">IPBES Global</span>
                <p className="text-stone-700 leading-relaxed text-[11px]">
                  <strong>Global Assessment:</strong> Restoring landscape mosaic connectivity through perennial native buffers and diversified field borders reverses pollinator declines and supports multi-trophic biodiversity resilience (Díaz et al., 2019).
                </p>
              </div>

              <div className="p-3 rounded-xl bg-white border border-stone-200 flex items-start gap-2.5">
                <span className="px-1.5 py-0.5 rounded text-[10px] font-mono font-bold bg-stone-100 text-stone-800 shrink-0">FAO Healthy Soils</span>
                <p className="text-stone-700 leading-relaxed text-[11px]">
                  <strong>Recarbonizing Global Soils (GSOCseq):</strong> Increasing soil organic carbon by vegetative residue retention directly enhances moisture infiltration by 30–50% in degraded arable lands (FAO ITPS, 2022).
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* SUB-VIEW 2: MULTI-METRIC MATRIX */}
      {activeSubTab === 'multi_metric' && (
        <MultiMetricReasoningView state={state} />
      )}

      {/* SUB-VIEW 3: NATURE RISK PROFILE */}
      {activeSubTab === 'risk_profile' && (
        <NatureRiskProfileView currentState={state} />
      )}

      {/* SUB-VIEW 4: FINDINGS PIPELINE */}
      {activeSubTab === 'findings' && (
        <EcologicalFindingsPipelineView state={state} />
      )}
    </div>
  );
};
