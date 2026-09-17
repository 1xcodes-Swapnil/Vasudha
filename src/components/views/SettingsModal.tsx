import React, { useState } from 'react';
import { X, Settings, Server, Activity, Layers } from 'lucide-react';
import { HealthStatusCard } from '../HealthStatusCard';
import { SystemPerformanceView } from '../SystemPerformanceView';
import { ArchitecturePipelineView } from '../ArchitecturePipelineView';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

type SettingsTab = 'health' | 'telemetry' | 'architecture';

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState<SettingsTab>('health');

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-stone-900/60 backdrop-blur-xs flex items-center justify-center p-4 sm:p-6">
      <div className="bg-white rounded-2xl border border-stone-200 shadow-xl w-full max-w-4xl max-h-[90vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
        {/* Header */}
        <div className="p-4 sm:px-6 bg-stone-900 text-stone-100 flex items-center justify-between border-b border-stone-800">
          <div className="flex items-center gap-2.5">
            <Settings className="w-4 h-4 text-emerald-400" />
            <div>
              <h2 className="text-sm font-bold tracking-tight">System Settings & Telemetry</h2>
              <p className="text-[11px] text-stone-400 font-mono">
                VASUDHA Platform Health, Latency & Architecture
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1 rounded-lg text-stone-400 hover:text-white hover:bg-stone-800 transition-colors"
            aria-label="Close modal"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tab Selector */}
        <div className="bg-stone-50 border-b border-stone-200 px-4 sm:px-6 py-2 flex gap-2 text-xs font-medium">
          <button
            onClick={() => setActiveTab('health')}
            className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-colors ${
              activeTab === 'health'
                ? 'bg-white text-stone-900 font-bold shadow-2xs border border-stone-200'
                : 'text-stone-600 hover:text-stone-900'
            }`}
          >
            <Server className="w-3.5 h-3.5 text-emerald-600" />
            <span>Service Health</span>
          </button>

          <button
            onClick={() => setActiveTab('telemetry')}
            className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-colors ${
              activeTab === 'telemetry'
                ? 'bg-white text-stone-900 font-bold shadow-2xs border border-stone-200'
                : 'text-stone-600 hover:text-stone-900'
            }`}
          >
            <Activity className="w-3.5 h-3.5 text-blue-600" />
            <span>Performance & Latency</span>
          </button>

          <button
            onClick={() => setActiveTab('architecture')}
            className={`px-3 py-1.5 rounded-lg flex items-center gap-1.5 transition-colors ${
              activeTab === 'architecture'
                ? 'bg-white text-stone-900 font-bold shadow-2xs border border-stone-200'
                : 'text-stone-600 hover:text-stone-900'
            }`}
          >
            <Layers className="w-3.5 h-3.5 text-purple-600" />
            <span>13-Stage Pipeline</span>
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-4">
          {activeTab === 'health' && (
            <div className="space-y-4">
              <HealthStatusCard />
              <div className="p-4 rounded-xl bg-stone-50 border border-stone-200 text-xs text-stone-600 space-y-1">
                <span className="font-bold text-stone-800">Deployment Architecture:</span>
                <p>
                  Running unified React + TypeScript frontend and FastAPI + PostgreSQL / pgvector backend.
                  Graceful degradation active: In local environments where full RAG vector store is offline,
                  the system falls back to structured knowledge-based reasoning without interruption.
                </p>
              </div>
            </div>
          )}

          {activeTab === 'telemetry' && <SystemPerformanceView />}

          {activeTab === 'architecture' && <ArchitecturePipelineView />}
        </div>

        {/* Footer */}
        <div className="p-3 sm:px-6 bg-stone-50 border-t border-stone-200 flex justify-end">
          <button
            onClick={onClose}
            className="px-4 py-1.5 rounded-xl bg-stone-900 text-white hover:bg-stone-800 text-xs font-semibold transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};
