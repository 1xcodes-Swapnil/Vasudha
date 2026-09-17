import React from 'react';
import { MapPin, Sprout, Activity, Compass, Info, Lock } from 'lucide-react';

export const PlaceholderWorkspace: React.FC = () => {
  return (
    <div className="bg-white border border-stone-200 rounded-sm p-6 shadow-xs">
      <div className="flex items-center justify-between pb-3 border-b border-stone-100 mb-5">
        <div>
          <h2 className="text-sm font-semibold uppercase tracking-wider text-stone-700">
            Biodiversity Intelligence Workspace (Phase 1+ Foundation)
          </h2>
          <p className="text-xs text-stone-500 mt-0.5">
            Module scaffolding for ecological state tracking, geographic context, and scientific reasoning.
          </p>
        </div>
        <div className="flex items-center gap-1 text-xs text-stone-500 font-mono">
          <Lock className="w-3.5 h-3.5" />
          <span>Locked until Phase 1</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Environmental State Scaffold */}
        <div className="border border-dashed border-stone-300 rounded-sm p-4 bg-stone-50/50">
          <div className="flex items-center gap-2 mb-3">
            <Sprout className="w-4 h-4 text-stone-600" />
            <h3 className="text-xs font-semibold uppercase tracking-wider text-stone-800">
              1. Environmental State Input
            </h3>
          </div>
          <p className="text-xs text-stone-500 mb-4 leading-relaxed">
            Will ingest and normalize multi-dimensional ecological variables across turns:
          </p>
          <ul className="text-xs space-y-2 text-stone-600 font-mono">
            <li className="flex items-center justify-between py-1 px-2 bg-white border border-stone-200 rounded-xs">
              <span>Soil</span>
              <span className="text-stone-400">pH, Organic Carbon, Moisture</span>
            </li>
            <li className="flex items-center justify-between py-1 px-2 bg-white border border-stone-200 rounded-xs">
              <span>Land</span>
              <span className="text-stone-400">Land Cover, Degradation Level</span>
            </li>
            <li className="flex items-center justify-between py-1 px-2 bg-white border border-stone-200 rounded-xs">
              <span>Climate</span>
              <span className="text-stone-400">Rainfall, Temperature Regimes</span>
            </li>
            <li className="flex items-center justify-between py-1 px-2 bg-white border border-stone-200 rounded-xs">
              <span>Biodiversity</span>
              <span className="text-stone-400">Richness, Habitat Diversity</span>
            </li>
            <li className="flex items-center justify-between py-1 px-2 bg-white border border-stone-200 rounded-xs">
              <span>Human Impact</span>
              <span className="text-stone-400">Deforestation, Pollution</span>
            </li>
          </ul>
        </div>

        {/* Geographic Context & Map Scaffold */}
        <div className="border border-dashed border-stone-300 rounded-sm p-4 bg-stone-50/50">
          <div className="flex items-center gap-2 mb-3">
            <MapPin className="w-4 h-4 text-stone-600" />
            <h3 className="text-xs font-semibold uppercase tracking-wider text-stone-800">
              2. Geographic & Biome Context
            </h3>
          </div>
          <p className="text-xs text-stone-500 mb-4 leading-relaxed">
            Interactive map coordinate resolution and ecoregion boundary grounding:
          </p>
          <div className="h-44 flex flex-col items-center justify-center bg-white border border-stone-200 rounded-xs text-stone-400 p-4 text-center">
            <Compass className="w-8 h-8 mb-2 stroke-1 text-stone-400" />
            <span className="text-xs font-medium text-stone-600">Interactive Map View Placeholder</span>
            <span className="text-[11px] text-stone-400 mt-1">Spatial bounding box, ecoregion baselines & native species indicators</span>
          </div>
        </div>

        {/* Scientific Intelligence & Reasoning Chain Scaffold */}
        <div className="border border-dashed border-stone-300 rounded-sm p-4 bg-stone-50/50">
          <div className="flex items-center gap-2 mb-3">
            <Activity className="w-4 h-4 text-stone-600" />
            <h3 className="text-xs font-semibold uppercase tracking-wider text-stone-800">
              3. Reasoning & Explainability Chain
            </h3>
          </div>
          <p className="text-xs text-stone-500 mb-4 leading-relaxed">
            Transparent chain explaining mechanism, interventions, evidence citations, and trade-offs:
          </p>
          <div className="space-y-2 text-xs">
            <div className="p-2.5 bg-white border border-stone-200 rounded-xs">
              <span className="font-semibold text-stone-700 block mb-0.5">Ecological Pressure Detection</span>
              <span className="text-stone-500 text-[11px]">Multi-metric analysis across ≥3 environmental variables</span>
            </div>
            <div className="p-2.5 bg-white border border-stone-200 rounded-xs">
              <span className="font-semibold text-stone-700 block mb-0.5">Intervention Feasibility & Trade-offs</span>
              <span className="text-stone-500 text-[11px]">Context-specific land-use, resource, and time horizons</span>
            </div>
            <div className="p-2.5 bg-white border border-stone-200 rounded-xs">
              <span className="font-semibold text-stone-700 block mb-0.5">Peer-Reviewed Evidence Mapping</span>
              <span className="text-stone-500 text-[11px]">Strict claim grounding (IPCC, IPBES, FAO, UNEP, CBD)</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
