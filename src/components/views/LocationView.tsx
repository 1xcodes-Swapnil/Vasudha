import React from 'react';
import { MapPin, Globe, Compass, Database, ShieldCheck, CheckCircle2, Layers } from 'lucide-react';
import { EnvironmentalState, SpatialContext } from '../../types';
import { GeoContextMap } from '../GeoContextMap';

interface LocationViewProps {
  state: EnvironmentalState;
  onSpatialContextChange: (spatialContext: SpatialContext) => void;
}

export const LocationView: React.FC<LocationViewProps> = ({ state, onSpatialContextChange }) => {
  return (
    <div className="max-w-6xl mx-auto space-y-6 pb-12">
      {/* Header Context Banner */}
      <div className="bg-white border border-stone-200 rounded-2xl p-4 sm:p-5 shadow-2xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <Globe className="w-4 h-4 text-emerald-700" />
            <h2 className="text-sm font-bold text-stone-900 tracking-tight font-mono uppercase">
              Spatial Resolution & Geographic Grounding
            </h2>
          </div>
          <p className="text-xs text-stone-500 mt-0.5">
            Click anywhere on the interactive canvas or enter coordinates to resolve the territorial biome.
          </p>
        </div>

        {/* Spatial Baselines Metadata Pills */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="px-2.5 py-1 rounded-md bg-stone-100 border border-stone-200 text-[11px] font-mono text-stone-700 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500" />
            <span>SoilGrids: 250m</span>
          </div>
          <div className="px-2.5 py-1 rounded-md bg-stone-100 border border-stone-200 text-[11px] font-mono text-stone-700 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-blue-500" />
            <span>ERA5 Climate: 0.1°</span>
          </div>
          <div className="px-2.5 py-1 rounded-md bg-stone-100 border border-stone-200 text-[11px] font-mono text-stone-700 flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-teal-500" />
            <span>Copernicus Land: 10m</span>
          </div>
        </div>
      </div>

      {/* Prominent Map Container */}
      <div className="bg-white rounded-2xl border border-stone-200 shadow-xs overflow-hidden">
        <GeoContextMap
          spatialContext={state.spatial_context}
          onSpatialChange={onSpatialContextChange}
        />
      </div>

      {/* Territorial Grounding Notes */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-stone-50 border border-stone-200 rounded-xl p-4 text-xs space-y-1.5">
          <div className="flex items-center gap-1.5 font-mono font-bold text-stone-800 uppercase tracking-wider text-[11px]">
            <Compass className="w-3.5 h-3.5 text-emerald-600" />
            <span>Ecological Ecoregion</span>
          </div>
          <p className="text-stone-600">
            Current coordinates resolve to <strong>{state.spatial_context.region || 'Unspecified'}</strong> ({state.spatial_context.ecosystem || 'General Biome'}).
          </p>
        </div>

        <div className="bg-stone-50 border border-stone-200 rounded-xl p-4 text-xs space-y-1.5">
          <div className="flex items-center gap-1.5 font-mono font-bold text-stone-800 uppercase tracking-wider text-[11px]">
            <Database className="w-3.5 h-3.5 text-blue-600" />
            <span>Authoritative Ingestion</span>
          </div>
          <p className="text-stone-600">
            Coordinates automatically link to global SoilGrids, GBIF species occurrences, and WorldClim precipitation grids.
          </p>
        </div>

        <div className="bg-stone-50 border border-stone-200 rounded-xl p-4 text-xs space-y-1.5">
          <div className="flex items-center gap-1.5 font-mono font-bold text-stone-800 uppercase tracking-wider text-[11px]">
            <ShieldCheck className="w-3.5 h-3.5 text-teal-600" />
            <span>RAG Grounding Filter</span>
          </div>
          <p className="text-stone-600">
            Intervention recommendations prioritize literature verified within this climate zone and soil classification.
          </p>
        </div>
      </div>
    </div>
  );
};
