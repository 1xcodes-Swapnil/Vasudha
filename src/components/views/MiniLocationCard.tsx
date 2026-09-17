import React from 'react';
import { MapPin, ArrowRight } from 'lucide-react';
import { SpatialContext } from '../../types';

interface MiniLocationCardProps {
  spatialContext: SpatialContext;
  onViewMap: () => void;
}

export const MiniLocationCard: React.FC<MiniLocationCardProps> = ({
  spatialContext,
  onViewMap,
}) => {
  const lat = spatialContext.latitude ?? 21.25;
  const lon = spatialContext.longitude ?? 74.23;
  const region = spatialContext.region || 'Nandurbar, Maharashtra, India';

  return (
    <div className="bg-white rounded-2xl border border-stone-200/80 p-4 shadow-2xs space-y-3">
      {/* Header */}
      <div className="flex items-center gap-2 text-stone-800 text-xs font-semibold">
        <MapPin className="w-4 h-4 text-stone-700" />
        <span>Current Location</span>
      </div>

      {/* Mini Map Visual Thumbnail */}
      <div
        onClick={onViewMap}
        className="relative w-full h-28 rounded-xl overflow-hidden border border-stone-200/70 bg-[#e7eee6] cursor-pointer group select-none"
        title="Click to view full interactive map"
      >
        {/* Topographic Contour Map Graphic */}
        <svg
          viewBox="0 0 300 140"
          preserveAspectRatio="none"
          className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
        >
          <defs>
            <linearGradient id="terrainGrad" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#e4eee3" />
              <stop offset="50%" stopColor="#d5e5d3" />
              <stop offset="100%" stopColor="#c5dac3" />
            </linearGradient>
            <linearGradient id="hill1" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#bdd5bb" stopOpacity="0.7" />
              <stop offset="100%" stopColor="#a9c6a7" stopOpacity="0.9" />
            </linearGradient>
            <linearGradient id="hill2" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#9bb999" stopOpacity="0.8" />
              <stop offset="100%" stopColor="#87a884" stopOpacity="0.95" />
            </linearGradient>
          </defs>

          {/* Base Terrain */}
          <rect width="300" height="140" fill="url(#terrainGrad)" />

          {/* Topographic Contour Lines */}
          <path
            d="M -10 40 C 60 20, 140 60, 220 30 C 260 15, 290 35, 310 25"
            stroke="#9db99b"
            strokeWidth="1.2"
            fill="none"
            opacity="0.6"
          />
          <path
            d="M -10 70 C 50 50, 120 90, 200 65 C 250 50, 280 75, 310 60"
            stroke="#9db99b"
            strokeWidth="1.2"
            fill="none"
            opacity="0.6"
          />
          <path
            d="M -10 110 C 70 85, 150 120, 230 100 C 270 90, 290 105, 310 95"
            stroke="#9db99b"
            strokeWidth="1.2"
            fill="none"
            opacity="0.6"
          />

          {/* Subtle River / Stream */}
          <path
            d="M 120 140 C 130 100, 180 70, 170 0"
            stroke="#cadfd1"
            strokeWidth="8"
            strokeLinecap="round"
            fill="none"
          />
          <path
            d="M 120 140 C 130 100, 180 70, 170 0"
            stroke="#b3d1bc"
            strokeWidth="3.5"
            strokeLinecap="round"
            fill="none"
          />

          {/* Low Hill Profiles */}
          <path
            d="M 0 100 Q 60 60, 130 95 T 260 85 T 310 110 L 310 140 L 0 140 Z"
            fill="url(#hill1)"
          />
          <path
            d="M 40 140 Q 120 90, 200 125 T 300 115 L 300 140 Z"
            fill="url(#hill2)"
          />
        </svg>

        {/* Center Marker Pin */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="relative -mt-2">
            <div className="w-6 h-6 rounded-full bg-stone-900/20 absolute -inset-0.5 animate-ping opacity-75" />
            <div className="w-7 h-7 rounded-full bg-stone-900 text-white flex items-center justify-center shadow-md ring-2 ring-white">
              <MapPin className="w-3.5 h-3.5 fill-white text-stone-900" />
            </div>
          </div>
        </div>

        {/* Hover overlay hint */}
        <div className="absolute inset-0 bg-emerald-900/10 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center text-[11px] font-medium text-emerald-950">
          <span className="bg-white/90 px-2 py-0.5 rounded-md shadow-2xs">Expand Map</span>
        </div>
      </div>

      {/* Location Details */}
      <div className="space-y-0.5">
        <h4 className="text-xs font-bold text-stone-900">{region}</h4>
        <p className="text-[11px] text-stone-500 font-mono">
          {lat.toFixed(2)}° N, {lon.toFixed(2)}° E
        </p>
      </div>

      {/* View on Map link */}
      <button
        onClick={onViewMap}
        className="text-[11px] text-stone-700 hover:text-emerald-800 font-medium flex items-center gap-1 group transition-colors pt-0.5"
      >
        <span>View on Map</span>
        <ArrowRight className="w-3 h-3 text-stone-500 group-hover:text-emerald-700 group-hover:translate-x-0.5 transition-all" />
      </button>
    </div>
  );
};
