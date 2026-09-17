/**
 * VASUDHA — Biodiversity Intelligence
 * Biodiversity Intelligence for a Living Earth
 */

import React, { useState } from 'react';
import { Sidebar, WorkspaceTab } from './components/Sidebar';
import { TopBar } from './components/TopBar';
import { IntelligenceView } from './components/views/IntelligenceView';
import { EnvironmentView } from './components/views/EnvironmentView';
import { LocationView } from './components/views/LocationView';
import { ReasoningView } from './components/views/ReasoningView';
import { EvidenceView } from './components/views/EvidenceView';
import { ActionsView } from './components/views/ActionsView';
import { ImpactView } from './components/views/ImpactView';
import { SettingsModal } from './components/views/SettingsModal';
import { EnvironmentalState, SpatialContext } from './types';
import { resetSessionMemory } from './services/api';

const INITIAL_ENVIRONMENTAL_STATE: EnvironmentalState = {
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
};

export default function App() {
  const [activeTab, setActiveTab] = useState<WorkspaceTab>('intelligence');
  const [isMobileNavOpen, setIsMobileNavOpen] = useState<boolean>(false);
  const [isSettingsOpen, setIsSettingsOpen] = useState<boolean>(false);

  const [environmentalState, setEnvironmentalState] = useState<EnvironmentalState>(
    INITIAL_ENVIRONMENTAL_STATE
  );

  // Persistent conversation state across turns
  const [sessionId, setSessionId] = useState<string>(
    () => `session_${Math.random().toString(36).substring(2, 9)}`
  );
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>([
    {
      role: 'assistant',
      content:
        'Welcome to VASUDHA — Biodiversity Intelligence for a Living Earth.\n\nUnderstand environmental conditions, trace ecological relationships, and discover evidence-backed actions for biodiversity.',
    },
  ]);

  // Spatial update preserving other indicators
  const handleSpatialChange = (updatedSpatial: SpatialContext) => {
    setEnvironmentalState((prev) => ({
      ...prev,
      spatial_context: updatedSpatial,
    }));
  };

  // Reset conversation session
  const handleResetSession = async () => {
    try {
      await resetSessionMemory(sessionId);
    } catch {
      // Degrade gracefully if backend was unreachable
    }
    const newSession = `session_${Math.random().toString(36).substring(2, 9)}`;
    setSessionId(newSession);
    setMessages([
      {
        role: 'assistant',
        content:
          'Dialogue history reset. Describe an ecological site disturbance or ask for multi-metric intervention guidance.',
      },
    ]);
  };

  // Start new analysis
  const handleNewAnalysis = () => {
    setEnvironmentalState(INITIAL_ENVIRONMENTAL_STATE);
    handleResetSession();
  };

  return (
    <div className="min-h-screen bg-[#f7f8f5] text-stone-900 flex font-sans selection:bg-emerald-100 selection:text-emerald-900">
      {/* Persistent Vertical Navigation Sidebar */}
      <Sidebar
        activeTab={activeTab}
        onSelectTab={setActiveTab}
        onOpenSettings={() => setIsSettingsOpen(true)}
        isOpenMobile={isMobileNavOpen}
        onCloseMobile={() => setIsMobileNavOpen(false)}
        currentRegion={environmentalState.spatial_context.region || 'Nandurbar, Maharashtra, India'}
        verifiedMetricsCount={12}
      />

      {/* Main Workspace Area (offset by sidebar width on desktop) */}
      <div className="flex-1 flex flex-col min-w-0 lg:pl-60">
        {/* Minimal Global Header */}
        <TopBar
          activeTab={activeTab}
          onOpenMobileMenu={() => setIsMobileNavOpen(true)}
          onSelectTab={setActiveTab}
          onResetSession={handleResetSession}
          onNewAnalysis={handleNewAnalysis}
          onSelectLocation={(loc) => {
            handleSpatialChange({
              region: loc.region,
              ecosystem: loc.ecosystem,
              latitude: loc.lat,
              longitude: loc.lon,
            });
          }}
          currentRegion={environmentalState.spatial_context.region || 'Nandurbar, Maharashtra, India'}
          coordinates={{
            lat: environmentalState.spatial_context.latitude ?? 21.25,
            lon: environmentalState.spatial_context.longitude ?? 74.23,
          }}
        />

        {/* Tabbed Main Content Canvas */}
        <main className="flex-1 p-4 sm:p-6 md:p-8">
          {activeTab === 'intelligence' && (
            <IntelligenceView
              currentState={environmentalState}
              onStateSynced={setEnvironmentalState}
              onNavigateTab={setActiveTab}
              sessionId={sessionId}
              messages={messages}
              setMessages={setMessages}
            />
          )}

          {activeTab === 'environment' && (
            <EnvironmentView
              state={environmentalState}
              onStateChange={setEnvironmentalState}
            />
          )}

          {activeTab === 'location' && (
            <LocationView
              state={environmentalState}
              onSpatialContextChange={handleSpatialChange}
            />
          )}

          {activeTab === 'reasoning' && (
            <ReasoningView state={environmentalState} />
          )}

          {activeTab === 'evidence' && (
            <EvidenceView state={environmentalState} />
          )}

          {activeTab === 'actions' && (
            <ActionsView state={environmentalState} />
          )}

          {activeTab === 'impact' && (
            <ImpactView state={environmentalState} />
          )}
        </main>

        {/* Minimal Workspace Footer */}
        <footer className="border-t border-stone-200/80 bg-white/70 py-3 px-6">
          <div className="flex flex-col sm:flex-row items-center justify-between text-[11px] text-stone-500 gap-2 font-mono">
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              <span className="font-semibold text-stone-700">VASUDHA</span>
              <span>•</span>
              <span>Biodiversity Intelligence for a Living Earth</span>
            </div>
            <div className="flex items-center gap-3">
              <span>Scientific Grounding: IPCC / IPBES / FAO / UNEP</span>
              <span>•</span>
              <span>Zero Fabricated Citations</span>
            </div>
          </div>
        </footer>
      </div>

      {/* Settings & Telemetry Modal */}
      <SettingsModal
        isOpen={isSettingsOpen}
        onClose={() => setIsSettingsOpen(false)}
      />
    </div>
  );
}
