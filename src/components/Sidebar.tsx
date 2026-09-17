import React from 'react';
import {
  MessageSquare,
  Leaf,
  MapPin,
  Brain,
  BookOpen,
  Sprout,
  BarChart3,
  Settings,
  X,
} from 'lucide-react';
import { VasudhaLogo } from './VasudhaLogo';

export type WorkspaceTab =
  | 'intelligence'
  | 'environment'
  | 'location'
  | 'reasoning'
  | 'evidence'
  | 'actions'
  | 'impact';

interface SidebarProps {
  activeTab: WorkspaceTab;
  onSelectTab: (tab: WorkspaceTab) => void;
  onOpenSettings: () => void;
  isOpenMobile: boolean;
  onCloseMobile: () => void;
  currentRegion?: string;
  verifiedMetricsCount?: number;
}

const NAV_ITEMS: Array<{
  id: WorkspaceTab;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}> = [
  {
    id: 'intelligence',
    label: 'Intelligence',
    icon: MessageSquare,
  },
  {
    id: 'environment',
    label: 'Environment',
    icon: Leaf,
  },
  {
    id: 'location',
    label: 'Location',
    icon: MapPin,
  },
  {
    id: 'reasoning',
    label: 'Reasoning',
    icon: Brain,
  },
  {
    id: 'evidence',
    label: 'Evidence',
    icon: BookOpen,
  },
  {
    id: 'actions',
    label: 'Actions',
    icon: Sprout,
  },
  {
    id: 'impact',
    label: 'Impact',
    icon: BarChart3,
  },
];

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onSelectTab,
  onOpenSettings,
  isOpenMobile,
  onCloseMobile,
}) => {
  return (
    <>
      {/* Mobile Backdrop */}
      {isOpenMobile && (
        <div
          className="fixed inset-0 bg-stone-950/60 backdrop-blur-xs z-40 lg:hidden"
          onClick={onCloseMobile}
          aria-hidden="true"
        />
      )}

      {/* Sidebar Container: Deep Forest Green #0e241d */}
      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-60 bg-[#0e241d] text-stone-100 flex flex-col border-r border-[#16362b] transition-transform duration-200 ease-in-out lg:translate-x-0 ${
          isOpenMobile ? 'translate-x-0' : '-translate-x-full'
        }`}
        aria-label="Main Navigation"
      >
        {/* Brand Header */}
        <div className="pt-6 pb-6 px-5 flex items-center justify-between">
          <div
            onClick={() => {
              onSelectTab('intelligence');
              onCloseMobile();
            }}
            className="cursor-pointer group select-none"
          >
            <VasudhaLogo variant="sidebar" theme="dark" />
          </div>

          <button
            onClick={onCloseMobile}
            className="p-1 rounded-md text-stone-400 hover:text-stone-100 hover:bg-[#1a382e] lg:hidden"
            aria-label="Close navigation"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Primary Vertical Navigation List */}
        <nav className="flex-1 overflow-y-auto px-3.5 py-2 space-y-1.5">
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;

            return (
              <button
                key={item.id}
                onClick={() => {
                  onSelectTab(item.id);
                  onCloseMobile();
                }}
                className={`w-full group flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-left transition-all ${
                  isActive
                    ? 'bg-[#254338] text-white font-medium shadow-xs'
                    : 'text-[#9cb5a8] hover:text-white hover:bg-[#163328]'
                }`}
                aria-current={isActive ? 'page' : undefined}
              >
                <Icon
                  className={`w-4 h-4 shrink-0 transition-colors ${
                    isActive ? 'text-white' : 'text-[#9cb5a8] group-hover:text-emerald-300'
                  }`}
                />
                <span className="text-[13px] font-medium tracking-tight">
                  {item.label}
                </span>
              </button>
            );
          })}

          {/* Thin Divider */}
          <div className="pt-2 pb-1">
            <div className="border-t border-[#1a382e]" />
          </div>

          {/* Settings Nav Item */}
          <button
            onClick={() => {
              onOpenSettings();
              onCloseMobile();
            }}
            className="w-full group flex items-center gap-3.5 px-3.5 py-2.5 rounded-xl text-left transition-all text-[#9cb5a8] hover:text-white hover:bg-[#163328]"
          >
            <Settings className="w-4 h-4 shrink-0 text-[#9cb5a8] group-hover:text-emerald-300" />
            <span className="text-[13px] font-medium tracking-tight">Settings</span>
          </button>
        </nav>

        {/* Subtle Bottom Brand Footer */}
        <div className="p-4 border-t border-[#16362b] text-[11px] text-[#718c80] flex items-center justify-between font-mono">
          <span className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            VASUDHA v2.4
          </span>
          <span className="text-[10px]">Tier-1 RAG</span>
        </div>
      </aside>
    </>
  );
};
