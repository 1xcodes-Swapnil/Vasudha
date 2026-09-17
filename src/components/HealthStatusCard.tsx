import React, { useState, useEffect } from 'react';
import { RefreshCw, CheckCircle2, AlertTriangle, XCircle, Server, Database, Sparkles } from 'lucide-react';
import { fetchHealthStatus } from '../services/api';
import { SystemHealth } from '../types';

export const HealthStatusCard: React.FC = () => {
  const [health, setHealth] = useState<SystemHealth | null>(null);
  const [loading, setLoading] = useState(true);

  const loadHealth = async () => {
    setLoading(true);
    try {
      const data = await fetchHealthStatus();
      setHealth(data);
    } catch (err) {
      console.error('Failed to load health:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadHealth();
    const interval = setInterval(loadHealth, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusBadge = (status?: string) => {
    if (status === 'ok' || status === 'connected') {
      return (
        <span className="inline-flex items-center gap-1 text-xs font-medium text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-sm border border-emerald-200">
          <CheckCircle2 className="w-3 h-3 text-emerald-600" />
          Healthy
        </span>
      );
    }
    if (status === 'degraded') {
      return (
        <span className="inline-flex items-center gap-1 text-xs font-medium text-amber-800 bg-amber-50 px-2 py-0.5 rounded-sm border border-amber-200">
          <AlertTriangle className="w-3 h-3 text-amber-600" />
          Ready (Local Fallback)
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 text-xs font-medium text-stone-700 bg-stone-100 px-2 py-0.5 rounded-sm border border-stone-300">
        <XCircle className="w-3 h-3 text-stone-500" />
        Offline
      </span>
    );
  };

  return (
    <div className="bg-white border border-stone-200 rounded-sm p-5 shadow-xs">
      <div className="flex items-center justify-between pb-3 border-b border-stone-100 mb-4">
        <div className="flex items-center gap-2">
          <Server className="w-4 h-4 text-stone-700" />
          <h2 className="text-sm font-semibold uppercase tracking-wider text-stone-700">
            System Foundation & Health Probes
          </h2>
        </div>
        <button
          onClick={loadHealth}
          disabled={loading}
          className="inline-flex items-center gap-1.5 text-xs text-stone-600 hover:text-stone-900 border border-stone-200 px-2.5 py-1 rounded-sm hover:bg-stone-50 transition cursor-pointer"
        >
          <RefreshCw className={`w-3 h-3 ${loading ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Backend API status */}
        <div className="p-3.5 bg-stone-50 border border-stone-200 rounded-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-mono font-semibold text-stone-600">FastAPI Backend</span>
            {getStatusBadge(health?.status)}
          </div>
          <div className="text-xs text-stone-600 space-y-1">
            <p><span className="font-mono text-stone-400">Endpoint:</span> /api/v1/health</p>
            <p><span className="font-mono text-stone-400">Env:</span> {health?.environment || 'development'}</p>
            <p><span className="font-mono text-stone-400">Version:</span> {health?.version || '0.1.0'}</p>
          </div>
        </div>

        {/* Database status */}
        <div className="p-3.5 bg-stone-50 border border-stone-200 rounded-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-mono font-semibold text-stone-600">Data Layer</span>
            {getStatusBadge(health?.database?.status)}
          </div>
          <div className="text-xs text-stone-600 space-y-1">
            <p><span className="font-mono text-stone-400">Engine:</span> {health?.database?.dialect === 'sqlite' ? 'SQLite (Local Development)' : 'PostgreSQL + pgvector'}</p>
            <p><span className="font-mono text-stone-400">Vector Extension:</span> {health?.database?.pgvector_enabled ? 'Active (pgvector)' : 'Configured (pgvector/Phase 1 Ready)'}</p>
            <p><span className="font-mono text-stone-400">Alembic:</span> Ready for Migrations</p>
          </div>
        </div>

        {/* AI Providers status */}
        <div className="p-3.5 bg-stone-50 border border-stone-200 rounded-sm">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-mono font-semibold text-stone-600">AI Abstractions</span>
            <span className="inline-flex items-center gap-1 text-xs font-medium text-blue-700 bg-blue-50 px-2 py-0.5 rounded-sm border border-blue-200">
              <Sparkles className="w-3 h-3" />
              Decoupled
            </span>
          </div>
          <div className="text-xs text-stone-600 space-y-1">
            <p><span className="font-mono text-stone-400">LLM Provider:</span> {health?.ai_providers?.llm || 'Gemini (Abstracted)'}</p>
            <p><span className="font-mono text-stone-400">Embeddings:</span> {health?.ai_providers?.embeddings || 'Local/Free (Abstracted)'}</p>
            <p><span className="font-mono text-stone-400">Dimension:</span> 384 (all-MiniLM-L6-v2)</p>
          </div>
        </div>
      </div>
    </div>
  );
};
