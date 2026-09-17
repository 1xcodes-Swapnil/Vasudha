import React from 'react';
import { ShieldCheck, Layers, Database, Cpu } from 'lucide-react';

export const Header: React.FC = () => {
  return (
    <header className="border-b border-stone-200 bg-stone-50/80 backdrop-blur-xs py-4 px-6 sticky top-0 z-20">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-block w-2.5 h-2.5 rounded-full bg-emerald-600" />
            <h1 className="text-xl font-semibold tracking-tight text-stone-900">
              VASUDHA — Biodiversity Intelligence
            </h1>
            <span className="text-xs font-mono px-2 py-0.5 rounded-sm bg-stone-200 text-stone-700 font-medium">
              Phase 0 Foundation
            </span>
          </div>
          <p className="text-xs text-stone-500 mt-1 max-w-2xl">
            Hybrid Layered RAG Architecture with Knowledge-Based Ecological Reasoning for environmental restoration and biodiversity risk assessment.
          </p>
        </div>

        <div className="flex flex-wrap items-center gap-2 text-xs font-mono text-stone-600">
          <div className="flex items-center gap-1.5 px-2.5 py-1 bg-white border border-stone-200 rounded-sm">
            <Layers className="w-3.5 h-3.5 text-emerald-700" />
            <span>FastAPI + Python</span>
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 bg-white border border-stone-200 rounded-sm">
            <Database className="w-3.5 h-3.5 text-blue-700" />
            <span>pgvector + SQLAlchemy</span>
          </div>
          <div className="flex items-center gap-1.5 px-2.5 py-1 bg-white border border-stone-200 rounded-sm">
            <Cpu className="w-3.5 h-3.5 text-amber-700" />
            <span>Gemini + Local Embeddings</span>
          </div>
        </div>
      </div>
    </header>
  );
};
