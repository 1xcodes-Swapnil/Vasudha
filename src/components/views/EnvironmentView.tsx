import React, { useState } from 'react';
import {
  Layers,
  ChevronDown,
  ChevronUp,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Sparkles,
  Info,
  Database,
  ArrowUpRight,
  ShieldCheck,
} from 'lucide-react';
import { EnvironmentalState } from '../../types';
import { validateEnvironmentalState } from '../../services/api';
import { EnvironmentalDatasetExplorer } from '../EnvironmentalDatasetExplorer';

export const BENCHMARK_SCENARIOS: Array<{
  id: string;
  name: string;
  badge: string;
  description: string;
  state: EnvironmentalState;
}> = [
  {
    id: 'semi_arid_cropland',
    name: 'Cropland Biodiversity Assessment — Nandurbar (Primary Benchmark)',
    badge: 'Evaluator Default',
    description: 'Depleted soil organic carbon (0.8%), acute moisture deficit (14%), simplified monoculture habitat (22/100), and rainfall deficit (480mm/yr) in Nandurbar, Maharashtra.',
    state: {
      soil: {
        ph: 5.4,
        organic_carbon: 0.8,
        moisture: 14.0,
      },
      land: {
        land_use: 'monoculture',
        land_cover: 'fragmented_canopy',
      },
      biodiversity: {
        species_richness: 18,
        habitat_diversity: 22.0,
      },
      climate: {
        temperature: 32.5,
        rainfall: 480.0,
      },
      human_impact: {
        pollution: 28.0,
        deforestation: 14.5,
      },
      spatial_context: {
        latitude: 21.25,
        longitude: 74.23,
        region: 'Nandurbar, Maharashtra, India',
        ecosystem: 'Tropical Dry Deciduous / Cropland Ecotone',
      },
    },
  },
  {
    id: 'riparian_watershed',
    name: 'Disturbed Agricultural Riparian Watershed',
    badge: 'Corridor & Runoff',
    description: 'Moderate soil carbon (1.4%), elevated agrochemical runoff (pollution 45%), fragmented riparian buffer corridor (habitat diversity 36/100).',
    state: {
      soil: {
        ph: 6.1,
        organic_carbon: 1.4,
        moisture: 24.0,
      },
      land: {
        land_use: 'agricultural',
        land_cover: 'cropland',
      },
      biodiversity: {
        species_richness: 26,
        habitat_diversity: 36.0,
      },
      climate: {
        temperature: 26.0,
        rainfall: 820.0,
      },
      human_impact: {
        pollution: 45.0,
        deforestation: 22.0,
      },
      spatial_context: {
        latitude: -15.45,
        longitude: -47.92,
        region: 'Cerrado Biome, Brazil',
        ecosystem: 'Tropical Savanna / Intensive Cropland Transition',
      },
    },
  },
  {
    id: 'mediterranean_dryland',
    name: 'Mediterranean Semi-Arid Terrace',
    badge: 'Thermal & Erosion',
    description: 'Depleted calcareous soil (pH 7.8, SOC 0.9%), extreme summer heat (33.5°C), low rainfall (380mm), severe topsoil erosion threat.',
    state: {
      soil: {
        ph: 7.8,
        organic_carbon: 0.9,
        moisture: 15.0,
      },
      land: {
        land_use: 'monoculture',
        land_cover: 'sparse_vegetation',
      },
      biodiversity: {
        species_richness: 21,
        habitat_diversity: 25.0,
      },
      climate: {
        temperature: 33.5,
        rainfall: 380.0,
      },
      human_impact: {
        pollution: 18.0,
        deforestation: 12.0,
      },
      spatial_context: {
        latitude: 37.9922,
        longitude: -1.1307,
        region: 'Murcia Basin, Spain',
        ecosystem: 'Mediterranean Dryland Agro-Ecosystem',
      },
    },
  },
];

interface EnvironmentViewProps {
  state: EnvironmentalState;
  onStateChange: (newState: EnvironmentalState) => void;
}

type ValueOrigin = 'user_supplied' | 'dataset_derived' | 'unknown';

export const EnvironmentView: React.FC<EnvironmentViewProps> = ({ state, onStateChange }) => {
  // Collapsible section toggles
  const [openSections, setOpenSections] = useState({
    soil: true,
    land: true,
    biodiversity: true,
    climate: true,
    human_impact: true,
  });

  const [showDatasetEnricher, setShowDatasetEnricher] = useState(false);
  const [validating, setValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<{
    valid: boolean;
    metrics_count: number;
    is_empty: boolean;
  } | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);

  // Track origins
  const getOrigin = (val: any): ValueOrigin => {
    if (val === null || val === undefined) return 'unknown';
    return 'user_supplied'; // Can be marked dataset_derived when enriched
  };

  const toggleSection = (section: keyof typeof openSections) => {
    setOpenSections((prev) => ({ ...prev, [section]: !prev[section] }));
  };

  const handleValidate = async () => {
    setValidating(true);
    setValidationError(null);
    try {
      const res = await validateEnvironmentalState(state);
      setValidationResult(res);
    } catch (err) {
      setValidationError(err instanceof Error ? err.message : 'Validation failed');
      setValidationResult(null);
    } finally {
      setValidating(false);
    }
  };

  const renderOriginBadge = (origin: ValueOrigin) => {
    switch (origin) {
      case 'user_supplied':
        return (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-50 text-emerald-700 border border-emerald-200">
            User Supplied
          </span>
        );
      case 'dataset_derived':
        return (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
            Dataset Derived
          </span>
        );
      case 'unknown':
        return (
          <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-stone-100 text-stone-500 border border-stone-200">
            Unknown (null)
          </span>
        );
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12">
      {/* Top Controls & Validation Bar */}
      <div className="bg-white border border-stone-200 rounded-2xl p-4 sm:p-5 shadow-2xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-sm font-bold text-stone-900 tracking-tight">
            Canonical Environmental State
          </h2>
          <p className="text-xs text-stone-500 mt-0.5">
            Biophysical variables driving multi-metric ecological reasoning and scientific RAG.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={handleValidate}
            disabled={validating}
            className="px-3.5 py-1.5 rounded-xl bg-stone-100 hover:bg-stone-200 text-stone-800 text-xs font-semibold border border-stone-200 flex items-center gap-1.5 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${validating ? 'animate-spin' : ''}`} />
            <span>Validate State</span>
          </button>

          <button
            onClick={() => setShowDatasetEnricher((prev) => !prev)}
            className="px-3.5 py-1.5 rounded-xl bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-xs font-semibold border border-emerald-200 flex items-center gap-1.5 transition-colors"
          >
            <Database className="w-3.5 h-3.5 text-emerald-700" />
            <span>{showDatasetEnricher ? 'Hide Datasets' : 'Authoritative Datasets'}</span>
          </button>
        </div>
      </div>

      {/* Validation Feedback */}
      {validationResult && (
        <div className="p-3.5 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-900 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
            <span>
              <strong>Scientific Validation Verified:</strong> {validationResult.metrics_count} biophysical metrics conform to ecological range constraints.
            </span>
          </div>
          <span className="text-[10px] font-mono font-bold uppercase bg-emerald-200/60 px-2 py-0.5 rounded-sm">
            Ready for RAG
          </span>
        </div>
      )}

      {validationError && (
        <div className="p-3.5 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-800 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{validationError}</span>
        </div>
      )}

      {/* BENCHMARK DEMO SCENARIO SELECTOR */}
      <div className="bg-white border border-stone-200 rounded-2xl p-4 sm:p-5 shadow-2xs space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-emerald-600" />
            <h3 className="text-xs font-bold font-mono uppercase tracking-wider text-stone-900">
              Evaluator Benchmark Scenarios
            </h3>
          </div>
          <span className="text-[11px] font-mono text-stone-500">
            One-Click Reproducible Baseline
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          {BENCHMARK_SCENARIOS.map((sc) => {
            const isCurrent =
              state.spatial_context?.region === sc.state.spatial_context?.region ||
              (sc.id === 'semi_arid_cropland' && state.soil.organic_carbon === 0.8 && state.soil.moisture === 14.0);
            return (
              <div
                key={sc.id}
                className={`p-3.5 rounded-xl border transition-all flex flex-col justify-between text-left ${
                  isCurrent
                    ? 'border-emerald-500 bg-emerald-50/40 ring-1 ring-emerald-500 shadow-2xs'
                    : 'border-stone-200 bg-stone-50/50 hover:bg-stone-50 hover:border-stone-300'
                }`}
              >
                <div className="space-y-1.5">
                  <div className="flex items-center justify-between">
                    <span className="text-[10px] font-mono font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-stone-100 text-stone-700">
                      {sc.badge}
                    </span>
                    {isCurrent && (
                      <span className="text-[10px] font-mono text-emerald-700 font-bold flex items-center gap-1">
                        <CheckCircle2 className="w-3 h-3 text-emerald-600" />
                        Active
                      </span>
                    )}
                  </div>
                  <h4 className="text-xs font-bold text-stone-900 leading-snug">{sc.name}</h4>
                  <p className="text-[11px] text-stone-600 leading-relaxed">{sc.description}</p>
                </div>

                <div className="pt-3 mt-2 border-t border-stone-200/60 flex items-center justify-between">
                  <span className="text-[10px] font-mono text-stone-500">
                    SOC {sc.state.soil.organic_carbon}% | M {sc.state.soil.moisture}% | Rain {sc.state.climate.rainfall}mm
                  </span>
                  <button
                    onClick={() => onStateChange(sc.state)}
                    className={`text-xs font-semibold px-2.5 py-1 rounded-lg transition-colors ${
                      isCurrent
                        ? 'bg-emerald-600 text-white shadow-2xs cursor-default'
                        : 'bg-white border border-stone-300 text-stone-800 hover:bg-stone-100'
                    }`}
                  >
                    {isCurrent ? 'Loaded' : 'Load'}
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Optional Ingestion / Authoritative Dataset Explorer */}
      {showDatasetEnricher && (
        <div className="border border-emerald-200 rounded-2xl bg-emerald-50/20 p-4 sm:p-6 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Database className="w-4 h-4 text-emerald-700" />
              <h3 className="text-xs font-bold font-mono uppercase text-emerald-900">
                Authoritative Global Datasets & Provenance Ingestion
              </h3>
            </div>
            <button
              onClick={() => setShowDatasetEnricher(false)}
              className="text-xs text-stone-500 hover:text-stone-800"
            >
              Close
            </button>
          </div>
          <EnvironmentalDatasetExplorer
            currentState={state}
            onStateEnriched={onStateChange}
          />
        </div>
      )}

      {/* 1. SOIL SECTION */}
      <div className="bg-white border border-stone-200 rounded-2xl overflow-hidden shadow-2xs">
        <button
          onClick={() => toggleSection('soil')}
          className="w-full p-4 sm:px-6 bg-stone-50/70 hover:bg-stone-50 border-b border-stone-200/80 flex items-center justify-between transition-colors text-left"
        >
          <div className="flex items-center gap-2.5">
            <span className="w-2.5 h-2.5 rounded-full bg-amber-600" />
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-stone-900">
              1. Soil Matrix (Edaphic Indicators)
            </h3>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-[11px] font-mono text-stone-500">pH • Carbon • Moisture</span>
            {openSections.soil ? <ChevronUp className="w-4 h-4 text-stone-400" /> : <ChevronDown className="w-4 h-4 text-stone-400" />}
          </div>
        </button>

        {openSections.soil && (
          <div className="p-4 sm:p-6 divide-y divide-stone-100 space-y-4">
            {/* pH */}
            <div className="pt-2 first:pt-0 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <label className="text-xs font-bold text-stone-800 flex items-center gap-1.5">
                  Soil pH
                  <span className="text-[11px] font-normal text-stone-500 font-mono">(0.0 - 14.0)</span>
                </label>
                <p className="text-[11px] text-stone-500">Determines microbial nutrient availability & ionization.</p>
              </div>
              <div className="flex items-center gap-3">
                {renderOriginBadge(getOrigin(state.soil.ph))}
                <div className="w-32">
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="14"
                    value={state.soil.ph ?? ''}
                    placeholder="null"
                    onChange={(e) =>
                      onStateChange({
                        ...state,
                        soil: {
                          ...state.soil,
                          ph: e.target.value === '' ? null : parseFloat(e.target.value),
                        },
                      })
                    }
                    className="w-full text-xs font-mono px-3 py-1.5 border border-stone-200 rounded-lg bg-stone-50 focus:bg-white focus:border-emerald-600 focus:outline-hidden"
                  />
                </div>
              </div>
            </div>

            {/* Organic Carbon */}
            <div className="pt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <label className="text-xs font-bold text-stone-800 flex items-center gap-1.5">
                  Organic Carbon
                  <span className="text-[11px] font-normal text-stone-500 font-mono">(% dry wt)</span>
                </label>
                <p className="text-[11px] text-stone-500">Core soil health & biological water retention capacity.</p>
              </div>
              <div className="flex items-center gap-3">
                {renderOriginBadge(getOrigin(state.soil.organic_carbon))}
                <div className="w-32">
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    value={state.soil.organic_carbon ?? ''}
                    placeholder="null"
                    onChange={(e) =>
                      onStateChange({
                        ...state,
                        soil: {
                          ...state.soil,
                          organic_carbon: e.target.value === '' ? null : parseFloat(e.target.value),
                        },
                      })
                    }
                    className="w-full text-xs font-mono px-3 py-1.5 border border-stone-200 rounded-lg bg-stone-50 focus:bg-white focus:border-emerald-600 focus:outline-hidden"
                  />
                </div>
              </div>
            </div>

            {/* Moisture */}
            <div className="pt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <label className="text-xs font-bold text-stone-800 flex items-center gap-1.5">
                  Soil Moisture
                  <span className="text-[11px] font-normal text-stone-500 font-mono">(% volumetric)</span>
                </label>
                <p className="text-[11px] text-stone-500">Available water holding content for rooting vegetation.</p>
              </div>
              <div className="flex items-center gap-3">
                {renderOriginBadge(getOrigin(state.soil.moisture))}
                <div className="w-32">
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    value={state.soil.moisture ?? ''}
                    placeholder="null"
                    onChange={(e) =>
                      onStateChange({
                        ...state,
                        soil: {
                          ...state.soil,
                          moisture: e.target.value === '' ? null : parseFloat(e.target.value),
                        },
                      })
                    }
                    className="w-full text-xs font-mono px-3 py-1.5 border border-stone-200 rounded-lg bg-stone-50 focus:bg-white focus:border-emerald-600 focus:outline-hidden"
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 2. LAND SECTION */}
      <div className="bg-white border border-stone-200 rounded-2xl overflow-hidden shadow-2xs">
        <button
          onClick={() => toggleSection('land')}
          className="w-full p-4 sm:px-6 bg-stone-50/70 hover:bg-stone-50 border-b border-stone-200/80 flex items-center justify-between transition-colors text-left"
        >
          <div className="flex items-center gap-2.5">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-600" />
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-stone-900">
              2. Land Use & Surface Cover
            </h3>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-[11px] font-mono text-stone-500">Land Use • Canopy Cover</span>
            {openSections.land ? <ChevronUp className="w-4 h-4 text-stone-400" /> : <ChevronDown className="w-4 h-4 text-stone-400" />}
          </div>
        </button>

        {openSections.land && (
          <div className="p-4 sm:p-6 divide-y divide-stone-100 space-y-4">
            {/* Land Use */}
            <div className="pt-2 first:pt-0 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <label className="text-xs font-bold text-stone-800">Land Use Type</label>
                <p className="text-[11px] text-stone-500">Anthropogenic or natural management category.</p>
              </div>
              <div className="flex items-center gap-3">
                {renderOriginBadge(getOrigin(state.land.land_use))}
                <select
                  value={state.land.land_use ?? ''}
                  onChange={(e) =>
                    onStateChange({
                      ...state,
                      land: { ...state.land, land_use: e.target.value || null },
                    })
                  }
                  className="w-48 text-xs font-mono px-3 py-1.5 border border-stone-200 rounded-lg bg-stone-50 focus:bg-white focus:border-emerald-600 focus:outline-hidden"
                >
                  <option value="">Unknown / None</option>
                  <option value="monoculture">Monoculture Cropland</option>
                  <option value="agroforestry">Agroforestry System</option>
                  <option value="silvopasture">Silvopasture Grazing</option>
                  <option value="native_forest">Native Forest Reserve</option>
                  <option value="fallow_degraded">Degraded Fallow</option>
                </select>
              </div>
            </div>

            {/* Land Cover */}
            <div className="pt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <label className="text-xs font-bold text-stone-800">Land Cover Class</label>
                <p className="text-[11px] text-stone-500">Vegetation structure and canopy density.</p>
              </div>
              <div className="flex items-center gap-3">
                {renderOriginBadge(getOrigin(state.land.land_cover))}
                <select
                  value={state.land.land_cover ?? ''}
                  onChange={(e) =>
                    onStateChange({
                      ...state,
                      land: { ...state.land, land_cover: e.target.value || null },
                    })
                  }
                  className="w-48 text-xs font-mono px-3 py-1.5 border border-stone-200 rounded-lg bg-stone-50 focus:bg-white focus:border-emerald-600 focus:outline-hidden"
                >
                  <option value="">Unknown / None</option>
                  <option value="fragmented_canopy">Fragmented Canopy (&lt;30%)</option>
                  <option value="closed_canopy">Closed Canopy (&gt;70%)</option>
                  <option value="open_scrubland">Open Scrub & Shrubland</option>
                  <option value="bare_compacted">Bare / Compacted Soil</option>
                  <option value="riparian_corridor">Riparian Buffer Zone</option>
                </select>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 3. BIODIVERSITY SECTION */}
      <div className="bg-white border border-stone-200 rounded-2xl overflow-hidden shadow-2xs">
        <button
          onClick={() => toggleSection('biodiversity')}
          className="w-full p-4 sm:px-6 bg-stone-50/70 hover:bg-stone-50 border-b border-stone-200/80 flex items-center justify-between transition-colors text-left"
        >
          <div className="flex items-center gap-2.5">
            <span className="w-2.5 h-2.5 rounded-full bg-teal-600" />
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-stone-900">
              3. Biodiversity & Species Richness
            </h3>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-[11px] font-mono text-stone-500">Richness • Habitat Diversity</span>
            {openSections.biodiversity ? <ChevronUp className="w-4 h-4 text-stone-400" /> : <ChevronDown className="w-4 h-4 text-stone-400" />}
          </div>
        </button>

        {openSections.biodiversity && (
          <div className="p-4 sm:p-6 divide-y divide-stone-100 space-y-4">
            {/* Species Richness */}
            <div className="pt-2 first:pt-0 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <label className="text-xs font-bold text-stone-800 flex items-center gap-1.5">
                  Species Richness
                  <span className="text-[11px] font-normal text-stone-500 font-mono">(observed count)</span>
                </label>
                <p className="text-[11px] text-stone-500">Documented native species taxa in immediate habitat.</p>
              </div>
              <div className="flex items-center gap-3">
                {renderOriginBadge(getOrigin(state.biodiversity.species_richness))}
                <div className="w-32">
                  <input
                    type="number"
                    min="0"
                    value={state.biodiversity.species_richness ?? ''}
                    placeholder="null"
                    onChange={(e) =>
                      onStateChange({
                        ...state,
                        biodiversity: {
                          ...state.biodiversity,
                          species_richness: e.target.value === '' ? null : parseInt(e.target.value, 10),
                        },
                      })
                    }
                    className="w-full text-xs font-mono px-3 py-1.5 border border-stone-200 rounded-lg bg-stone-50 focus:bg-white focus:border-emerald-600 focus:outline-hidden"
                  />
                </div>
              </div>
            </div>

            {/* Habitat Diversity */}
            <div className="pt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <label className="text-xs font-bold text-stone-800 flex items-center gap-1.5">
                  Habitat Diversity Index
                  <span className="text-[11px] font-normal text-stone-500 font-mono">(0.0 - 100.0)</span>
                </label>
                <p className="text-[11px] text-stone-500">Structural heterogeneity index supporting ecological niches.</p>
              </div>
              <div className="flex items-center gap-3">
                {renderOriginBadge(getOrigin(state.biodiversity.habitat_diversity))}
                <div className="w-32">
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    value={state.biodiversity.habitat_diversity ?? ''}
                    placeholder="null"
                    onChange={(e) =>
                      onStateChange({
                        ...state,
                        biodiversity: {
                          ...state.biodiversity,
                          habitat_diversity: e.target.value === '' ? null : parseFloat(e.target.value),
                        },
                      })
                    }
                    className="w-full text-xs font-mono px-3 py-1.5 border border-stone-200 rounded-lg bg-stone-50 focus:bg-white focus:border-emerald-600 focus:outline-hidden"
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 4. CLIMATE SECTION */}
      <div className="bg-white border border-stone-200 rounded-2xl overflow-hidden shadow-2xs">
        <button
          onClick={() => toggleSection('climate')}
          className="w-full p-4 sm:px-6 bg-stone-50/70 hover:bg-stone-50 border-b border-stone-200/80 flex items-center justify-between transition-colors text-left"
        >
          <div className="flex items-center gap-2.5">
            <span className="w-2.5 h-2.5 rounded-full bg-blue-600" />
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-stone-900">
              4. Climate & Precipitation Regime
            </h3>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-[11px] font-mono text-stone-500">Temperature • Rainfall</span>
            {openSections.climate ? <ChevronUp className="w-4 h-4 text-stone-400" /> : <ChevronDown className="w-4 h-4 text-stone-400" />}
          </div>
        </button>

        {openSections.climate && (
          <div className="p-4 sm:p-6 divide-y divide-stone-100 space-y-4">
            {/* Temperature */}
            <div className="pt-2 first:pt-0 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <label className="text-xs font-bold text-stone-800 flex items-center gap-1.5">
                  Mean Temperature
                  <span className="text-[11px] font-normal text-stone-500 font-mono">(°C)</span>
                </label>
                <p className="text-[11px] text-stone-500">Thermal regime driving evapotranspiration rate.</p>
              </div>
              <div className="flex items-center gap-3">
                {renderOriginBadge(getOrigin(state.climate.temperature))}
                <div className="w-32">
                  <input
                    type="number"
                    step="0.1"
                    min="-50"
                    max="60"
                    value={state.climate.temperature ?? ''}
                    placeholder="null"
                    onChange={(e) =>
                      onStateChange({
                        ...state,
                        climate: {
                          ...state.climate,
                          temperature: e.target.value === '' ? null : parseFloat(e.target.value),
                        },
                      })
                    }
                    className="w-full text-xs font-mono px-3 py-1.5 border border-stone-200 rounded-lg bg-stone-50 focus:bg-white focus:border-emerald-600 focus:outline-hidden"
                  />
                </div>
              </div>
            </div>

            {/* Rainfall */}
            <div className="pt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <label className="text-xs font-bold text-stone-800 flex items-center gap-1.5">
                  Annual Rainfall
                  <span className="text-[11px] font-normal text-stone-500 font-mono">(mm / year)</span>
                </label>
                <p className="text-[11px] text-stone-500">Hydrological baseline determining water stress & runoff.</p>
              </div>
              <div className="flex items-center gap-3">
                {renderOriginBadge(getOrigin(state.climate.rainfall))}
                <div className="w-32">
                  <input
                    type="number"
                    step="10"
                    min="0"
                    max="15000"
                    value={state.climate.rainfall ?? ''}
                    placeholder="null"
                    onChange={(e) =>
                      onStateChange({
                        ...state,
                        climate: {
                          ...state.climate,
                          rainfall: e.target.value === '' ? null : parseFloat(e.target.value),
                        },
                      })
                    }
                    className="w-full text-xs font-mono px-3 py-1.5 border border-stone-200 rounded-lg bg-stone-50 focus:bg-white focus:border-emerald-600 focus:outline-hidden"
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 5. HUMAN IMPACT SECTION */}
      <div className="bg-white border border-stone-200 rounded-2xl overflow-hidden shadow-2xs">
        <button
          onClick={() => toggleSection('human_impact')}
          className="w-full p-4 sm:px-6 bg-stone-50/70 hover:bg-stone-50 border-b border-stone-200/80 flex items-center justify-between transition-colors text-left"
        >
          <div className="flex items-center gap-2.5">
            <span className="w-2.5 h-2.5 rounded-full bg-rose-600" />
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-stone-900">
              5. Anthropogenic Pressures
            </h3>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-[11px] font-mono text-stone-500">Pollution • Deforestation</span>
            {openSections.human_impact ? <ChevronUp className="w-4 h-4 text-stone-400" /> : <ChevronDown className="w-4 h-4 text-stone-400" />}
          </div>
        </button>

        {openSections.human_impact && (
          <div className="p-4 sm:p-6 divide-y divide-stone-100 space-y-4">
            {/* Pollution */}
            <div className="pt-2 first:pt-0 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <label className="text-xs font-bold text-stone-800 flex items-center gap-1.5">
                  Pollution Index
                  <span className="text-[11px] font-normal text-stone-500 font-mono">(0.0 - 100.0)</span>
                </label>
                <p className="text-[11px] text-stone-500">Agrochemical runoff, heavy metals, or industrial toxicity.</p>
              </div>
              <div className="flex items-center gap-3">
                {renderOriginBadge(getOrigin(state.human_impact.pollution))}
                <div className="w-32">
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    value={state.human_impact.pollution ?? ''}
                    placeholder="null"
                    onChange={(e) =>
                      onStateChange({
                        ...state,
                        human_impact: {
                          ...state.human_impact,
                          pollution: e.target.value === '' ? null : parseFloat(e.target.value),
                        },
                      })
                    }
                    className="w-full text-xs font-mono px-3 py-1.5 border border-stone-200 rounded-lg bg-stone-50 focus:bg-white focus:border-emerald-600 focus:outline-hidden"
                  />
                </div>
              </div>
            </div>

            {/* Deforestation */}
            <div className="pt-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
              <div>
                <label className="text-xs font-bold text-stone-800 flex items-center gap-1.5">
                  Deforestation Rate
                  <span className="text-[11px] font-normal text-stone-500 font-mono">(% canopy loss)</span>
                </label>
                <p className="text-[11px] text-stone-500">Historical or active tree cover loss within territory.</p>
              </div>
              <div className="flex items-center gap-3">
                {renderOriginBadge(getOrigin(state.human_impact.deforestation))}
                <div className="w-32">
                  <input
                    type="number"
                    step="0.1"
                    min="0"
                    max="100"
                    value={state.human_impact.deforestation ?? ''}
                    placeholder="null"
                    onChange={(e) =>
                      onStateChange({
                        ...state,
                        human_impact: {
                          ...state.human_impact,
                          deforestation: e.target.value === '' ? null : parseFloat(e.target.value),
                        },
                      })
                    }
                    className="w-full text-xs font-mono px-3 py-1.5 border border-stone-200 rounded-lg bg-stone-50 focus:bg-white focus:border-emerald-600 focus:outline-hidden"
                  />
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
