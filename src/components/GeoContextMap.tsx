/**
 * GeoContextMap.tsx - Clean, Scientific Interactive Map & Spatial Context Component (Phase 2)
 *
 * Implements:
 * - Leaflet map with OpenStreetMap tiles & custom SVG pin
 * - Pin selection via map click or coordinate inputs
 * - Synchronization with canonical EnvironmentalState (latitude, longitude, region, ecosystem)
 * - Strict non-destructive updates (preserves soil, climate, biodiversity, land, human impact)
 * - Graceful degradation for map loading failures and offline/unavailable geospatial services
 */

import React, { useEffect, useRef, useState, useCallback } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import {
  MapPin,
  Compass,
  X,
  RefreshCw,
  Layers,
  AlertCircle,
  CheckCircle2,
  HelpCircle,
  Globe,
  Sliders,
} from 'lucide-react';
import { SpatialContext, GeoContextResult } from '../types';
import { lookupGeoContext } from '../services/api';

interface GeoContextMapProps {
  spatialContext: SpatialContext;
  onSpatialChange: (updated: SpatialContext) => void;
  disabled?: boolean;
}

// Preset ecological benchmarks for rapid scientific testing
const ECOLOGICAL_PRESETS = [
  { name: 'Nandurbar, Maharashtra, India', lat: 21.25, lon: 74.23, eco: 'Tropical Dry Deciduous / Cropland Ecotone' },
  { name: 'Western Ghats, India', lat: 12.5, lon: 75.5, eco: 'Tropical Moist Forest' },
  { name: 'Amazon Basin, Brazil', lat: -3.4, lon: -62.2, eco: 'Evergreen Rainforest' },
  { name: 'Fennoscandia, Finland', lat: 61.0, lon: 24.0, eco: 'Boreal Taiga & Peatland' },
  { name: 'Serengeti, Tanzania', lat: -2.3, lon: 34.8, eco: 'Acacia Savanna & Grassland' },
  { name: 'Mediterranean, Italy', lat: 41.9, lon: 12.5, eco: 'Mediterranean Woodland' },
];

export const GeoContextMap: React.FC<GeoContextMapProps> = ({
  spatialContext,
  onSpatialChange,
  disabled = false,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markerRef = useRef<L.Marker | null>(null);

  // Manual input state
  const [inputLat, setInputLat] = useState<string>(
    spatialContext.latitude !== null && spatialContext.latitude !== undefined
      ? spatialContext.latitude.toString()
      : ''
  );
  const [inputLon, setInputLon] = useState<string>(
    spatialContext.longitude !== null && spatialContext.longitude !== undefined
      ? spatialContext.longitude.toString()
      : ''
  );

  const [inputError, setInputError] = useState<string | null>(null);
  const [isLoadingContext, setIsLoadingContext] = useState<boolean>(false);
  const [mapLoadError, setMapLoadError] = useState<boolean>(false);
  const [enrichmentNotice, setEnrichmentNotice] = useState<string | null>(null);

  // Sync internal input fields if parent state changes externally
  useEffect(() => {
    if (spatialContext.latitude !== null && spatialContext.latitude !== undefined) {
      setInputLat(spatialContext.latitude.toString());
    } else {
      setInputLat('');
    }

    if (spatialContext.longitude !== null && spatialContext.longitude !== undefined) {
      setInputLon(spatialContext.longitude.toString());
    } else {
      setInputLon('');
    }
  }, [spatialContext.latitude, spatialContext.longitude]);

  // SVG Pin definition to bypass Leaflet asset loading dependencies
  const createPinIcon = useCallback((regionName?: string) => {
    const label = regionName ? regionName.substring(0, 16) : 'Selected Pin';
    return L.divIcon({
      className: 'geo-leaflet-custom-marker',
      html: `
        <div style="position: relative; display: flex; flex-direction: column; align-items: center; transform: translate(-50%, -100%);">
          <div style="background-color: #065f46; color: #ffffff; padding: 2px 6px; border-radius: 3px; font-size: 11px; font-weight: 600; font-family: monospace; white-space: nowrap; box-shadow: 0 2px 4px rgba(0,0,0,0.3); border: 1px solid #047857; margin-bottom: 2px;">
            ${label}
          </div>
          <div style="width: 14px; height: 14px; background-color: #059669; border: 2px solid #ffffff; border-radius: 50%; box-shadow: 0 1px 3px rgba(0,0,0,0.35);"></div>
        </div>
      `,
      iconSize: [0, 0],
      iconAnchor: [0, 0],
    });
  }, []);

  // Update or place marker on map
  const updateMapMarker = useCallback((lat: number, lon: number, regionName?: string) => {
    if (!mapInstanceRef.current) return;

    const map = mapInstanceRef.current;
    const latLng = L.latLng(lat, lon);

    if (markerRef.current) {
      markerRef.current.setLatLng(latLng);
      markerRef.current.setIcon(createPinIcon(regionName));
    } else {
      const marker = L.marker(latLng, {
        icon: createPinIcon(regionName),
        draggable: !disabled,
      }).addTo(map);

      marker.on('dragend', (e) => {
        const newPos = e.target.getLatLng();
        handleCoordinateSelection(newPos.lat, newPos.lng);
      });

      markerRef.current = marker;
    }

    map.panTo(latLng, { animate: true });
  }, [createPinIcon, disabled]);

  // Remove marker from map
  const removeMapMarker = useCallback(() => {
    if (markerRef.current && mapInstanceRef.current) {
      mapInstanceRef.current.removeLayer(markerRef.current);
      markerRef.current = null;
    }
  }, []);

  // Coordinate resolution handler
  const handleCoordinateSelection = async (lat: number, lon: number) => {
    // Validate boundaries
    if (isNaN(lat) || lat < -90 || lat > 90) {
      setInputError('Latitude must be between -90.0° and +90.0°');
      return;
    }
    if (isNaN(lon) || lon < -180 || lon > 180) {
      setInputError('Longitude must be between -180.0° and +180.0°');
      return;
    }

    setInputError(null);
    setIsLoadingContext(true);
    setEnrichmentNotice(null);

    const roundedLat = Math.round(lat * 1000000) / 1000000;
    const roundedLon = Math.round(lon * 1000000) / 1000000;

    setInputLat(roundedLat.toString());
    setInputLon(roundedLon.toString());

    try {
      // Query backend GeoContextProvider
      const geoResult: GeoContextResult = await lookupGeoContext({
        latitude: roundedLat,
        longitude: roundedLon,
      });

      const updatedContext: SpatialContext = {
        latitude: roundedLat,
        longitude: roundedLon,
        region: geoResult.region || null,
        ecosystem: geoResult.ecosystem || null,
      };

      onSpatialChange(updatedContext);
      updateMapMarker(roundedLat, roundedLon, geoResult.region || undefined);

      if (geoResult.degraded) {
        setEnrichmentNotice('Geospatial provider degraded: coordinates preserved; region/ecosystem marked unknown.');
      } else {
        setEnrichmentNotice(`Enriched: ${geoResult.region || 'Region identified'} • ${geoResult.ecosystem || ''}`);
      }
    } catch (err) {
      // Graceful degradation: preserve coordinates even if geo service is offline
      const fallbackContext: SpatialContext = {
        latitude: roundedLat,
        longitude: roundedLon,
        region: spatialContext.region || null,
        ecosystem: spatialContext.ecosystem || null,
      };
      onSpatialChange(fallbackContext);
      updateMapMarker(roundedLat, roundedLon, spatialContext.region || undefined);
      setEnrichmentNotice('Geospatial service offline: coordinates recorded, region/ecosystem unresolved.');
    } finally {
      setIsLoadingContext(false);
    }
  };

  // Initialize Leaflet Map
  useEffect(() => {
    if (!mapContainerRef.current) return;

    // Destroy existing instance if container is reused
    if (mapInstanceRef.current) {
      mapInstanceRef.current.remove();
      mapInstanceRef.current = null;
      markerRef.current = null;
    }

    try {
      const initialLat = spatialContext.latitude ?? 20.0;
      const initialLon = spatialContext.longitude ?? 0.0;
      const initialZoom = spatialContext.latitude !== null && spatialContext.latitude !== undefined ? 5 : 2;

      const map = L.map(mapContainerRef.current, {
        center: [initialLat, initialLon],
        zoom: initialZoom,
        minZoom: 1,
        maxZoom: 18,
        zoomControl: true,
        attributionControl: false,
      });

      // Standard OpenStreetMap tiles
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
      }).addTo(map);

      // Handle map click to drop or change pin
      map.on('click', (e: L.LeafletMouseEvent) => {
        if (disabled) return;
        handleCoordinateSelection(e.latlng.lat, e.latlng.lng);
      });

      mapInstanceRef.current = map;

      // If initial coordinates exist, place the pin
      if (
        spatialContext.latitude !== null &&
        spatialContext.latitude !== undefined &&
        spatialContext.longitude !== null &&
        spatialContext.longitude !== undefined
      ) {
        updateMapMarker(
          spatialContext.latitude,
          spatialContext.longitude,
          spatialContext.region || undefined
        );
      }
    } catch (err) {
      console.error('Failed to initialize interactive map:', err);
      setMapLoadError(true);
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
        markerRef.current = null;
      }
    };
  }, []); // Run once on mount

  // Apply manual input coordinates
  const handleApplyManualCoordinates = (e: React.FormEvent) => {
    e.preventDefault();
    const lat = parseFloat(inputLat);
    const lon = parseFloat(inputLon);

    if (isNaN(lat) || isNaN(lon)) {
      setInputError('Please enter valid numeric decimal coordinates');
      return;
    }

    handleCoordinateSelection(lat, lon);
  };

  // Clear location
  const handleClearLocation = () => {
    setInputLat('');
    setInputLon('');
    setInputError(null);
    setEnrichmentNotice(null);
    removeMapMarker();

    // Reset to empty coordinates and unknown region/ecosystem
    onSpatialChange({
      latitude: null,
      longitude: null,
      region: null,
      ecosystem: null,
    });
  };

  // Has selected location
  const hasLocation =
    spatialContext.latitude !== null &&
    spatialContext.latitude !== undefined &&
    spatialContext.longitude !== null &&
    spatialContext.longitude !== undefined;

  return (
    <div className="bg-white border border-stone-200 rounded-sm overflow-hidden">
      {/* Header Bar */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-stone-200 bg-stone-50">
        <div className="flex items-center gap-2">
          <Globe className="w-4 h-4 text-emerald-700" />
          <h3 className="text-xs font-semibold font-mono tracking-wider text-stone-800 uppercase">
            Geo Context & Interactive Spatial Grounding
          </h3>
        </div>
        <div className="flex items-center gap-2 text-xs">
          {hasLocation ? (
            <span className="inline-flex items-center gap-1 font-mono text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-sm border border-emerald-200">
              <CheckCircle2 className="w-3 h-3" />
              Pinned ({spatialContext.latitude?.toFixed(4)}°, {spatialContext.longitude?.toFixed(4)}°)
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 font-mono text-stone-500 bg-stone-100 px-2 py-0.5 rounded-sm border border-stone-200">
              <HelpCircle className="w-3 h-3 text-stone-400" />
              Location Unpinned
            </span>
          )}
        </div>
      </div>

      {/* Main Map + Controls Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-0">
        {/* Interactive Map Canvas */}
        <div className="lg:col-span-8 relative bg-stone-100 min-h-[300px] border-b lg:border-b-0 lg:border-r border-stone-200">
          {!mapLoadError ? (
            <div
              ref={mapContainerRef}
              className="w-full h-[320px] z-0 focus:outline-hidden"
              style={{ cursor: disabled ? 'default' : 'crosshair' }}
              aria-label="Interactive Ecological Map"
            />
          ) : (
            <div className="w-full h-[320px] flex flex-col items-center justify-center p-6 text-center text-stone-600 bg-stone-50">
              <AlertCircle className="w-8 h-8 text-amber-600 mb-2" />
              <p className="text-sm font-semibold text-stone-800">Map Rendering Fallback Mode</p>
              <p className="text-xs text-stone-500 max-w-sm mt-1">
                Visual tile server connection unavailable in this viewport. Use the precision coordinate inputs below to set location.
              </p>
            </div>
          )}

          {/* Map Overlay Instructions */}
          <div className="absolute top-2 left-2 z-[500] bg-white/90 backdrop-blur-xs border border-stone-300 px-2.5 py-1 rounded-sm text-[11px] font-mono text-stone-700 shadow-xs pointer-events-none">
            Click map or drag pin to position coordinates
          </div>

          {/* Loading indicator */}
          {isLoadingContext && (
            <div className="absolute inset-0 z-[600] bg-white/60 backdrop-blur-xs flex items-center justify-center gap-2 text-xs font-mono text-emerald-800">
              <RefreshCw className="w-4 h-4 animate-spin text-emerald-600" />
              Resolving ecological context & WWF biome...
            </div>
          )}
        </div>

        {/* Spatial Properties & Coordinate Input Sidebar */}
        <div className="lg:col-span-4 p-4 flex flex-col justify-between space-y-4 bg-white">
          {/* Coordinate Input Form */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-mono font-semibold text-stone-700">Precision Coordinates</span>
              {hasLocation && (
                <button
                  type="button"
                  onClick={handleClearLocation}
                  disabled={disabled}
                  className="text-xs font-mono text-stone-500 hover:text-red-700 flex items-center gap-1 hover:underline cursor-pointer"
                >
                  <X className="w-3 h-3" />
                  Clear Location
                </button>
              )}
            </div>

            <form onSubmit={handleApplyManualCoordinates} className="space-y-2">
              <div className="grid grid-cols-2 gap-2">
                <div>
                  <label className="block text-[11px] font-mono text-stone-500 mb-0.5">
                    Latitude (-90 to +90)
                  </label>
                  <input
                    type="number"
                    step="any"
                    min="-90"
                    max="90"
                    placeholder="e.g. 12.5000"
                    value={inputLat}
                    onChange={(e) => setInputLat(e.target.value)}
                    disabled={disabled}
                    className="w-full text-xs font-mono border border-stone-200 rounded-sm px-2.5 py-1.5 focus:border-emerald-600 focus:outline-hidden bg-stone-50 focus:bg-white"
                  />
                </div>
                <div>
                  <label className="block text-[11px] font-mono text-stone-500 mb-0.5">
                    Longitude (-180 to +180)
                  </label>
                  <input
                    type="number"
                    step="any"
                    min="-180"
                    max="180"
                    placeholder="e.g. 75.5000"
                    value={inputLon}
                    onChange={(e) => setInputLon(e.target.value)}
                    disabled={disabled}
                    className="w-full text-xs font-mono border border-stone-200 rounded-sm px-2.5 py-1.5 focus:border-emerald-600 focus:outline-hidden bg-stone-50 focus:bg-white"
                  />
                </div>
              </div>

              {inputError && (
                <p className="text-[11px] text-red-600 font-mono flex items-center gap-1">
                  <AlertCircle className="w-3 h-3" />
                  {inputError}
                </p>
              )}

              <button
                type="submit"
                disabled={disabled || isLoadingContext || !inputLat || !inputLon}
                className="w-full py-1.5 px-3 text-xs font-mono font-medium text-emerald-900 bg-emerald-100 hover:bg-emerald-200 border border-emerald-300 rounded-sm flex items-center justify-center gap-1.5 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                <MapPin className="w-3.5 h-3.5" />
                Set Location Coordinates
              </button>
            </form>
          </div>

          {/* Quick Presets for Scientific Testing */}
          <div className="pt-2 border-t border-stone-100">
            <span className="block text-[11px] font-mono text-stone-500 mb-1.5">
              Benchmark Ecological Hotspots:
            </span>
            <div className="flex flex-wrap gap-1">
              {ECOLOGICAL_PRESETS.map((preset) => (
                <button
                  key={preset.name}
                  type="button"
                  onClick={() => handleCoordinateSelection(preset.lat, preset.lon)}
                  disabled={disabled}
                  className="text-[10px] font-mono bg-stone-100 hover:bg-stone-200 text-stone-700 px-2 py-0.5 rounded-xs border border-stone-200 cursor-pointer"
                >
                  {preset.name.split(',')[0]}
                </button>
              ))}
            </div>
          </div>

          {/* Resolved Spatial Context Card */}
          <div className="p-3 bg-stone-50 border border-stone-200 rounded-sm text-xs space-y-1.5">
            <div className="flex items-center justify-between pb-1 border-b border-stone-200">
              <span className="font-mono font-semibold text-stone-700 uppercase tracking-wider text-[11px]">
                Spatial Context State
              </span>
              <span className="font-mono text-[10px] text-stone-400">Canonical</span>
            </div>

            <div className="grid grid-cols-2 gap-x-2 gap-y-1 text-[11px]">
              <div>
                <span className="font-mono text-stone-400">Latitude:</span>{' '}
                <span className="font-mono font-semibold text-stone-800">
                  {spatialContext.latitude !== null && spatialContext.latitude !== undefined
                    ? `${spatialContext.latitude.toFixed(6)}°`
                    : 'Unknown'}
                </span>
              </div>
              <div>
                <span className="font-mono text-stone-400">Longitude:</span>{' '}
                <span className="font-mono font-semibold text-stone-800">
                  {spatialContext.longitude !== null && spatialContext.longitude !== undefined
                    ? `${spatialContext.longitude.toFixed(6)}°`
                    : 'Unknown'}
                </span>
              </div>
              <div className="col-span-2">
                <span className="font-mono text-stone-400">Region:</span>{' '}
                <span className="font-mono font-semibold text-emerald-800">
                  {spatialContext.region || 'Unknown / Unassigned'}
                </span>
              </div>
              <div className="col-span-2">
                <span className="font-mono text-stone-400">Ecosystem:</span>{' '}
                <span className="font-mono font-semibold text-stone-800">
                  {spatialContext.ecosystem || 'Unknown / Unassigned'}
                </span>
              </div>
            </div>

            {enrichmentNotice && (
              <p className="text-[10px] font-mono text-stone-600 bg-white p-1.5 rounded-xs border border-stone-200 mt-1">
                {enrichmentNotice}
              </p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
