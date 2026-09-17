import React, { useState } from 'react';
import {
  Zap,
  Clock,
  ChevronUp,
  ChevronDown,
  ChevronRight,
  Sprout,
  SlidersHorizontal,
  BookOpen,
  Lightbulb,
} from 'lucide-react';
import { MiniLocationCard } from './MiniLocationCard';
import { SpatialContext, EnvironmentalState } from '../../types';
import { WorkspaceTab } from '../Sidebar';

interface IntelligenceRightPanelProps {
  spatialContext: SpatialContext;
  currentState: EnvironmentalState;
  onNavigateTab: (tab: WorkspaceTab) => void;
  onTriggerQuickAction: (actionType: string) => void;
  onSelectRecentAnalysis?: (title: string) => void;
}

export const IntelligenceRightPanel: React.FC<IntelligenceRightPanelProps> = ({
  spatialContext,
  onNavigateTab,
  onTriggerQuickAction,
  onSelectRecentAnalysis,
}) => {
  const [isRecentOpen, setIsRecentOpen] = useState(true);

  const QUICK_ACTIONS = [
    {
      id: 'analyze-biodiversity',
      label: 'Analyze Biodiversity',
      icon: Sprout,
      action: () => onTriggerQuickAction('Analyze Biodiversity'),
    },
    {
      id: 'check-state',
      label: 'Check Environmental State',
      icon: SlidersHorizontal,
      action: () => onNavigateTab('environment'),
    },
    {
      id: 'view-evidence',
      label: 'View Scientific Evidence',
      icon: BookOpen,
      action: () => onNavigateTab('evidence'),
    },
    {
      id: 'get-recommendations',
      label: 'Get Recommendations',
      icon: Lightbulb,
      action: () => onNavigateTab('actions'),
    },
  ];

  const RECENT_ANALYSES = [
    {
      id: 'recent-1',
      title: 'Cropland Biodiversity Assessment',
      time: '2 hours ago',
      status: 'active',
    },
    {
      id: 'recent-2',
      title: 'Soil Health Analysis',
      time: '1 day ago',
      status: 'archived',
    },
    {
      id: 'recent-3',
      title: 'Climate Impact Projection',
      time: '2 days ago',
      status: 'archived',
    },
  ];

  return (
    <div className="w-full space-y-4 select-none">
      {/* 1. Current Location Card */}
      <MiniLocationCard
        spatialContext={spatialContext}
        onViewMap={() => onNavigateTab('location')}
      />

      {/* 2. Quick Actions Card */}
      <div className="bg-white rounded-2xl border border-stone-200/80 p-4 shadow-2xs space-y-3">
        <div className="flex items-center gap-2 text-stone-800 text-xs font-semibold">
          <Zap className="w-4 h-4 text-stone-700" />
          <span>Quick Actions</span>
        </div>

        <div className="space-y-1">
          {QUICK_ACTIONS.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                type="button"
                onClick={item.action}
                className="w-full flex items-center justify-between p-2.5 rounded-xl text-left hover:bg-emerald-50/60 active:bg-emerald-100/70 text-stone-700 hover:text-emerald-950 group transition-all cursor-pointer border border-transparent hover:border-emerald-200/60"
              >
                <div className="flex items-center gap-2.5 min-w-0">
                  <Icon className="w-3.5 h-3.5 text-stone-500 group-hover:text-emerald-700 shrink-0 transition-colors" />
                  <span className="text-xs font-medium truncate">{item.label}</span>
                </div>
                <ChevronRight className="w-3.5 h-3.5 text-stone-400 group-hover:text-emerald-800 group-hover:translate-x-0.5 transition-all shrink-0" />
              </button>
            );
          })}
        </div>
      </div>

      {/* 3. Recent Analysis Card */}
      <div className="bg-white rounded-2xl border border-stone-200/80 p-4 shadow-2xs space-y-3">
        <button
          type="button"
          onClick={() => setIsRecentOpen(!isRecentOpen)}
          className="w-full flex items-center justify-between text-stone-800 text-xs font-semibold cursor-pointer"
        >
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4 text-stone-700" />
            <span>Recent Analysis</span>
          </div>
          {isRecentOpen ? (
            <ChevronUp className="w-4 h-4 text-stone-500" />
          ) : (
            <ChevronDown className="w-4 h-4 text-stone-500" />
          )}
        </button>

        {isRecentOpen && (
          <div className="space-y-1 pt-1 animate-in fade-in duration-150">
            {RECENT_ANALYSES.map((analysis) => (
              <button
                key={analysis.id}
                type="button"
                onClick={() => onSelectRecentAnalysis && onSelectRecentAnalysis(analysis.title)}
                className="w-full flex items-center justify-between p-2.5 rounded-xl text-left hover:bg-stone-50 active:bg-stone-100 text-stone-700 hover:text-stone-900 group transition-all cursor-pointer border border-transparent hover:border-stone-200/60"
              >
                <div className="min-w-0 pr-2">
                  <div className="flex items-center gap-1.5">
                    <span
                      className={`w-1.5 h-1.5 rounded-full shrink-0 ${
                        analysis.status === 'active' ? 'bg-emerald-600' : 'bg-stone-300'
                      }`}
                    />
                    <span className="text-xs font-medium text-stone-800 truncate">
                      {analysis.title}
                    </span>
                  </div>
                  <div className="text-[10px] text-stone-500 pl-3 font-mono">
                    {analysis.time}
                  </div>
                </div>
                <ChevronRight className="w-3.5 h-3.5 text-stone-400 group-hover:text-stone-700 group-hover:translate-x-0.5 transition-all shrink-0" />
              </button>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
