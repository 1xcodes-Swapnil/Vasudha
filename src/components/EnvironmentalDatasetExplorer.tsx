import React, { useState, useEffect } from 'react';
import {
  Database,
  CheckCircle2,
  AlertTriangle,
  ExternalLink,
  ShieldCheck,
  RefreshCw,
  Compass,
  FileCheck2,
  Info,
  Layers,
  ArrowRight,
  Filter,
  Sparkles,
  HelpCircle,
} from 'lucide-react';
import {
  DatasetMetadata,
  VariableProvenance,
  DataQualityReport,
  PointQueryResult,
  EnvironmentalState,
  DataQualityCheck,
} from '../types';
import {
  fetchDatasetRegistry,
  queryAuthoritativeDatasets,
  enrichEnvironmentalState,
} from '../services/api';

interface EnvironmentalDatasetExplorerProps {
  currentState: EnvironmentalState;
  onStateEnriched?: (newState: EnvironmentalState) => void;
}

export const EnvironmentalDatasetExplorer: React.FC<EnvironmentalDatasetExplorerProps> = ({
  currentState,
  onStateEnriched,
}) => {
  const [datasets, setDatasets] = useState<DatasetMetadata[]>([]);
  const [loadingDatasets, setLoadingDatasets] = useState(false);
  const [activeTab, setActiveTab] = useState<'registry' | 'point_query' | 'provenance' | 'quality_audit'>('point_query');

  // Point query state
  const [lat, setLat] = useState<number>(currentState.spatial_context.latitude || 10.53);
  const [lon, setLon] = useState<number>(currentState.spatial_context.longitude || 76.21);
  const [allowSynthetic, setAllowSynthetic] = useState(false);
  const [queryLoading, setQueryLoading] = useState(false);
  const [queryResult, setQueryResult] = useState<PointQueryResult | null>(null);
  const [enrichLoading, setEnrichLoading] = useState(false);
  const [enrichSuccessMsg, setEnrichSuccessMsg] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [selectedDatasetId, setSelectedDatasetId] = useState<string | null>(null);

  // Filter for provenance
  const [provDomainFilter, setProvDomainFilter] = useState<string>('all');

  useEffect(() => {
    loadRegistry();
  }, []);

  const loadRegistry = async () => {
    setLoadingDatasets(true);
    try {
      const data = await fetchDatasetRegistry();
      setDatasets(data);
    } catch (err: any) {
      console.error('Failed to load dataset registry:', err);
    } finally {
      setLoadingDatasets(false);
    }
  };

  const handleRunPointQuery = async (queryLat: number, queryLon: number) => {
    setQueryLoading(true);
    setErrorMsg(null);
    setEnrichSuccessMsg(null);
    try {
      const result = await queryAuthoritativeDatasets(queryLat, queryLon, allowSynthetic);
      setQueryResult(result);
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to query authoritative datasets');
    } finally {
      setQueryLoading(false);
    }
  };

  const handleEnrichState = async (overwrite: boolean = false) => {
    setEnrichLoading(true);
    setErrorMsg(null);
    setEnrichSuccessMsg(null);
    try {
      const resp = await enrichEnvironmentalState({
        state: currentState,
        latitude: lat,
        longitude: lon,
        overwrite_existing: overwrite,
        allow_synthetic_fallback: allowSynthetic,
      });

      if (onStateEnriched) {
        onStateEnriched(resp.enriched_state);
      }
      setEnrichSuccessMsg(
        `Successfully enriched Environmental State: ${resp.metrics_added_count} metrics filled from authoritative sources (${resp.metrics_preserved_count} user values preserved).`
      );
    } catch (err: any) {
      setErrorMsg(err.message || 'Failed to enrich environmental state');
    } finally {
      setEnrichLoading(false);
    }
  };

  const presetLocations = [
    { name: 'Western Ghats Moist Deciduous', lat: 10.53, lon: 76.21 },
    { name: 'Amazon Basin Tropical Forest', lat: -3.46, lon: -62.21 },
    { name: 'Serengeti Acacia Savanna', lat: -2.33, lon: 34.83 },
    { name: 'Fennoscandia Boreal Taiga', lat: 64.18, lon: 17.55 },
    { name: 'Mediterranean Sclerophyllous Scrub', lat: 38.72, lon: -9.13 },
    { name: 'Atacama Hyper-Arid Desert', lat: -23.86, lon: -69.13 },
  ];

  return (
    <div id="environmental-dataset-explorer" className="space-y-6">
      {/* Top Header Card */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <span className="px-2.5 py-0.5 rounded text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Phase 7 Layer
              </span>
              <span className="text-xs text-slate-400 font-mono">Scientific Environmental Datasets</span>
            </div>
            <h2 className="text-xl font-bold text-slate-100 mt-2 flex items-center gap-2">
              <Database className="w-6 h-6 text-emerald-400" />
              Authoritative Environmental Dataset Layer
            </h2>
            <p className="text-sm text-slate-400 mt-1 max-w-3xl">
              Traceable, multi-domain environmental data ingestion from ISRIC SoilGrids, ESA Copernicus WorldCover,
              GBIF, WorldClim v2.1, Global Forest Watch (Hansen GFC), and UNEP/SEDAC. All variables feature explicit
              unit normalization, scientific provenance, and strict zero vs. null auditing.
            </p>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => handleRunPointQuery(lat, lon)}
              disabled={queryLoading}
              className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-sm font-medium rounded-lg flex items-center gap-2 transition"
            >
              <RefreshCw className={`w-4 h-4 ${queryLoading ? 'animate-spin' : ''}`} />
              Fetch Real-World Data
            </button>
          </div>
        </div>

        {/* Navigation Tabs */}
        <div className="flex border-b border-slate-800 mt-6 -mb-2 space-x-6">
          <button
            onClick={() => setActiveTab('point_query')}
            className={`pb-3 text-sm font-medium flex items-center gap-2 border-b-2 transition ${
              activeTab === 'point_query'
                ? 'border-emerald-500 text-emerald-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Compass className="w-4 h-4" />
            Point Query & State Enrichment
          </button>
          <button
            onClick={() => setActiveTab('provenance')}
            className={`pb-3 text-sm font-medium flex items-center gap-2 border-b-2 transition ${
              activeTab === 'provenance'
                ? 'border-emerald-500 text-emerald-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <ShieldCheck className="w-4 h-4" />
            Variable Provenance ({queryResult ? Object.keys(queryResult.provenance_records).length : 0})
          </button>
          <button
            onClick={() => setActiveTab('quality_audit')}
            className={`pb-3 text-sm font-medium flex items-center gap-2 border-b-2 transition ${
              activeTab === 'quality_audit'
                ? 'border-emerald-500 text-emerald-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <FileCheck2 className="w-4 h-4" />
            Data Quality Audit & Normalization
          </button>
          <button
            onClick={() => setActiveTab('registry')}
            className={`pb-3 text-sm font-medium flex items-center gap-2 border-b-2 transition ${
              activeTab === 'registry'
                ? 'border-emerald-500 text-emerald-400'
                : 'border-transparent text-slate-400 hover:text-slate-200'
            }`}
          >
            <Layers className="w-4 h-4" />
            Authoritative Dataset Registry ({datasets.length})
          </button>
        </div>
      </div>

      {/* Messages */}
      {errorMsg && (
        <div className="p-4 bg-rose-950/40 border border-rose-800 rounded-xl text-rose-300 text-sm flex items-center gap-3">
          <AlertTriangle className="w-5 h-5 flex-shrink-0 text-rose-400" />
          <span>{errorMsg}</span>
        </div>
      )}
      {enrichSuccessMsg && (
        <div className="p-4 bg-emerald-950/40 border border-emerald-800 rounded-xl text-emerald-300 text-sm flex items-center gap-3">
          <CheckCircle2 className="w-5 h-5 flex-shrink-0 text-emerald-400" />
          <span>{enrichSuccessMsg}</span>
        </div>
      )}

      {/* Tab 1: Point Query & Enrichment */}
      {activeTab === 'point_query' && (
        <div className="space-y-6">
          {/* Coordinates & Preset Selector */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-5 space-y-4">
            <h3 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center gap-2">
              <Compass className="w-4 h-4 text-emerald-400" />
              Target Coordinate Point
            </h3>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div>
                <label className="block text-xs text-slate-400 mb-1">Latitude (°N/S)</label>
                <input
                  type="number"
                  step="0.01"
                  min="-90"
                  max="90"
                  value={lat}
                  onChange={(e) => setLat(parseFloat(e.target.value) || 0)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div>
                <label className="block text-xs text-slate-400 mb-1">Longitude (°E/W)</label>
                <input
                  type="number"
                  step="0.01"
                  min="-180"
                  max="180"
                  value={lon}
                  onChange={(e) => setLon(parseFloat(e.target.value) || 0)}
                  className="w-full bg-slate-800 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 text-sm focus:outline-none focus:border-emerald-500"
                />
              </div>
              <div className="flex items-center gap-2 pt-6">
                <input
                  type="checkbox"
                  id="allowSynthetic"
                  checked={allowSynthetic}
                  onChange={(e) => setAllowSynthetic(e.target.checked)}
                  className="w-4 h-4 text-emerald-600 rounded bg-slate-800 border-slate-700 focus:ring-emerald-500"
                />
                <label htmlFor="allowSynthetic" className="text-xs text-slate-300">
                  Allow Synthetic Fallback if unmapped
                </label>
              </div>
              <div className="flex items-center gap-2 pt-5">
                <button
                  onClick={() => handleRunPointQuery(lat, lon)}
                  disabled={queryLoading}
                  className="w-full px-4 py-2 bg-emerald-600 hover:bg-emerald-500 disabled:opacity-50 text-white text-sm font-semibold rounded-lg flex items-center justify-center gap-2 transition"
                >
                  <RefreshCw className={`w-4 h-4 ${queryLoading ? 'animate-spin' : ''}`} />
                  Query Datasets
                </button>
              </div>
            </div>

            {/* Presets */}
            <div>
              <span className="text-xs text-slate-400 block mb-2">Preset Biomes for Grounded Validation:</span>
              <div className="flex flex-wrap gap-2">
                {presetLocations.map((p) => (
                  <button
                    key={p.name}
                    onClick={() => {
                      setLat(p.lat);
                      setLon(p.lon);
                      handleRunPointQuery(p.lat, p.lon);
                    }}
                    className="px-2.5 py-1 text-xs bg-slate-800 hover:bg-slate-700 border border-slate-700 rounded-md text-slate-300 transition flex items-center gap-1.5"
                  >
                    <span>{p.name}</span>
                    <span className="text-slate-500 font-mono text-[10px]">({p.lat}, {p.lon})</span>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Point Query Results Card */}
          {queryResult && (
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="text-lg font-bold text-slate-100">
                      Authoritative Point Observation ({queryResult.latitude}°, {queryResult.longitude}°)
                    </h3>
                    {queryResult.is_fully_authoritative ? (
                      <span className="px-2 py-0.5 text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 rounded flex items-center gap-1">
                        <ShieldCheck className="w-3.5 h-3.5" /> Fully Authoritative
                      </span>
                    ) : (
                      <span className="px-2 py-0.5 text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30 rounded flex items-center gap-1">
                        <AlertTriangle className="w-3.5 h-3.5" /> Contains Synthetic Fallback
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-slate-400 mt-1">
                    Region: <strong className="text-slate-300">{queryResult.canonical_state.spatial_context.region || 'Unknown'}</strong> | Biome: <strong className="text-slate-300">{queryResult.canonical_state.spatial_context.ecosystem || 'Unknown'}</strong>
                  </p>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={() => handleEnrichState(false)}
                    disabled={enrichLoading}
                    className="px-3.5 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 text-xs font-medium rounded-lg flex items-center gap-1.5 transition"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
                    Enrich State (Preserve User Inputs)
                  </button>
                  <button
                    onClick={() => handleEnrichState(true)}
                    disabled={enrichLoading}
                    className="px-3.5 py-2 bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-medium rounded-lg flex items-center gap-1.5 transition"
                  >
                    <ArrowRight className="w-3.5 h-3.5" />
                    Overwrite All with Dataset
                  </button>
                </div>
              </div>

              {/* Multi-Domain Metric Grid */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Soil */}
                <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-4 space-y-2">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    <span>Soil Properties</span>
                    <span className="text-[10px] text-emerald-400 font-mono">ISRIC SoilGrids</span>
                  </div>
                  <div className="text-sm text-slate-200 space-y-1">
                    <div className="flex justify-between">
                      <span className="text-slate-400">pH:</span>
                      <span className="font-semibold font-mono">{queryResult.canonical_state.soil.ph ?? 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Organic Carbon (SOC):</span>
                      <span className="font-semibold font-mono">{queryResult.canonical_state.soil.organic_carbon ? `${queryResult.canonical_state.soil.organic_carbon}%` : 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Moisture Content:</span>
                      <span className="font-semibold font-mono">{queryResult.canonical_state.soil.moisture ? `${queryResult.canonical_state.soil.moisture}%` : 'N/A'}</span>
                    </div>
                  </div>
                </div>

                {/* Land */}
                <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-4 space-y-2">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    <span>Land Cover & Use</span>
                    <span className="text-[10px] text-emerald-400 font-mono">ESA Copernicus</span>
                  </div>
                  <div className="text-sm text-slate-200 space-y-1">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Land Cover:</span>
                      <span className="font-semibold capitalize">{queryResult.canonical_state.land.land_cover ?? 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Land Use:</span>
                      <span className="font-semibold capitalize">{queryResult.canonical_state.land.land_use ?? 'N/A'}</span>
                    </div>
                  </div>
                </div>

                {/* Biodiversity */}
                <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-4 space-y-2">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    <span>Biodiversity</span>
                    <span className="text-[10px] text-emerald-400 font-mono">GBIF Occurrence</span>
                  </div>
                  <div className="text-sm text-slate-200 space-y-1">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Species Richness:</span>
                      <span className="font-semibold font-mono">{queryResult.canonical_state.biodiversity.species_richness ?? 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Habitat Diversity Index:</span>
                      <span className="font-semibold font-mono">{queryResult.canonical_state.biodiversity.habitat_diversity ?? 'N/A'}</span>
                    </div>
                  </div>
                </div>

                {/* Climate */}
                <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-4 space-y-2">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    <span>Climate & Precipitation</span>
                    <span className="text-[10px] text-emerald-400 font-mono">WorldClim v2.1</span>
                  </div>
                  <div className="text-sm text-slate-200 space-y-1">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Annual Mean Temp:</span>
                      <span className="font-semibold font-mono">{queryResult.canonical_state.climate.temperature ? `${queryResult.canonical_state.climate.temperature}°C` : 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Annual Rainfall:</span>
                      <span className="font-semibold font-mono">{queryResult.canonical_state.climate.rainfall ? `${queryResult.canonical_state.climate.rainfall} mm` : 'N/A'}</span>
                    </div>
                  </div>
                </div>

                {/* Human Impact */}
                <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-4 space-y-2">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    <span>Human Disturbance</span>
                    <span className="text-[10px] text-emerald-400 font-mono">GFW & UNEP</span>
                  </div>
                  <div className="text-sm text-slate-200 space-y-1">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Deforestation Loss:</span>
                      <span className="font-semibold font-mono">{queryResult.canonical_state.human_impact.deforestation !== null && queryResult.canonical_state.human_impact.deforestation !== undefined ? `${queryResult.canonical_state.human_impact.deforestation}%` : 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Pollution Index:</span>
                      <span className="font-semibold font-mono">{queryResult.canonical_state.human_impact.pollution !== null && queryResult.canonical_state.human_impact.pollution !== undefined ? queryResult.canonical_state.human_impact.pollution : 'N/A'}</span>
                    </div>
                  </div>
                </div>

                {/* Quality Summary card */}
                <div className="bg-slate-950/60 border border-slate-800/80 rounded-lg p-4 space-y-2">
                  <div className="flex items-center justify-between text-xs font-semibold text-slate-400 uppercase tracking-wider">
                    <span>Quality Audit</span>
                    <span className="text-[10px] text-emerald-400 font-mono">Validation Engine</span>
                  </div>
                  <div className="text-sm text-slate-200 space-y-1">
                    <div className="flex justify-between">
                      <span className="text-slate-400">Passed Checks:</span>
                      <span className="font-semibold text-emerald-400">{queryResult.quality_report.passed_checks}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Warnings:</span>
                      <span className="font-semibold text-amber-400">{queryResult.quality_report.warnings_count}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-slate-400">Observed 0.0 Variables:</span>
                      <span className="font-semibold text-slate-300">{queryResult.quality_report.zero_variables.length}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Tab 2: Variable Provenance Records */}
      {activeTab === 'provenance' && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
                Variable-Level Scientific Provenance
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Every extracted metric maintains complete attribution, original raw units, transformation rules, licensing, and spatial resolution.
              </p>
            </div>

            {/* Filter */}
            <div className="flex items-center gap-2">
              <Filter className="w-4 h-4 text-slate-400" />
              <select
                value={provDomainFilter}
                onChange={(e) => setProvDomainFilter(e.target.value)}
                className="bg-slate-800 border border-slate-700 text-xs text-slate-300 rounded-lg px-2.5 py-1.5 focus:outline-none focus:border-emerald-500"
              >
                <option value="all">All Domains</option>
                <option value="soil">Soil</option>
                <option value="land">Land</option>
                <option value="biodiversity">Biodiversity</option>
                <option value="climate">Climate</option>
                <option value="human_impact">Human Impact</option>
              </select>
            </div>
          </div>

          {!queryResult || Object.keys(queryResult.provenance_records).length === 0 ? (
            <div className="text-center py-12 text-slate-500 text-sm">
              <Info className="w-8 h-8 mx-auto mb-2 text-slate-600" />
              No point query has been run yet. Use the "Point Query & State Enrichment" tab to fetch provenance.
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {(Object.entries(queryResult.provenance_records) as [string, VariableProvenance][])
                .filter(([varKey]) => provDomainFilter === 'all' || varKey.startsWith(provDomainFilter))
                .map(([varKey, prov]) => (
                  <div
                    key={varKey}
                    className="bg-slate-950/70 border border-slate-800 rounded-lg p-4 space-y-3"
                  >
                    <div className="flex items-start justify-between">
                      <div>
                        <span className="text-xs font-mono font-bold text-emerald-400">{prov.variable_name}</span>
                        <h4 className="text-sm font-semibold text-slate-200">{prov.dataset_name}</h4>
                        <p className="text-xs text-slate-400">{prov.source_organization}</p>
                      </div>
                      <span className="px-2 py-0.5 text-[10px] font-mono bg-slate-800 border border-slate-700 text-slate-300 rounded">
                        {prov.license}
                      </span>
                    </div>

                    <div className="grid grid-cols-2 gap-2 text-xs bg-slate-900/60 p-2.5 rounded border border-slate-800/80">
                      <div>
                        <span className="text-slate-500 block">Raw Measurement</span>
                        <span className="font-mono text-slate-300">{String(prov.raw_value)} {prov.raw_unit || ''}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">Canonical Harmonized</span>
                        <span className="font-mono text-emerald-300 font-semibold">{String(prov.canonical_value)} {prov.canonical_unit}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">Spatial Resolution</span>
                        <span className="text-slate-300">{prov.spatial_resolution}</span>
                      </div>
                      <div>
                        <span className="text-slate-500 block">Temporal Coverage</span>
                        <span className="text-slate-300">{prov.temporal_coverage}</span>
                      </div>
                    </div>

                    {prov.known_limitations && prov.known_limitations.length > 0 && (
                      <div className="text-[11px] text-slate-400 bg-amber-950/20 border border-amber-900/40 p-2 rounded">
                        <strong className="text-amber-400/90 font-medium">Limitations: </strong>
                        {prov.known_limitations[0]}
                      </div>
                    )}

                    <div className="flex items-center justify-between text-xs pt-1 border-t border-slate-800/80 text-slate-400">
                      <span>Source Reference:</span>
                      <a
                        href={prov.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-emerald-400 hover:text-emerald-300 flex items-center gap-1"
                      >
                        Dataset Portal <ExternalLink className="w-3 h-3" />
                      </a>
                    </div>
                  </div>
                ))}
            </div>
          )}
        </div>
      )}

      {/* Tab 3: Data Quality Audit */}
      {activeTab === 'quality_audit' && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
          <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-4 border-b border-slate-800">
            <div>
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <FileCheck2 className="w-5 h-5 text-emerald-400" />
                Data Quality Checks & Ingestion Audit
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Every record undergoes physical boundary verification, unit conversion logging, and explicit 0.0 vs null auditing.
              </p>
            </div>

            {queryResult && (
              <div className="flex items-center gap-4 text-xs font-mono">
                <span className="text-emerald-400">Passed: {queryResult.quality_report.passed_checks}</span>
                <span className="text-amber-400">Warnings: {queryResult.quality_report.warnings_count}</span>
                <span className="text-rose-400">Errors: {queryResult.quality_report.errors_count}</span>
              </div>
            )}
          </div>

          {!queryResult || queryResult.quality_report.checks.length === 0 ? (
            <div className="text-center py-12 text-slate-500 text-sm">
              <Info className="w-8 h-8 mx-auto mb-2 text-slate-600" />
              No ingestion audit logs generated yet. Run a point query to inspect validation checks.
            </div>
          ) : (
            <div className="space-y-3">
              {queryResult.quality_report.checks.map((check: DataQualityCheck, idx: number) => {
                let badgeColor = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
                if (check.severity === 'warning') {
                  badgeColor = 'bg-amber-500/10 text-amber-400 border-amber-500/20';
                } else if (check.severity === 'error') {
                  badgeColor = 'bg-rose-500/10 text-rose-400 border-rose-500/20';
                }

                return (
                  <div
                    key={`${check.metric_name}-${idx}`}
                    className="p-3 bg-slate-950/70 border border-slate-800 rounded-lg flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs"
                  >
                    <div className="flex items-start gap-2.5">
                      <span className={`px-2 py-0.5 rounded font-mono text-[10px] font-semibold border ${badgeColor}`}>
                        {check.flag_type}
                      </span>
                      <div>
                        <span className="font-mono font-semibold text-slate-300 block">{check.metric_name}</span>
                        <span className="text-slate-400">{check.message}</span>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 text-[11px] font-mono text-slate-400">
                      {check.original_value !== undefined && (
                        <span>Raw: <strong className="text-slate-300">{String(check.original_value)}</strong></span>
                      )}
                      {check.transformed_value !== undefined && (
                        <span>Harmonized: <strong className="text-emerald-400">{String(check.transformed_value)}</strong></span>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Tab 4: Authoritative Dataset Registry */}
      {activeTab === 'registry' && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 space-y-6">
          <div className="flex items-center justify-between pb-4 border-b border-slate-800">
            <div>
              <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
                <Layers className="w-5 h-5 text-emerald-400" />
                Authoritative Environmental Datasets ({datasets.length})
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">
                Standardized, peer-reviewed global scientific datasets integrated into the ecological knowledge pipeline.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {datasets.map((ds) => (
              <div
                key={ds.id}
                className="bg-slate-950 border border-slate-800 rounded-xl p-5 space-y-4 hover:border-slate-700 transition"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <span className="px-2 py-0.5 text-[10px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 rounded uppercase">
                      {ds.domain}
                    </span>
                    <h4 className="text-base font-bold text-slate-100 mt-1">{ds.name}</h4>
                    <p className="text-xs text-slate-400">{ds.source_organization}</p>
                  </div>
                  <span className="px-2 py-0.5 text-xs font-mono bg-slate-900 border border-slate-700 text-slate-300 rounded">
                    {ds.license}
                  </span>
                </div>

                {/* Variables & Units */}
                <div>
                  <span className="text-xs text-slate-500 block mb-1">Measured Variables & Harmonized Units:</span>
                  <div className="flex flex-wrap gap-1.5">
                    {ds.variables.map((v) => (
                      <span
                        key={v}
                        className="px-2 py-0.5 text-[11px] font-mono bg-slate-900 border border-slate-800 text-slate-300 rounded"
                      >
                        {v} ({ds.canonical_units[v] || 'canonical'})
                      </span>
                    ))}
                  </div>
                </div>

                {/* Coverage */}
                <div className="grid grid-cols-2 gap-2 text-xs text-slate-400 pt-2 border-t border-slate-900">
                  <div>
                    <span className="text-slate-500 block">Spatial Resolution</span>
                    <span>{ds.spatial_resolution}</span>
                  </div>
                  <div>
                    <span className="text-slate-500 block">Temporal Scope</span>
                    <span>{ds.temporal_coverage}</span>
                  </div>
                </div>

                {/* Limitations */}
                {ds.known_limitations && ds.known_limitations.length > 0 && (
                  <div className="text-xs text-slate-400 bg-slate-900/60 p-2.5 rounded border border-slate-800/80">
                    <span className="text-amber-400 font-medium block mb-1 flex items-center gap-1">
                      <AlertTriangle className="w-3 h-3" /> Known Scientific Limitations:
                    </span>
                    <ul className="list-disc list-inside space-y-0.5 text-[11px] text-slate-400">
                      {ds.known_limitations.map((lim, i) => (
                        <li key={i}>{lim}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-xs">
                  <span className="text-slate-500 font-mono text-[10px]">ID: {ds.id}</span>
                  <a
                    href={ds.source_url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-emerald-400 hover:text-emerald-300 flex items-center gap-1 font-medium"
                  >
                    Open Source Portal <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};
