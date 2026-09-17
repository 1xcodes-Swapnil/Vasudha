import React, { useState, useEffect } from 'react';
import {
  BookOpen,
  CheckCircle2,
  ExternalLink,
  Filter,
  Layers,
  Search,
  FileText,
  Building2,
  Calendar,
  Sparkles,
  ChevronRight,
  ChevronDown,
} from 'lucide-react';
import {
  ScientificDocument,
  ScientificChunk,
  EvidenceChunkPacket,
} from '../types';
import {
  fetchCorpusDocuments,
  fetchDocumentChunks,
  searchScientificEvidence,
} from '../services/api';

export const ScientificCorpusExplorer: React.FC = () => {
  const [documents, setDocuments] = useState<ScientificDocument[]>([]);
  const [loadingDocs, setLoadingDocs] = useState<boolean>(true);
  const [selectedDocId, setSelectedDocId] = useState<string | null>(null);
  const [selectedDocChunks, setSelectedDocChunks] = useState<ScientificChunk[]>([]);
  const [loadingChunks, setLoadingChunks] = useState<boolean>(false);

  // Search State
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [isSearching, setIsSearching] = useState<boolean>(false);
  const [searchResults, setSearchResults] = useState<EvidenceChunkPacket[]>([]);
  const [selectedOrgFilter, setSelectedOrgFilter] = useState<string>('ALL');

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    setLoadingDocs(true);
    try {
      const docs = await fetchCorpusDocuments();
      setDocuments(docs);
      if (docs.length > 0 && !selectedDocId) {
        handleSelectDoc(docs[0].id);
      }
    } catch (err) {
      console.error('Failed to load scientific documents:', err);
    } finally {
      setLoadingDocs(false);
    }
  };

  const handleSelectDoc = async (docId: string) => {
    setSelectedDocId(docId);
    setLoadingChunks(true);
    try {
      const chunks = await fetchDocumentChunks(docId);
      setSelectedDocChunks(chunks);
    } catch (err) {
      console.error('Failed to load document chunks:', err);
    } finally {
      setLoadingChunks(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;

    setIsSearching(true);
    try {
      const res = await searchScientificEvidence({
        query: searchQuery,
        top_k: 6,
      });
      setSearchResults(res.evidence_chunks);
    } catch (err) {
      console.error('Semantic search failed:', err);
    } finally {
      setIsSearching(false);
    }
  };

  const organizations = ['ALL', 'IPCC', 'IPBES', 'FAO', 'UNEP', 'CBD', 'Science', 'Nature'];

  const filteredDocs =
    selectedOrgFilter === 'ALL'
      ? documents
      : documents.filter((d) =>
          d.organization.toLowerCase().includes(selectedOrgFilter.toLowerCase())
        );

  const selectedDoc = documents.find((d) => d.id === selectedDocId);

  return (
    <div className="bg-white border border-stone-200 rounded-sm p-6 shadow-xs space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-stone-100 gap-2">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-sm font-semibold uppercase tracking-wider text-stone-800">
              Scientific Corpus & Evidence Knowledge Base
            </h2>
            <span className="text-2xs font-mono px-2 py-0.5 bg-emerald-50 text-emerald-800 border border-emerald-200 rounded-sm font-medium">
              Phase 4 Active
            </span>
          </div>
          <p className="text-xs text-stone-500 mt-1">
            Curated repository of landmark global assessments and peer-reviewed literature.
            Zero hallucination guarantee with 100% citation and DOI traceability.
          </p>
        </div>
        <div className="text-xs font-mono text-stone-500 bg-stone-50 px-2.5 py-1 border border-stone-200 rounded-sm self-start sm:self-auto">
          Indexed: <span className="font-bold text-stone-800">{documents.length}</span> Documents
        </div>
      </div>

      {/* Semantic Search Bar */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <div className="relative flex-1">
          <Search className="w-4 h-4 text-stone-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search scientific evidence (e.g., 'soil organic carbon drought water retention' or 'habitat fragmentation')..."
            className="w-full pl-9 pr-4 py-2 text-xs bg-stone-50 border border-stone-300 rounded-sm focus:outline-none focus:ring-1 focus:ring-emerald-500 focus:bg-white transition-all text-stone-800"
          />
        </div>
        <button
          type="submit"
          disabled={isSearching || !searchQuery.trim()}
          className="px-4 py-2 text-xs font-medium text-white bg-emerald-700 hover:bg-emerald-800 rounded-sm shadow-2xs transition-colors disabled:opacity-50"
        >
          {isSearching ? 'Searching Vector Space...' : 'Semantic Search'}
        </button>
      </form>

      {/* Search Results Display */}
      {searchResults.length > 0 && (
        <div className="bg-stone-50 p-4 border border-emerald-200 rounded-sm space-y-3">
          <div className="flex items-center justify-between">
            <h3 className="text-2xs font-mono uppercase font-bold text-emerald-900 flex items-center gap-1.5">
              <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
              Retrieved Evidence Packets ({searchResults.length})
            </h3>
            <button
              onClick={() => setSearchResults([])}
              className="text-3xs text-stone-500 hover:text-stone-800 underline"
            >
              Clear Search
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {searchResults.map((result) => (
              <div
                key={result.chunk_id}
                className="bg-white p-3 border border-stone-200 rounded-2xs text-xs space-y-2"
              >
                <div className="flex items-start justify-between gap-2">
                  <span className="text-2xs font-bold text-stone-800">{result.title}</span>
                  <span className="px-1.5 py-0.5 text-3xs font-mono bg-emerald-100 text-emerald-900 rounded-2xs shrink-0">
                    {(result.relevance_score * 100).toFixed(0)}% Match
                  </span>
                </div>
                <p className="text-2xs text-stone-700 font-serif bg-stone-50/70 p-2 rounded-2xs border border-stone-100">
                  "{result.content}"
                </p>
                <div className="text-3xs text-stone-500 font-mono truncate">
                  {result.citation}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Organization Filters */}
      <div className="flex flex-wrap items-center gap-1.5 pt-1">
        <span className="text-3xs font-mono text-stone-500 mr-1 flex items-center gap-1">
          <Filter className="w-3 h-3" /> Filter Org:
        </span>
        {organizations.map((org) => (
          <button
            key={org}
            onClick={() => setSelectedOrgFilter(org)}
            className={`px-2.5 py-1 text-3xs font-mono uppercase rounded-2xs transition-colors ${
              selectedOrgFilter === org
                ? 'bg-stone-800 text-white font-semibold'
                : 'bg-stone-100 text-stone-600 hover:bg-stone-200'
            }`}
          >
            {org}
          </button>
        ))}
      </div>

      {/* Document Explorer Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left: Document List */}
        <div className="lg:col-span-5 space-y-2 max-h-[500px] overflow-y-auto pr-1">
          {filteredDocs.map((doc) => {
            const isSelected = doc.id === selectedDocId;
            return (
              <div
                key={doc.id}
                onClick={() => handleSelectDoc(doc.id)}
                className={`p-3 border rounded-sm cursor-pointer transition-all ${
                  isSelected
                    ? 'border-emerald-600 bg-emerald-50/20 shadow-xs ring-1 ring-emerald-500/40'
                    : 'border-stone-200 bg-white hover:border-stone-300 hover:bg-stone-50/50'
                }`}
              >
                <div className="flex items-start justify-between gap-1 mb-1">
                  <span className="text-2xs font-bold text-stone-800 line-clamp-2">
                    {doc.title}
                  </span>
                  <span className="px-1.5 py-0.5 text-3xs font-mono bg-stone-100 text-stone-700 border border-stone-200 rounded-2xs shrink-0">
                    {doc.organization}
                  </span>
                </div>
                <div className="text-3xs text-stone-500 font-mono flex items-center gap-2">
                  <span>{doc.year}</span>
                  <span>•</span>
                  <span>{doc.chunk_count} Chunks</span>
                  <span>•</span>
                  <span className="capitalize">{doc.geographic_scope}</span>
                </div>
              </div>
            );
          })}
        </div>

        {/* Right: Selected Document Chunks & Metadata */}
        <div className="lg:col-span-7">
          {selectedDoc ? (
            <div className="border border-stone-200 rounded-sm bg-stone-50/50 p-4 space-y-4">
              <div>
                <div className="flex items-center gap-2 text-3xs font-mono text-emerald-800 mb-1">
                  <span>{selectedDoc.id}</span>
                  <span>•</span>
                  <span className="uppercase">{selectedDoc.source_type.replace(/_/g, ' ')}</span>
                </div>
                <h3 className="text-sm font-bold text-stone-900">{selectedDoc.title}</h3>
                <p className="text-2xs text-stone-600 mt-1 font-mono">{selectedDoc.authors} ({selectedDoc.year})</p>
              </div>

              {/* Citation & Metadata */}
              <div className="bg-white p-3 border border-stone-200 rounded-sm text-xs space-y-2">
                <div>
                  <span className="text-3xs font-mono text-stone-400 uppercase block">Formal Citation</span>
                  <p className="text-2xs text-stone-800 font-serif">{selectedDoc.citation}</p>
                </div>
                {selectedDoc.doi && (
                  <div className="flex items-center gap-1.5 text-3xs font-mono text-emerald-700">
                    <span>DOI:</span>
                    <a
                      href={`https://doi.org/${selectedDoc.doi}`}
                      target="_blank"
                      rel="noreferrer"
                      className="hover:underline flex items-center gap-1"
                    >
                      {selectedDoc.doi} <ExternalLink className="w-2.5 h-2.5" />
                    </a>
                  </div>
                )}
                {selectedDoc.abstract && (
                  <div className="pt-2 border-t border-stone-100">
                    <span className="text-3xs font-mono text-stone-400 uppercase block">Abstract</span>
                    <p className="text-2xs text-stone-600">{selectedDoc.abstract}</p>
                  </div>
                )}
              </div>

              {/* Chunks List */}
              <div className="space-y-3">
                <h4 className="text-2xs font-mono font-bold uppercase tracking-wider text-stone-600 flex items-center gap-1.5">
                  <FileText className="w-3.5 h-3.5 text-emerald-600" />
                  Indexed Document Passages / Chunks ({selectedDocChunks.length})
                </h4>

                {loadingChunks ? (
                  <div className="p-4 text-center text-xs text-stone-500 font-mono">
                    Loading passages...
                  </div>
                ) : (
                  <div className="space-y-2 max-h-[350px] overflow-y-auto pr-1">
                    {selectedDocChunks.map((chunk) => (
                      <div
                        key={chunk.id}
                        className="bg-white p-3 border border-stone-200 rounded-2xs text-xs space-y-1.5"
                      >
                        <div className="flex items-center justify-between text-3xs font-mono text-stone-500">
                          <span className="font-semibold text-stone-700">
                            {chunk.section || `Chunk ${chunk.chunk_index + 1}`}
                          </span>
                          <span className="text-emerald-700">{chunk.id}</span>
                        </div>
                        <p className="text-2xs text-stone-700 font-serif leading-relaxed">
                          {chunk.content}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="p-8 border border-dashed border-stone-200 rounded-sm text-center text-xs text-stone-500">
              Select a scientific document to view its metadata, full citation, and indexed passages.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
