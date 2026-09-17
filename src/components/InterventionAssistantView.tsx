/**
 * Phase 14: Conversational Environmental Intelligence & Recommendation Assistant View
 * Integrates multi-turn conversation memory, structured environmental data, map context,
 * and comprehensive evidence-backed intervention recommendations with full explainability.
 */

import React, { useState, useEffect } from 'react';
import {
  EnvironmentalState,
  InterventionRecommendation,
  ConversationChatResponse,
  ClarificationQuestionItem,
} from '../types';
import {
  sendConversationMessage,
  generateInterventions,
  resetSessionMemory,
} from '../services/api';
import { GeoContextMap } from './GeoContextMap';

interface Props {
  currentState: EnvironmentalState;
  onStateSynced: (state: EnvironmentalState) => void;
}

export const InterventionAssistantView: React.FC<Props> = ({ currentState, onStateSynced }) => {
  const [sessionId] = useState<string>(() => `session_${Math.random().toString(36).substring(2, 9)}`);
  const [messages, setMessages] = useState<Array<{ role: 'user' | 'assistant'; content: string }>>([
    {
      role: 'assistant',
      content: 'Hello! I am your AI ecological intelligence assistant. Describe your environmental problem, share site conditions, or ask for intervention recommendations.',
    },
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [recommendations, setRecommendations] = useState<InterventionRecommendation[]>([]);
  const [selectedRecId, setSelectedRecId] = useState<string | null>(null);
  const [clarificationQuestions, setClarificationQuestions] = useState<ClarificationQuestionItem[]>([]);
  const [detectedConflicts, setDetectedConflicts] = useState<string[]>([]);
  const [activeTab, setActiveTab] = useState<'assistant' | 'recommendations' | 'state' | 'map'>('recommendations');

  // Load initial recommendations on mount or state change
  useEffect(() => {
    loadRecommendations(currentState);
  }, [currentState]);

  const loadRecommendations = async (state: EnvironmentalState) => {
    try {
      setLoading(true);
      setError(null);
      const res = await generateInterventions({ state, max_recommendations: 5 });
      setRecommendations(res.recommendations || []);
      if (res.recommendations && res.recommendations.length > 0 && !selectedRecId) {
        setSelectedRecId(res.recommendations[0].recommendation_id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate recommendations');
    } finally {
      setLoading(false);
    }
  };

  const submitMessage = async (msg: string) => {
    if (!msg.trim() || loading) return;

    const userMsg = msg.trim();
    setInputMessage('');
    setMessages((prev) => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);
    setError(null);

    try {
      const res: ConversationChatResponse = await sendConversationMessage(sessionId, userMsg);
      setMessages((prev) => [...prev, { role: 'assistant', content: res.conversational_response }]);
      setClarificationQuestions(res.clarification_questions || []);
      setDetectedConflicts(res.detected_conflicts || []);

      if (res.recommendations && res.recommendations.length > 0) {
        setRecommendations(res.recommendations);
        setSelectedRecId(res.recommendations[0].recommendation_id);
      }

      // If environmental memory updated, construct and sync updated state
      const mem = res.environmental_memory;
      const updatedState: EnvironmentalState = {
        soil: {
          ph: mem.soil_ph !== null && mem.soil_ph !== undefined ? mem.soil_ph : currentState.soil.ph,
          organic_carbon: mem.soil_organic_carbon !== null && mem.soil_organic_carbon !== undefined ? mem.soil_organic_carbon : currentState.soil.organic_carbon,
          moisture: mem.soil_moisture !== null && mem.soil_moisture !== undefined ? mem.soil_moisture : currentState.soil.moisture,
        },
        land: {
          land_use: mem.land_use !== null && mem.land_use !== undefined ? mem.land_use : currentState.land.land_use,
          land_cover: mem.land_cover !== null && mem.land_cover !== undefined ? mem.land_cover : currentState.land.land_cover,
        },
        biodiversity: {
          species_richness: mem.species_richness !== null && mem.species_richness !== undefined ? mem.species_richness : currentState.biodiversity.species_richness,
          habitat_diversity: currentState.biodiversity.habitat_diversity,
        },
        climate: {
          temperature: mem.temperature !== null && mem.temperature !== undefined ? mem.temperature : currentState.climate.temperature,
          rainfall: mem.rainfall !== null && mem.rainfall !== undefined ? mem.rainfall : currentState.climate.rainfall,
        },
        human_impact: {
          pollution: mem.pollution !== null && mem.pollution !== undefined ? mem.pollution : currentState.human_impact.pollution,
          deforestation: mem.deforestation !== null && mem.deforestation !== undefined ? mem.deforestation : currentState.human_impact.deforestation,
        },
        spatial_context: currentState.spatial_context,
      };
      onStateSynced(updatedState);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Chat request failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    await submitMessage(inputMessage);
  };

  const handleResetSession = async () => {
    try {
      await resetSessionMemory(sessionId);
      setMessages([
        {
          role: 'assistant',
          content: 'Session memory reset. How can I help you analyze your ecosystem today?',
        },
      ]);
      setClarificationQuestions([]);
      setDetectedConflicts([]);
    } catch (err) {
      setError('Failed to reset session');
    }
  };

  const selectedRec = recommendations.find((r) => r.recommendation_id === selectedRecId) || recommendations[0];

  return (
    <div className="bg-white rounded-2xl border border-stone-200/80 shadow-xs overflow-hidden">
      {/* Header & Tabs */}
      <div className="bg-stone-50 border-b border-stone-200 p-4 sm:px-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-mono font-medium bg-emerald-100 text-emerald-800">
              Phase 13–14 Active
            </span>
            <h2 className="text-base font-bold text-stone-900 tracking-tight">
              Conversational Environmental Intelligence Assistant
            </h2>
          </div>
          <p className="text-xs text-stone-500 mt-0.5">
            Multi-turn memory, clarification routing, explainable ecological reasoning, and evidence validation.
          </p>
        </div>

        <div className="flex items-center gap-2 bg-stone-200/70 p-1 rounded-xl text-xs font-medium">
          <button
            onClick={() => setActiveTab('recommendations')}
            className={`px-3 py-1.5 rounded-lg transition-colors ${
              activeTab === 'recommendations' ? 'bg-white text-stone-900 shadow-xs' : 'text-stone-600 hover:text-stone-900'
            }`}
          >
            Recommendations ({recommendations.length})
          </button>
          <button
            onClick={() => setActiveTab('assistant')}
            className={`px-3 py-1.5 rounded-lg transition-colors ${
              activeTab === 'assistant' ? 'bg-white text-stone-900 shadow-xs' : 'text-stone-600 hover:text-stone-900'
            }`}
          >
            Chat Assistant
          </button>
          <button
            onClick={() => setActiveTab('state')}
            className={`px-3 py-1.5 rounded-lg transition-colors ${
              activeTab === 'state' ? 'bg-white text-stone-900 shadow-xs' : 'text-stone-600 hover:text-stone-900'
            }`}
          >
            Environmental Data
          </button>
          <button
            onClick={() => setActiveTab('map')}
            className={`px-3 py-1.5 rounded-lg transition-colors ${
              activeTab === 'map' ? 'bg-white text-stone-900 shadow-xs' : 'text-stone-600 hover:text-stone-900'
            }`}
          >
            Interactive Map
          </button>
        </div>
      </div>

      {error && (
        <div className="bg-rose-50 border-b border-rose-200 p-3 px-6 text-xs text-rose-700 flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError(null)} className="font-bold underline hover:text-rose-900">Dismiss</button>
        </div>
      )}

      {/* Clarification or Conflict Banner */}
      {(clarificationQuestions.length > 0 || detectedConflicts.length > 0) && (
        <div className="bg-amber-50 border-b border-amber-200 p-4 px-6 text-xs text-amber-900 space-y-2">
          {detectedConflicts.length > 0 && (
            <div className="flex items-start gap-2">
              <span className="font-bold text-amber-800 uppercase tracking-wider text-[10px] mt-0.5">Conflict Notice:</span>
              <p>{detectedConflicts.join(' ')}</p>
            </div>
          )}
          {clarificationQuestions.length > 0 && (
            <div className="flex items-start gap-2">
              <span className="font-bold text-amber-800 uppercase tracking-wider text-[10px] mt-0.5">Clarification Needed:</span>
              <div className="space-y-1.5 flex-1">
                <p>To provide high-precision recommendations, please address:</p>
                <div className="mt-1 space-y-2 text-amber-900">
                  {Array.isArray(clarificationQuestions) && clarificationQuestions.map((q, idx) => {
                    const text = typeof q === 'string' ? q : q?.question_text || q?.question_id || 'Clarification required';
                    const context = typeof q === 'object' && q ? q.context : null;
                    const suggestions = typeof q === 'object' && q && Array.isArray(q.suggested_answers) ? q.suggested_answers : [];

                    return (
                      <div key={idx} className="space-y-1">
                        <div className="font-medium text-amber-950 text-xs flex items-start gap-1.5">
                          <span className="text-amber-600 font-bold">•</span>
                          <span>{text}</span>
                        </div>
                        {context && (
                          <p className="text-[11px] text-amber-800/90 pl-3 leading-relaxed">
                            {context}
                          </p>
                        )}
                        {suggestions.length > 0 && (
                          <div className="flex flex-wrap gap-1.5 pt-1 pl-3">
                            {suggestions.map((ans, sIdx) => (
                              <button
                                key={sIdx}
                                type="button"
                                onClick={() => submitMessage(ans)}
                                className="px-2 py-0.5 rounded-md bg-amber-100 hover:bg-amber-200 text-amber-900 text-[10px] border border-amber-300 font-medium transition-colors cursor-pointer"
                              >
                                {ans}
                              </button>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      <div className="p-6">
        {/* Tab 1: Recommendations & Explainability */}
        {activeTab === 'recommendations' && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
            {/* Left: List of Recommendations */}
            <div className="lg:col-span-5 space-y-3">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-stone-600">
                  Ranked Interventions ({recommendations.length})
                </h3>
                <button
                  onClick={() => loadRecommendations(currentState)}
                  disabled={loading}
                  className="text-xs text-emerald-700 hover:text-emerald-800 font-medium underline"
                >
                  {loading ? 'Evaluating...' : 'Refresh'}
                </button>
              </div>

              {loading && recommendations.length === 0 ? (
                <div className="text-center py-12 text-stone-400 text-xs font-mono animate-pulse">
                  Synthesizing multi-metric reasoning & evidence...
                </div>
              ) : recommendations.length === 0 ? (
                <div className="text-center py-12 text-stone-500 text-xs">
                  No matching interventions found for current parameters. Try adding rainfall or soil data.
                </div>
              ) : (
                recommendations.map((rec, idx) => {
                  const isSelected = rec.recommendation_id === selectedRecId;
                  return (
                    <div
                      key={rec.recommendation_id}
                      onClick={() => setSelectedRecId(rec.recommendation_id)}
                      className={`p-4 rounded-xl border transition-all cursor-pointer text-left ${
                        isSelected
                          ? 'border-emerald-500 bg-emerald-50/40 shadow-xs ring-1 ring-emerald-500/20'
                          : 'border-stone-200 bg-white hover:border-stone-300 hover:bg-stone-50/50'
                      }`}
                    >
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-stone-100 text-stone-700 font-medium">
                          #{idx + 1} • {rec.category}
                        </span>
                        <span className="text-[10px] font-mono text-emerald-700 font-bold">
                          Conf: {(rec.confidence_basis.overall_confidence * 100).toFixed(0)}%
                        </span>
                      </div>
                      <h4 className="text-sm font-bold text-stone-900 mb-1">{rec.title}</h4>
                      <p className="text-xs text-stone-600 line-clamp-2">{rec.what_to_do}</p>
                      <div className="mt-3 flex items-center justify-between text-[11px] text-stone-500 font-mono">
                        <span>Horizon: {rec.time_horizon}</span>
                        <span className="text-emerald-700 font-medium">Feasibility: {rec.feasibility.status}</span>
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            {/* Right: Detailed Selected Recommendation Inspector */}
            <div className="lg:col-span-7 bg-stone-50/60 rounded-2xl border border-stone-200/80 p-6 space-y-6">
              {selectedRec ? (
                <div className="space-y-6">
                  {/* Title & Category */}
                  <div className="border-b border-stone-200 pb-4">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="text-xs font-mono uppercase tracking-wider px-2.5 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-semibold">
                        {selectedRec.category}
                      </span>
                      <span className="text-xs font-mono text-stone-500">
                        ID: {selectedRec.recommendation_id}
                      </span>
                    </div>
                    <h3 className="text-xl font-bold text-stone-900">{selectedRec.title}</h3>
                    <p className="text-sm text-stone-700 mt-2 font-medium">{selectedRec.what_to_do}</p>
                  </div>

                  {/* 1. Why this intervention? (Explanation Chain) */}
                  <div className="bg-white rounded-xl p-4 border border-stone-200 space-y-3">
                    <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-emerald-800">
                      Why this intervention? (Explainability Chain)
                    </h4>
                    <div className="text-xs text-stone-700 space-y-2">
                      <p><strong className="text-stone-900">Ecological Pressure:</strong> {selectedRec.explanation_chain.ecological_pressure}</p>
                      <p><strong className="text-stone-900">Mechanistic Rationale:</strong> {selectedRec.explanation_chain.ecological_mechanism}</p>
                      {selectedRec.explanation_chain.scientific_evidence_summary.length > 0 && (
                        <div>
                          <span className="font-semibold text-stone-900">Literature Summary:</span>
                          <ul className="list-disc list-inside mt-1 space-y-1 text-stone-600">
                            {selectedRec.explanation_chain.scientific_evidence_summary.map((sum, i) => (
                              <li key={i}>{sum}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* 2. Impacted Metrics & Quantitative Effects */}
                  <div className="bg-white rounded-xl p-4 border border-stone-200 space-y-3">
                    <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-stone-700">
                      Impacted Metrics & Expected Effects
                    </h4>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {selectedRec.impacted_metrics.map((eff, i) => (
                        <div key={i} className="p-2.5 rounded-lg bg-stone-50 border border-stone-200 text-xs flex items-center justify-between">
                          <span className="font-medium text-stone-800">{eff.metric_name}</span>
                          <span className={`font-mono px-2 py-0.5 rounded text-[10px] ${
                            eff.direction === 'increase' ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
                          }`}>
                            {eff.direction} ({eff.magnitude})
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* 3. Feasibility & Confidence */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="bg-white rounded-xl p-4 border border-stone-200 space-y-2">
                      <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-stone-700">
                        Feasibility Assessment
                      </h4>
                      <p className="text-xs font-semibold text-emerald-700">{selectedRec.feasibility.status}</p>
                      <p className="text-xs text-stone-600">{selectedRec.feasibility.reason}</p>
                    </div>
                    <div className="bg-white rounded-xl p-4 border border-stone-200 space-y-2">
                      <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-stone-700">
                        Confidence Basis & Evidence
                      </h4>
                      <p className="text-xs font-semibold text-stone-900">
                        Grade: {selectedRec.confidence_basis.evidence_grade} ({(selectedRec.confidence_basis.overall_confidence * 100).toFixed(0)}%)
                      </p>
                      <p className="text-xs text-stone-600">{selectedRec.confidence_basis.justification_summary}</p>
                    </div>
                  </div>

                  {/* 4. Trade-offs & Limitations */}
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="bg-white rounded-xl p-4 border border-stone-200 space-y-2">
                      <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-amber-800">
                        Context-Specific Trade-offs
                      </h4>
                      <ul className="list-disc list-inside text-xs text-stone-700 space-y-1">
                        {selectedRec.tradeoffs.map((t, i) => (
                          <li key={i}>{t}</li>
                        ))}
                      </ul>
                    </div>
                    <div className="bg-white rounded-xl p-4 border border-stone-200 space-y-2">
                      <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-rose-800">
                        Operational Limitations
                      </h4>
                      <ul className="list-disc list-inside text-xs text-stone-700 space-y-1">
                        {selectedRec.limitations.map((l, i) => (
                          <li key={i}>{l}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-20 text-stone-400 text-xs">Select a recommendation to inspect details.</div>
              )}
            </div>
          </div>
        )}

        {/* Tab 2: Conversational Chat Assistant */}
        {activeTab === 'assistant' && (
          <div className="max-w-3xl mx-auto space-y-6">
            <div className="flex items-center justify-between border-b border-stone-200 pb-3">
              <div>
                <h3 className="text-sm font-bold text-stone-900">Multi-Turn Environmental Chat</h3>
                <p className="text-xs text-stone-500">Session ID: {sessionId}</p>
              </div>
              <button
                onClick={handleResetSession}
                className="text-xs font-medium text-stone-600 hover:text-stone-900 underline"
              >
                Reset Session
              </button>
            </div>

            {/* Chat History */}
            <div className="space-y-4 max-h-[500px] overflow-y-auto p-4 bg-stone-50 rounded-xl border border-stone-200">
              {messages.map((msg, idx) => (
                <div
                  key={idx}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl p-4 text-xs leading-relaxed ${
                      msg.role === 'user'
                        ? 'bg-emerald-700 text-white rounded-br-xs'
                        : 'bg-white text-stone-800 border border-stone-200 rounded-bl-xs shadow-xs'
                    }`}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-white text-stone-500 border border-stone-200 rounded-2xl p-3 text-xs animate-pulse">
                    Analyzing ecological state & retrieving literature...
                  </div>
                </div>
              )}
            </div>

            {/* Chat Input */}
            <form onSubmit={handleSendMessage} className="flex gap-2">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask e.g. 'What if rainfall is 400mm?' or 'How does agroforestry improve soil carbon?'..."
                className="flex-1 bg-white border border-stone-300 rounded-xl px-4 py-3 text-xs text-stone-900 focus:outline-hidden focus:ring-2 focus:ring-emerald-500"
              />
              <button
                type="submit"
                disabled={loading || !inputMessage.trim()}
                className="bg-emerald-700 hover:bg-emerald-800 text-white px-6 py-3 rounded-xl text-xs font-semibold disabled:opacity-50 transition-colors shadow-xs"
              >
                Send
              </button>
            </form>
          </div>
        )}

        {/* Tab 3: Environmental Data Summary */}
        {activeTab === 'state' && (
          <div className="space-y-6">
            <h3 className="text-sm font-bold text-stone-900">Structured Environmental Data Panel</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="p-4 rounded-xl border border-stone-200 bg-stone-50 space-y-2">
                <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-stone-700">Soil Metrics</h4>
                <p className="text-xs text-stone-600">pH: {currentState.soil.ph ?? <span className="text-amber-600 font-semibold">Unknown</span>}</p>
                <p className="text-xs text-stone-600">Organic Carbon: {currentState.soil.organic_carbon !== null && currentState.soil.organic_carbon !== undefined ? `${currentState.soil.organic_carbon}%` : <span className="text-amber-600 font-semibold">Unknown</span>}</p>
                <p className="text-xs text-stone-600">Moisture: {currentState.soil.moisture !== null && currentState.soil.moisture !== undefined ? `${currentState.soil.moisture}%` : <span className="text-amber-600 font-semibold">Unknown</span>}</p>
              </div>

              <div className="p-4 rounded-xl border border-stone-200 bg-stone-50 space-y-2">
                <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-stone-700">Land & Climate</h4>
                <p className="text-xs text-stone-600">Land Use: {currentState.land.land_use ?? <span className="text-amber-600 font-semibold">Unknown</span>}</p>
                <p className="text-xs text-stone-600">Rainfall: {currentState.climate.rainfall !== null && currentState.climate.rainfall !== undefined ? `${currentState.climate.rainfall} mm` : <span className="text-amber-600 font-semibold">Unknown</span>}</p>
                <p className="text-xs text-stone-600">Temperature: {currentState.climate.temperature !== null && currentState.climate.temperature !== undefined ? `${currentState.climate.temperature}°C` : <span className="text-amber-600 font-semibold">Unknown</span>}</p>
              </div>

              <div className="p-4 rounded-xl border border-stone-200 bg-stone-50 space-y-2">
                <h4 className="text-xs font-mono font-bold uppercase tracking-wider text-stone-700">Biodiversity & Impact</h4>
                <p className="text-xs text-stone-600">Species Richness: {currentState.biodiversity.species_richness ?? <span className="text-amber-600 font-semibold">Unknown</span>}</p>
                <p className="text-xs text-stone-600">Habitat Diversity: {currentState.biodiversity.habitat_diversity ?? <span className="text-amber-600 font-semibold">Unknown</span>}</p>
                <p className="text-xs text-stone-600">Deforestation: {currentState.human_impact.deforestation !== null && currentState.human_impact.deforestation !== undefined ? `${currentState.human_impact.deforestation}%` : <span className="text-amber-600 font-semibold">Unknown</span>}</p>
              </div>
            </div>
          </div>
        )}

        {/* Tab 4: Interactive Map */}
        {activeTab === 'map' && (
          <div className="space-y-4">
            <h3 className="text-sm font-bold text-stone-900">Geographic Context & Spatial Resolution</h3>
            <GeoContextMap
              spatialContext={currentState.spatial_context}
              onSpatialChange={(spatial) => {
                onStateSynced({
                  ...currentState,
                  spatial_context: spatial,
                });
              }}
            />
          </div>
        )}
      </div>
    </div>
  );
};
