import React, { useState, useRef, useEffect } from 'react';
import { Menu, MapPin, ChevronDown, Plus, RotateCcw, Check } from 'lucide-react';
import { WorkspaceTab } from './Sidebar';

interface TopBarProps {
  activeTab: WorkspaceTab;
  onOpenMobileMenu: () => void;
  onSelectTab: (tab: WorkspaceTab) => void;
  onResetSession: () => void;
  onNewAnalysis: () => void;
  onSelectLocation?: (location: {
    region: string;
    ecosystem: string;
    lat: number;
    lon: number;
  }) => void;
  currentRegion?: string;
  coordinates?: { lat: number | null; lon: number | null };
}

const AVAILABLE_LOCATIONS = [
  {
    region: 'Nandurbar, Maharashtra, India',
    ecosystem: 'Tropical Dry Deciduous / Cropland Ecotone',
    lat: 21.25,
    lon: 74.23,
    description: 'Cropland Biodiversity Assessment (Primary Benchmark)',
  },
  {
    region: 'Deccan Plateau, India',
    ecosystem: 'Tropical Dry Deciduous / Semi-Arid Cropland',
    lat: 12.9716,
    lon: 77.5946,
    description: 'Degraded Semi-Arid Monoculture Cropland',
  },
  {
    region: 'Cerrado Biome, Brazil',
    ecosystem: 'Wooded Savanna / Agro-Ecological Transition',
    lat: -14.235,
    lon: -51.9253,
    description: 'Savanna Ecoregion & Riparian Buffer',
  },
  {
    region: 'Murcia Basin, Spain',
    ecosystem: 'Mediterranean Dry Scrubland / Olive Agro-Ecosystem',
    lat: 37.9922,
    lon: -1.1307,
    description: 'Arid Soil Erosion & Water Scarcity Basin',
  },
];

export const TopBar: React.FC<TopBarProps> = ({
  onOpenMobileMenu,
  onResetSession,
  onNewAnalysis,
  onSelectLocation,
  currentRegion = 'Nandurbar, Maharashtra, India',
}) => {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsDropdownOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <header className="sticky top-0 z-30 bg-[#f7f8f5]/90 backdrop-blur-md px-4 sm:px-8 py-3.5 border-b border-stone-200/60">
      <div className="flex items-center justify-between gap-4 max-w-7xl mx-auto">
        {/* Left: Mobile Menu Toggle & Location Dropdown */}
        <div className="flex items-center gap-3 min-w-0">
          <button
            onClick={onOpenMobileMenu}
            className="p-1.5 -ml-1.5 rounded-lg text-stone-600 hover:text-stone-900 hover:bg-stone-200/60 lg:hidden focus:outline-hidden"
            aria-label="Open sidebar navigation"
          >
            <Menu className="w-5 h-5" />
          </button>

          {/* Interactive Location Dropdown Selector */}
          <div className="relative" ref={dropdownRef}>
            <button
              onClick={() => setIsDropdownOpen(!isDropdownOpen)}
              className="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-stone-200/50 text-stone-800 text-sm font-medium transition-colors cursor-pointer group"
              title="Select geographic location context"
            >
              <MapPin className="w-4 h-4 text-stone-700 shrink-0 group-hover:text-emerald-700 transition-colors" />
              <span className="font-semibold text-stone-800 truncate max-w-[200px] sm:max-w-[280px]">
                {currentRegion}
              </span>
              <ChevronDown
                className={`w-3.5 h-3.5 text-stone-500 transition-transform duration-150 ${
                  isDropdownOpen ? 'rotate-180' : ''
                }`}
              />
            </button>

            {/* Dropdown Menu */}
            {isDropdownOpen && (
              <div className="absolute left-0 mt-1.5 w-80 sm:w-96 bg-white rounded-xl shadow-lg border border-stone-200/90 py-2 z-50 animate-in fade-in zoom-in-95 duration-150">
                <div className="px-3.5 py-1.5 text-[10px] font-mono uppercase tracking-wider text-stone-700 font-semibold border-b border-stone-100">
                  Select Environmental Context:
                </div>
                <div className="max-h-72 overflow-y-auto py-1">
                  {AVAILABLE_LOCATIONS.map((loc) => {
                    const isSelected = loc.region === currentRegion;
                    return (
                      <button
                        key={loc.region}
                        onClick={() => {
                          if (onSelectLocation) {
                            onSelectLocation(loc);
                          }
                          setIsDropdownOpen(false);
                        }}
                        className={`w-full px-3.5 py-2.5 text-left flex items-start justify-between gap-2 hover:bg-stone-50 transition-colors ${
                          isSelected ? 'bg-emerald-50/70 text-emerald-900' : 'text-stone-700'
                        }`}
                      >
                        <div>
                          <div className="text-xs font-semibold text-stone-900 flex items-center gap-1.5">
                            <MapPin className="w-3 h-3 text-emerald-600 shrink-0" />
                            <span>{loc.region}</span>
                          </div>
                          <div className="text-[11px] text-stone-700 mt-0.5 font-sans">
                            {loc.ecosystem}
                          </div>
                          <div className="text-[10px] text-stone-600 font-mono mt-0.5">
                            {loc.lat}° N, {loc.lon}° E
                          </div>
                        </div>
                        {isSelected && (
                          <Check className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Right Actions: + New Analysis, Reset Session, User Avatar */}
        <div className="flex items-center gap-2.5 sm:gap-3 shrink-0">
          <button
            onClick={onNewAnalysis}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white hover:bg-stone-50 text-stone-700 text-xs font-medium rounded-lg border border-stone-200/80 shadow-2xs transition-all hover:border-stone-300"
            title="Start new analysis with benchmark baseline"
          >
            <Plus className="w-3.5 h-3.5 text-stone-600" />
            <span>New Analysis</span>
          </button>

          <button
            onClick={onResetSession}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white hover:bg-stone-50 text-stone-700 text-xs font-medium rounded-lg border border-stone-200/80 shadow-2xs transition-all hover:border-stone-300"
            title="Reset conversation dialogue session"
          >
            <RotateCcw className="w-3.5 h-3.5 text-stone-600" />
            <span className="hidden sm:inline">Reset Session</span>
          </button>

          {/* User Profile Avatar Circle (swapniljee5205@gmail.com -> 'S') */}
          <div
            className="w-8 h-8 rounded-full bg-[#1b3b30] text-white flex items-center justify-center text-xs font-semibold shadow-2xs select-none ring-2 ring-emerald-900/10 cursor-pointer"
            title="Swapnil (swapniljee5205@gmail.com)"
          >
            S
          </div>
        </div>
      </div>
    </header>
  );
};
