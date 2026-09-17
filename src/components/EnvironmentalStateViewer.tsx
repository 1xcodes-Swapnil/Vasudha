/**
 * Phase 1: Canonical Environmental State Interactive Inspector & Validator
 *
 * Provides live testing of:
 * - Soil (pH, organic carbon %, moisture %)
 * - Land (land use, land cover)
 * - Biodiversity (species richness, habitat diversity index)
 * - Climate (temperature °C, rainfall mm)
 * - Human Impact (pollution, deforestation %)
 * - Spatial Context (latitude, longitude, region, ecosystem)
 *
 * Implements strict scientific validation, null vs zero preservation, and live API connectivity.
 */

import React, { useState, useEffect } from 'react';
import { Sprout, Check, AlertCircle, RefreshCw, Layers, ArrowUpRight } from 'lucide-react';
import {
  EnvironmentalState,
  EnvironmentalProfileResponse,
} from '../types';
import {
  validateEnvironmentalState,
  createEnvironmentalProfile,
  updateEnvironmentalProfile,
  listEnvironmentalProfiles,
} from '../services/api';

const DEFAULT_EXAMPLE_STATE: EnvironmentalState = {
  soil: {
    ph: 6.5,
    organic_carbon: 3.2,
    moisture: 22.0,
  },
  land: {
    land_use: 'agroforestry',
    land_cover: 'tropical_dry_deciduous',
  },
  biodiversity: {
    species_richness: 84,
    habitat_diversity: 65.0,
  },
  climate: {
    temperature: 24.5,
    rainfall: 1100.0,
  },
  human_impact: {
    pollution: 8.5,
    deforestation: 12.0,
  },
  spatial_context: {
    latitude: 12.9716,
    longitude: 77.5946,
    region: 'Deccan Plateau',
    ecosystem: 'Tropical Dry Forest',
  },
};

interface EnvironmentalStateViewerProps {
  state?: EnvironmentalState;
  onStateChange?: (newState: EnvironmentalState) => void;
}

export const EnvironmentalStateViewer: React.FC<EnvironmentalStateViewerProps> = ({
  state,
  onStateChange,
}) => {
  const [internalState, setInternalState] = useState<EnvironmentalState>(DEFAULT_EXAMPLE_STATE);
  const currentState = state || internalState;

  const setCurrentState = (newState: EnvironmentalState | ((prev: EnvironmentalState) => EnvironmentalState)) => {
    if (typeof newState === 'function') {
      const computed = newState(currentState);
      if (onStateChange) {
        onStateChange(computed);
      } else {
        setInternalState(computed);
      }
    } else {
      if (onStateChange) {
        onStateChange(newState);
      } else {
        setInternalState(newState);
      }
    }
  };
  const [profileName, setProfileName] = useState<string>('Deccan Agroforestry Site A');
  const [activeProfileId, setActiveProfileId] = useState<string | null>(null);
  const [validationResult, setValidationResult] = useState<{
    valid: boolean;
    metrics_count: number;
    is_empty: boolean;
  } | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [recentProfiles, setRecentProfiles] = useState<EnvironmentalProfileResponse[]>([]);

  // Validate on change
  const handleValidate = async () => {
    setErrorMsg(null);
    try {
      const res = await validateEnvironmentalState(currentState);
      setValidationResult(res);
      setSuccessMsg(`Validation successful: ${res.metrics_count} scientific metrics verified.`);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Validation failed');
      setValidationResult(null);
    }
  };

  // Load profiles on mount
  useEffect(() => {
    listEnvironmentalProfiles()
      .then((items) => setRecentProfiles(items))
      .catch(() => {});
  }, []);

  const handleSaveProfile = async () => {
    setLoading(true);
    setErrorMsg(null);
    setSuccessMsg(null);
    try {
      const created = await createEnvironmentalProfile({
        name: profileName,
        description: 'Observation captured via Phase 1 canonical state interface',
        state: currentState,
      });
      setActiveProfileId(created.id);
      setSuccessMsg(`Profile saved successfully with ID: ${created.id.slice(0, 8)}... (${created.metrics_count} metrics)`);
      const updatedList = await listEnvironmentalProfiles();
      setRecentProfiles(updatedList);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Save failed');
    } finally {
      setLoading(false);
    }
  };

  const handleApplyPartialPatch = async () => {
    if (!activeProfileId) {
      setErrorMsg('Please save or select an existing profile first to apply a patch.');
      return;
    }
    setLoading(true);
    setErrorMsg(null);
    try {
      // Simulate partial update with an observed zero rainfall and updated pH
      const patch = {
        climate: { rainfall: 0.0 }, // explicit observed zero
        soil: { ph: 7.1 },
      };
      const updated = await updateEnvironmentalProfile(activeProfileId, patch);
      setCurrentState(updated.state);
      setSuccessMsg(`Applied partial patch (Rainfall: 0.0 mm [observed zero], Soil pH: 7.1). Older fields retained!`);
    } catch (err) {
      setErrorMsg(err instanceof Error ? err.message : 'Patch failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white border border-stone-200 rounded-sm p-6 shadow-xs space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-stone-100 gap-3">
        <div>
          <div className="flex items-center gap-2">
            <Sprout className="w-4 h-4 text-emerald-700" />
            <h2 className="text-sm font-semibold uppercase tracking-wider text-stone-800">
              Canonical Environmental State & Data Model (Phase 1)
            </h2>
          </div>
          <p className="text-xs text-stone-500 mt-0.5">
            Structured, validated multi-metric ecological foundation. Distinguishes null (unknown) from 0 (observed zero).
          </p>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-xs font-mono px-2 py-0.5 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-sm">
            Phase 1 Active
          </span>
        </div>
      </div>

      {/* Messages */}
      {errorMsg && (
        <div className="flex items-start gap-2 p-3 bg-rose-50 border border-rose-200 text-rose-800 rounded-xs text-xs">
          <AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}
      {successMsg && (
        <div className="flex items-start gap-2 p-3 bg-emerald-50 border border-emerald-200 text-emerald-800 rounded-xs text-xs">
          <Check className="w-4 h-4 mt-0.5 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {/* Profile Form & Data Entry Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-xs">
        {/* Soil Metrics */}
        <div className="border border-stone-200 rounded-sm p-4 bg-stone-50/60">
          <h3 className="font-semibold text-stone-800 uppercase tracking-wider text-[11px] mb-3 flex items-center justify-between">
            <span>1. Soil Metrics</span>
            <span className="text-stone-400 font-mono">0.0 - 14.0 pH</span>
          </h3>
          <div className="space-y-3">
            <div>
              <label className="block text-stone-600 mb-1">pH (0.0 to 14.0):</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="14"
                value={currentState.soil.ph ?? ''}
                onChange={(e) =>
                  setCurrentState({
                    ...currentState,
                    soil: { ...currentState.soil, ph: e.target.value === '' ? null : parseFloat(e.target.value) },
                  })
                }
                className="w-full px-2.5 py-1.5 bg-white border border-stone-300 rounded-xs font-mono text-stone-800 focus:outline-none focus:border-stone-500"
                placeholder="null (unknown)"
              />
            </div>
            <div>
              <label className="block text-stone-600 mb-1">Organic Carbon (% wt):</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="100"
                value={currentState.soil.organic_carbon ?? ''}
                onChange={(e) =>
                  setCurrentState({
                    ...currentState,
                    soil: { ...currentState.soil, organic_carbon: e.target.value === '' ? null : parseFloat(e.target.value) },
                  })
                }
                className="w-full px-2.5 py-1.5 bg-white border border-stone-300 rounded-xs font-mono text-stone-800 focus:outline-none focus:border-stone-500"
                placeholder="null (unknown)"
              />
            </div>
            <div>
              <label className="block text-stone-600 mb-1">Moisture (% vol):</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="100"
                value={currentState.soil.moisture ?? ''}
                onChange={(e) =>
                  setCurrentState({
                    ...currentState,
                    soil: { ...currentState.soil, moisture: e.target.value === '' ? null : parseFloat(e.target.value) },
                  })
                }
                className="w-full px-2.5 py-1.5 bg-white border border-stone-300 rounded-xs font-mono text-stone-800 focus:outline-none focus:border-stone-500"
                placeholder="null (unknown)"
              />
            </div>
          </div>
        </div>

        {/* Climate Metrics */}
        <div className="border border-stone-200 rounded-sm p-4 bg-stone-50/60">
          <h3 className="font-semibold text-stone-800 uppercase tracking-wider text-[11px] mb-3 flex items-center justify-between">
            <span>2. Climate Metrics</span>
            <span className="text-stone-400 font-mono">°C & mm/yr</span>
          </h3>
          <div className="space-y-3">
            <div>
              <label className="block text-stone-600 mb-1">Temperature (°C):</label>
              <input
                type="number"
                step="0.1"
                min="-90"
                max="60"
                value={currentState.climate.temperature ?? ''}
                onChange={(e) =>
                  setCurrentState({
                    ...currentState,
                    climate: { ...currentState.climate, temperature: e.target.value === '' ? null : parseFloat(e.target.value) },
                  })
                }
                className="w-full px-2.5 py-1.5 bg-white border border-stone-300 rounded-xs font-mono text-stone-800 focus:outline-none focus:border-stone-500"
                placeholder="null (unknown)"
              />
            </div>
            <div>
              <label className="block text-stone-600 mb-1">Rainfall (mm/year):</label>
              <input
                type="number"
                step="10"
                min="0"
                max="20000"
                value={currentState.climate.rainfall ?? ''}
                onChange={(e) =>
                  setCurrentState({
                    ...currentState,
                    climate: { ...currentState.climate, rainfall: e.target.value === '' ? null : parseFloat(e.target.value) },
                  })
                }
                className="w-full px-2.5 py-1.5 bg-white border border-stone-300 rounded-xs font-mono text-stone-800 focus:outline-none focus:border-stone-500"
                placeholder="null (unknown)"
              />
            </div>
          </div>
        </div>

        {/* Biodiversity & Human Impact */}
        <div className="border border-stone-200 rounded-sm p-4 bg-stone-50/60">
          <h3 className="font-semibold text-stone-800 uppercase tracking-wider text-[11px] mb-3 flex items-center justify-between">
            <span>3. Biodiversity & Impact</span>
            <span className="text-stone-400 font-mono">Counts & Indices</span>
          </h3>
          <div className="space-y-3">
            <div>
              <label className="block text-stone-600 mb-1">Species Richness (count):</label>
              <input
                type="number"
                min="0"
                value={currentState.biodiversity.species_richness ?? ''}
                onChange={(e) =>
                  setCurrentState({
                    ...currentState,
                    biodiversity: {
                      ...currentState.biodiversity,
                      species_richness: e.target.value === '' ? null : parseInt(e.target.value, 10),
                    },
                  })
                }
                className="w-full px-2.5 py-1.5 bg-white border border-stone-300 rounded-xs font-mono text-stone-800 focus:outline-none focus:border-stone-500"
                placeholder="null (unknown)"
              />
            </div>
            <div>
              <label className="block text-stone-600 mb-1">Deforestation (% loss):</label>
              <input
                type="number"
                step="0.1"
                min="0"
                max="100"
                value={currentState.human_impact.deforestation ?? ''}
                onChange={(e) =>
                  setCurrentState({
                    ...currentState,
                    human_impact: {
                      ...currentState.human_impact,
                      deforestation: e.target.value === '' ? null : parseFloat(e.target.value),
                    },
                  })
                }
                className="w-full px-2.5 py-1.5 bg-white border border-stone-300 rounded-xs font-mono text-stone-800 focus:outline-none focus:border-stone-500"
                placeholder="null (unknown)"
              />
            </div>
          </div>
        </div>

        {/* Land Use & Cover */}
        <div className="border border-stone-200 rounded-sm p-4 bg-stone-50/60">
          <h3 className="font-semibold text-stone-800 uppercase tracking-wider text-[11px] mb-3 flex items-center justify-between">
            <span>4. Land Classification</span>
            <span className="text-stone-400 font-mono">Use & Cover</span>
          </h3>
          <div className="space-y-3">
            <div>
              <label className="block text-stone-600 mb-1">Land Use:</label>
              <input
                type="text"
                value={currentState.land.land_use ?? ''}
                onChange={(e) =>
                  setCurrentState({
                    ...currentState,
                    land: { ...currentState.land, land_use: e.target.value || null },
                  })
                }
                className="w-full px-2.5 py-1.5 bg-white border border-stone-300 rounded-xs font-mono text-stone-800 focus:outline-none focus:border-stone-500"
                placeholder="e.g. agroforestry, pasture"
              />
            </div>
            <div>
              <label className="block text-stone-600 mb-1">Land Cover:</label>
              <input
                type="text"
                value={currentState.land.land_cover ?? ''}
                onChange={(e) =>
                  setCurrentState({
                    ...currentState,
                    land: { ...currentState.land, land_cover: e.target.value || null },
                  })
                }
                className="w-full px-2.5 py-1.5 bg-white border border-stone-300 rounded-xs font-mono text-stone-800 focus:outline-none focus:border-stone-500"
                placeholder="e.g. tropical_forest, wetland"
              />
            </div>
          </div>
        </div>

        {/* Spatial Context */}
        <div className="border border-stone-200 rounded-sm p-4 bg-stone-50/60 md:col-span-2">
          <h3 className="font-semibold text-stone-800 uppercase tracking-wider text-[11px] mb-3 flex items-center justify-between">
            <span>5. Spatial Context & Coordinates</span>
            <span className="text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-xs border border-emerald-200 text-[10px] font-mono">Linked to Geo Map</span>
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div>
              <label className="block text-stone-600 mb-1">Latitude:</label>
              <input
                type="number"
                step="0.0001"
                min="-90"
                max="90"
                value={currentState.spatial_context.latitude ?? ''}
                onChange={(e) =>
                  setCurrentState({
                    ...currentState,
                    spatial_context: {
                      ...currentState.spatial_context,
                      latitude: e.target.value === '' ? null : parseFloat(e.target.value),
                    },
                  })
                }
                className="w-full px-2.5 py-1.5 bg-white border border-stone-300 rounded-xs font-mono text-stone-800 focus:outline-none focus:border-stone-500"
                placeholder="-90.0 to 90.0"
              />
            </div>
            <div>
              <label className="block text-stone-600 mb-1">Longitude:</label>
              <input
                type="number"
                step="0.0001"
                min="-180"
                max="180"
                value={currentState.spatial_context.longitude ?? ''}
                onChange={(e) =>
                  setCurrentState({
                    ...currentState,
                    spatial_context: {
                      ...currentState.spatial_context,
                      longitude: e.target.value === '' ? null : parseFloat(e.target.value),
                    },
                  })
                }
                className="w-full px-2.5 py-1.5 bg-white border border-stone-300 rounded-xs font-mono text-stone-800 focus:outline-none focus:border-stone-500"
                placeholder="-180.0 to 180.0"
              />
            </div>
            <div>
              <label className="block text-stone-600 mb-1">Region:</label>
              <input
                type="text"
                value={currentState.spatial_context.region ?? ''}
                onChange={(e) =>
                  setCurrentState({
                    ...currentState,
                    spatial_context: { ...currentState.spatial_context, region: e.target.value || null },
                  })
                }
                className="w-full px-2.5 py-1.5 bg-white border border-stone-300 rounded-xs font-mono text-stone-800 focus:outline-none focus:border-stone-500"
                placeholder="e.g. Western Ghats"
              />
            </div>
            <div>
              <label className="block text-stone-600 mb-1">Ecosystem / Biome:</label>
              <input
                type="text"
                value={currentState.spatial_context.ecosystem ?? ''}
                onChange={(e) =>
                  setCurrentState({
                    ...currentState,
                    spatial_context: { ...currentState.spatial_context, ecosystem: e.target.value || null },
                  })
                }
                className="w-full px-2.5 py-1.5 bg-white border border-stone-300 rounded-xs font-mono text-stone-800 focus:outline-none focus:border-stone-500"
                placeholder="e.g. Tropical Moist Forest"
              />
            </div>
          </div>
        </div>
      </div>

      {/* Action Controls */}
      <div className="flex flex-wrap items-center justify-between gap-3 pt-3 border-t border-stone-100">
        <div className="flex items-center gap-2">
          <input
            type="text"
            value={profileName}
            onChange={(e) => setProfileName(e.target.value)}
            className="px-2.5 py-1.5 bg-stone-50 border border-stone-300 rounded-xs text-xs text-stone-800 font-mono w-64"
            placeholder="Profile / Site Name"
          />
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={handleValidate}
            className="px-3 py-1.5 text-xs font-semibold bg-stone-100 hover:bg-stone-200 text-stone-800 border border-stone-300 rounded-xs flex items-center gap-1.5 transition-colors"
          >
            <Check className="w-3.5 h-3.5 text-stone-600" />
            Validate Schema
          </button>

          <button
            type="button"
            onClick={handleSaveProfile}
            disabled={loading}
            className="px-3.5 py-1.5 text-xs font-semibold bg-emerald-800 hover:bg-emerald-900 text-white rounded-xs flex items-center gap-1.5 transition-colors disabled:opacity-50"
          >
            <Layers className="w-3.5 h-3.5" />
            {loading ? 'Saving...' : 'Persist Profile to DB'}
          </button>

          <button
            type="button"
            onClick={handleApplyPartialPatch}
            disabled={loading || !activeProfileId}
            title={activeProfileId ? 'Test partial patch merge rule' : 'Save profile first'}
            className="px-3 py-1.5 text-xs font-semibold bg-stone-800 hover:bg-stone-900 text-white rounded-xs flex items-center gap-1.5 transition-colors disabled:opacity-40"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            Test Partial Patch (0.0 mm rain)
          </button>
        </div>
      </div>

      {/* Profile History / Stored Profiles */}
      {recentProfiles.length > 0 && (
        <div className="border-t border-stone-100 pt-4">
          <h4 className="text-[11px] font-semibold uppercase tracking-wider text-stone-500 mb-2 font-mono">
            Persisted Environmental Profiles ({recentProfiles.length})
          </h4>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
            {recentProfiles.slice(0, 3).map((p) => (
              <div
                key={p.id}
                onClick={() => {
                  setActiveProfileId(p.id);
                  setCurrentState(p.state);
                  setProfileName(p.name || 'Unnamed');
                  setSuccessMsg(`Loaded profile: ${p.name || p.id.slice(0, 8)}`);
                }}
                className={`p-2.5 rounded-xs border text-xs cursor-pointer transition-colors ${
                  activeProfileId === p.id
                    ? 'border-emerald-600 bg-emerald-50/40 text-stone-900'
                    : 'border-stone-200 bg-stone-50/40 hover:bg-stone-100 text-stone-700'
                }`}
              >
                <div className="font-semibold flex items-center justify-between">
                  <span>{p.name || 'Observation'}</span>
                  <span className="text-[10px] font-mono text-stone-400">{p.metrics_count} metrics</span>
                </div>
                <div className="text-[11px] text-stone-500 font-mono mt-1">
                  ID: {p.id.slice(0, 8)}... • pH: {p.state.soil.ph ?? 'null'} • Rain: {p.state.climate.rainfall ?? 'null'}mm
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
