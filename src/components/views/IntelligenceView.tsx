import React, { useState, useRef } from 'react';
import {
  ArrowRight,
  Sparkles,
  AlertCircle,
  HelpCircle,
  Paperclip,
  MapPin,
  CloudRain,
  Droplets,
  Wheat,
  Sprout,
  ShieldCheck,
  Compass,
  BookOpen,
} from 'lucide-react';
import {
  EnvironmentalState,
  InterventionRecommendation,
  ConversationChatResponse,
  ClarificationQuestionItem,
} from '../../types';
import { sendConversationMessage } from '../../services/api';
import { WorkspaceTab } from '../Sidebar';
import { VasudhaLogo } from '../VasudhaLogo';
import { MistyLandscape } from '../MistyLandscape';
import { IntelligenceRightPanel } from './IntelligenceRightPanel';

interface IntelligenceViewProps {
  currentState: EnvironmentalState;
  onStateSynced: (state: EnvironmentalState) => void;
  onNavigateTab: (tab: WorkspaceTab) => void;
  sessionId: string;
  messages: Array<{ role: 'user' | 'assistant'; content: string }>;
  setMessages: React.Dispatch<
    React.SetStateAction<Array<{ role: 'user' | 'assistant'; content: string }>>
  >;
}

export const IntelligenceView: React.FC<IntelligenceViewProps> = ({
  currentState,
  onStateSynced,
  onNavigateTab,
  sessionId,
  messages,
  setMessages,
}) => {
  const [inputMessage, setInputMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [clarificationQuestions, setClarificationQuestions] = useState<ClarificationQuestionItem[]>([]);
  const [recommendationPreviews, setRecommendationPreviews] = useState<
    InterventionRecommendation[]
  >([]);
  const [attachedFileName, setAttachedFileName] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Dynamic status descriptors based on current environmental state
  const rainfallLevel =
    currentState.climate.rainfall === null || currentState.climate.rainfall === undefined
      ? 'Low'
      : currentState.climate.rainfall < 600
      ? 'Deficit (<600mm)'
      : currentState.climate.rainfall < 1200
      ? 'Moderate'
      : 'High';

  const moistureLevel =
    currentState.soil.moisture === null || currentState.soil.moisture === undefined
      ? 'Low'
      : currentState.soil.moisture < 20
      ? 'Deficit (14%)'
      : currentState.soil.moisture < 40
      ? 'Moderate'
      : 'Adequate';

  const landUseLevel =
    currentState.land.land_use === 'monoculture'
      ? 'Cropland'
      : currentState.land.land_use || 'Cropland';

  const habitatLevel =
    currentState.biodiversity.habitat_diversity === null ||
    currentState.biodiversity.habitat_diversity === undefined
      ? 'Low'
      : currentState.biodiversity.habitat_diversity < 35
      ? 'Fragmented (22/100)'
      : 'Moderate';

  // Check if active user dialogue has started
  const hasUserMessages = messages.some((m) => m.role === 'user');

  const SUGGESTED_QUERIES = [
    { label: 'Assess Nandurbar baseline', query: 'Analyze the Nandurbar benchmark environmental state and identify primary ecological pressures.' },
    { label: 'Why this intervention?', query: 'Explain the causal chain and biophysical mechanisms behind the prescribed agroforestry interventions.' },
    { label: 'Inspect scientific evidence', query: 'What peer-reviewed IPCC and FAO evidence supports carbon recarbonization in semi-arid drylands?' },
    { label: 'Nature risk profile', query: 'What are the critical ecological tipping points and nature risks for this landscape?' },
  ];

  const handleSendMessage = async (textToSend?: string) => {
    const query = (textToSend || inputMessage).trim();
    if (!query || loading) return;

    setInputMessage('');
    setAttachedFileName(null);
    setMessages((prev) => [...prev, { role: 'user', content: query }]);
    setLoading(true);
    setError(null);

    try {
      const res: ConversationChatResponse = await sendConversationMessage(sessionId, query);
      setMessages((prev) => [...prev, { role: 'assistant', content: res.conversational_response }]);
      setClarificationQuestions(res.clarification_questions || []);

      if (res.recommendations && res.recommendations.length > 0) {
        setRecommendationPreviews(res.recommendations.slice(0, 2));
      }

      // Sync environmental state if memory extracted new biophysical signals
      const mem = res.environmental_memory;
      if (mem) {
        const updatedState: EnvironmentalState = {
          soil: {
            ph: mem.soil_ph ?? currentState.soil.ph,
            organic_carbon: mem.soil_organic_carbon ?? currentState.soil.organic_carbon,
            moisture: mem.soil_moisture ?? currentState.soil.moisture,
          },
          land: {
            land_use: mem.land_use ?? currentState.land.land_use,
            land_cover: mem.land_cover ?? currentState.land.land_cover,
          },
          biodiversity: {
            species_richness: mem.species_richness ?? currentState.biodiversity.species_richness,
            habitat_diversity: currentState.biodiversity.habitat_diversity,
          },
          climate: {
            temperature: mem.temperature ?? currentState.climate.temperature,
            rainfall: mem.rainfall ?? currentState.climate.rainfall,
          },
          human_impact: {
            pollution: mem.pollution ?? currentState.human_impact.pollution,
            deforestation: mem.deforestation ?? currentState.human_impact.deforestation,
          },
          spatial_context: currentState.spatial_context,
        };
        onStateSynced(updatedState);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Communication error with intelligence engine');
    } finally {
      setLoading(false);
      setTimeout(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setAttachedFileName(file.name);
      setInputMessage((prev) =>
        prev
          ? `${prev} [Attached: ${file.name}]`
          : `Analyze environmental parameters from ${file.name}:`
      );
    }
  };

  return (
    <div className="relative min-h-[calc(100vh-130px)] flex flex-col lg:flex-row gap-6 lg:gap-8 items-start max-w-7xl mx-auto pb-12">
      {/* Hidden file input */}
      <input
        type="file"
        ref={fileInputRef}
        onChange={handleFileUpload}
        className="hidden"
        accept=".csv,.json,.txt,.pdf"
      />

      {/* Main Center Canvas: The Chatbot & Hero Area */}
      <div className="relative flex-1 w-full min-h-[620px] rounded-3xl overflow-hidden flex flex-col justify-between">
        {/* Watercolor misty landscape background at bottom */}
        <MistyLandscape className="z-0" />

        {/* Content Container */}
        <div className="relative z-10 w-full flex-1 flex flex-col justify-center px-3 sm:px-6 py-6 sm:py-8">
          {/* 1. HERO BRAND SECTION */}
          <div className="flex flex-col items-center text-center max-w-xl mx-auto space-y-4">
            {/* Precision Vasudha Emblem & Wordmark */}
            <VasudhaLogo variant="full" size="xl" theme="light" showTagline={true} />

            {/* Description Subtext */}
            <p className="text-xs sm:text-sm text-[#3d594c] max-w-md mx-auto font-sans leading-relaxed pt-0.5">
              Understand environmental conditions, trace ecological relationships, and discover
              evidence-backed actions for biodiversity.
            </p>

            {/* 4 Status Pills */}
            <div className="flex flex-wrap items-center justify-center gap-2 sm:gap-2.5 pt-1.5">
              <button
                onClick={() => onNavigateTab('environment')}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-[#eef4ee] hover:bg-[#e4ede4] border border-[#d6e2d5] text-[11px] font-medium text-[#234436] shadow-2xs transition-colors cursor-pointer"
                title="View climate rainfall parameters"
              >
                <CloudRain className="w-3.5 h-3.5 text-[#2e5e4b]" />
                <span>Rainfall: {rainfallLevel}</span>
              </button>

              <button
                onClick={() => onNavigateTab('environment')}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-[#eef4ee] hover:bg-[#e4ede4] border border-[#d6e2d5] text-[11px] font-medium text-[#234436] shadow-2xs transition-colors cursor-pointer"
                title="View soil moisture parameters"
              >
                <Droplets className="w-3.5 h-3.5 text-[#2e5e4b]" />
                <span>Soil Moisture: {moistureLevel}</span>
              </button>

              <button
                onClick={() => onNavigateTab('environment')}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-[#eef4ee] hover:bg-[#e4ede4] border border-[#d6e2d5] text-[11px] font-medium text-[#234436] shadow-2xs transition-colors cursor-pointer"
                title="View land use parameters"
              >
                <Wheat className="w-3.5 h-3.5 text-[#2e5e4b]" />
                <span>Land Use: {landUseLevel}</span>
              </button>

              <button
                onClick={() => onNavigateTab('environment')}
                className="inline-flex items-center gap-1.5 px-3 py-1 rounded-xl bg-[#eef4ee] hover:bg-[#e4ede4] border border-[#d6e2d5] text-[11px] font-medium text-[#234436] shadow-2xs transition-colors cursor-pointer"
                title="View biodiversity habitat index"
              >
                <Sprout className="w-3.5 h-3.5 text-[#2e5e4b]" />
                <span>Habitat: {habitatLevel}</span>
              </button>
            </div>
          </div>

          {/* 2. CONVERSATION STREAM */}
          {hasUserMessages && (
            <div className="w-full max-w-2xl mx-auto my-6 space-y-4 max-h-[440px] overflow-y-auto px-1 pr-2">
              {messages
                .filter((msg, idx) => !(idx === 0 && msg.role === 'assistant'))
                .map((msg, idx) => {
                  const isUser = msg.role === 'user';
                  return (
                    <div
                      key={idx}
                      className={`flex ${isUser ? 'justify-end' : 'justify-start'} animate-in fade-in duration-200`}
                    >
                      <div
                        className={`max-w-[88%] sm:max-w-[82%] rounded-2xl p-4 text-xs leading-relaxed space-y-2 shadow-xs ${
                          isUser
                            ? 'bg-[#173b2d] text-white rounded-br-xs'
                            : 'bg-white/95 text-stone-800 border border-stone-200/90 rounded-bl-xs backdrop-blur-xs'
                        }`}
                      >
                        <div className="flex items-center justify-between gap-2 border-b border-white/10 pb-1.5 text-[10px] font-mono opacity-85">
                          <span className="font-bold uppercase tracking-wider">
                            {isUser ? 'Land Steward / Researcher' : 'VASUDHA Intelligence'}
                          </span>
                          {!isUser && (
                            <span className="inline-flex items-center gap-1 text-emerald-800 font-semibold bg-emerald-100/90 px-1.5 py-0.5 rounded-sm">
                              <ShieldCheck className="w-2.5 h-2.5" />
                              Grounded RAG
                            </span>
                          )}
                        </div>
                        <div className="whitespace-pre-wrap font-sans text-xs sm:text-[13px] leading-relaxed">
                          {msg.content}
                        </div>
                      </div>
                    </div>
                  );
                })}

              {loading && (
                <div className="flex justify-start">
                  <div className="bg-white/95 border border-stone-200/90 rounded-2xl rounded-bl-xs p-4 text-xs text-stone-600 font-mono space-y-2 shadow-xs animate-pulse">
                    <div className="flex items-center gap-2 text-emerald-800 font-semibold">
                      <Sparkles className="w-3.5 h-3.5 animate-spin text-emerald-600" />
                      <span>Synthesizing multi-metric ecological relationships...</span>
                    </div>
                    <p className="text-[11px] text-stone-500">
                      Cross-referencing IPCC AR6, FAO GSOCseq, and local biophysical thresholds.
                    </p>
                  </div>
                </div>
              )}

              {/* Clarification banner */}
              {Array.isArray(clarificationQuestions) && clarificationQuestions.length > 0 && (
                <div className="p-3.5 rounded-xl bg-amber-50/95 border border-amber-200 text-xs text-amber-900 space-y-2 shadow-2xs">
                  <div className="flex items-center gap-2 font-semibold text-amber-800">
                    <HelpCircle className="w-4 h-4 text-amber-700" />
                    <span>Ecological Clarification Needed:</span>
                  </div>
                  <div className="space-y-2 pl-1">
                    {clarificationQuestions.map((q, i) => {
                      const text = typeof q === 'string' ? q : q?.question_text || q?.question_id || 'Clarification required';
                      const context = typeof q === 'object' && q ? q.context : null;
                      const suggestions = typeof q === 'object' && q && Array.isArray(q.suggested_answers) ? q.suggested_answers : [];

                      return (
                        <div key={i} className="space-y-1">
                          <div className="font-medium text-amber-950 text-[11px] flex items-start gap-1.5">
                            <span className="text-amber-600 font-bold">•</span>
                            <span>{text}</span>
                          </div>
                          {context && (
                            <p className="text-[10px] text-amber-800/90 pl-3 leading-relaxed">
                              {context}
                            </p>
                          )}
                          {suggestions.length > 0 && (
                            <div className="flex flex-wrap gap-1.5 pt-1 pl-3">
                              {suggestions.map((ans, sIdx) => (
                                <button
                                  key={sIdx}
                                  type="button"
                                  onClick={() => handleSendMessage(ans)}
                                  className="px-2.5 py-1 rounded-lg bg-white hover:bg-amber-100 text-amber-900 text-[10px] font-medium border border-amber-300/80 shadow-2xs transition-colors cursor-pointer"
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
              )}

              {/* Prescribed Interventions Preview */}
              {recommendationPreviews.length > 0 && (
                <div className="bg-emerald-50/90 border border-emerald-200 rounded-2xl p-4 space-y-2.5 shadow-2xs">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-bold text-emerald-950 flex items-center gap-1.5">
                      <Sprout className="w-4 h-4 text-emerald-700" />
                      Prescribed Nature-Based Interventions
                    </span>
                    <button
                      onClick={() => onNavigateTab('actions')}
                      className="text-[11px] text-emerald-800 hover:text-emerald-900 font-semibold underline flex items-center gap-0.5"
                    >
                      View All in Actions <ArrowRight className="w-3 h-3" />
                    </button>
                  </div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                    {recommendationPreviews.map((rec) => (
                      <div
                        key={rec.recommendation_id}
                        onClick={() => onNavigateTab('actions')}
                        className="bg-white p-2.5 rounded-xl border border-emerald-200/80 hover:border-emerald-500 cursor-pointer transition-colors shadow-2xs"
                      >
                        <h4 className="text-xs font-bold text-stone-900 line-clamp-1">{rec.title}</h4>
                        <p className="text-[11px] text-stone-600 line-clamp-2 mt-0.5">{rec.what_to_do}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Error Notice */}
              {error && (
                <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-800 flex items-start gap-2">
                  <AlertCircle className="w-4 h-4 text-rose-600 mt-0.5 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>
          )}

          {/* 3. SUGGESTED BENCHMARK PROMPT PILLS (Before dialogue starts) */}
          {!hasUserMessages && (
            <div className="w-full max-w-2xl mx-auto mt-4 pt-1">
              <div className="flex flex-wrap items-center justify-center gap-2">
                {SUGGESTED_QUERIES.map((item, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => handleSendMessage(item.query)}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-white/90 hover:bg-white border border-stone-200/80 hover:border-emerald-600 text-stone-700 hover:text-emerald-900 text-xs font-medium shadow-2xs transition-all cursor-pointer group"
                  >
                    <Sparkles className="w-3 h-3 text-emerald-600 group-hover:rotate-12 transition-transform" />
                    <span>{item.label}</span>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* 4. FLOATING CHAT INPUT BOX */}
          <div className="w-full max-w-2xl mx-auto mt-5">
            <div className="bg-white rounded-2xl sm:rounded-[22px] border border-stone-200/90 shadow-xs hover:shadow-md p-3.5 sm:p-4 space-y-3 transition-all focus-within:shadow-md focus-within:border-emerald-700/50">
              {/* Textarea */}
              <textarea
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                disabled={loading}
                rows={2}
                placeholder="Ask VASUDHA about your environment..."
                className="w-full resize-none bg-transparent text-sm text-stone-900 placeholder:text-stone-400 focus:outline-hidden font-sans"
              />

              {/* Attached file chip if any */}
              {attachedFileName && (
                <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md bg-stone-100 text-[11px] text-stone-700 font-mono">
                  <Paperclip className="w-3 h-3 text-stone-500" />
                  <span>{attachedFileName}</span>
                  <button
                    onClick={() => setAttachedFileName(null)}
                    className="text-stone-400 hover:text-stone-700 ml-1 cursor-pointer"
                  >
                    ×
                  </button>
                </div>
              )}

              {/* Bottom Action Row */}
              <div className="flex items-center justify-between pt-1">
                <div className="flex items-center gap-1.5 sm:gap-2">
                  {/* Attachment Icon Button */}
                  <button
                    type="button"
                    onClick={() => fileInputRef.current?.click()}
                    className="p-1.5 rounded-lg text-stone-500 hover:text-stone-800 hover:bg-stone-100 transition-colors cursor-pointer"
                    title="Attach ecological survey / soil dataset (.csv, .json, .txt)"
                  >
                    <Paperclip className="w-4 h-4" />
                  </button>

                  {/* Location Icon Button */}
                  <button
                    type="button"
                    onClick={() => onNavigateTab('location')}
                    className="p-1.5 rounded-lg text-stone-500 hover:text-stone-800 hover:bg-stone-100 transition-colors cursor-pointer"
                    title="View & select geographic parcel context"
                  >
                    <MapPin className="w-4 h-4" />
                  </button>
                </div>

                {/* Submit Button */}
                <button
                  type="button"
                  onClick={() => handleSendMessage()}
                  disabled={loading || !inputMessage.trim()}
                  className="w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-[#163b2c] hover:bg-[#0f2a20] disabled:opacity-40 disabled:hover:bg-[#163b2c] text-white flex items-center justify-center transition-all shadow-xs cursor-pointer"
                  title="Send message to VASUDHA"
                >
                  <ArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Column: Location, Quick Actions, Recent Analysis Panel */}
      <div className="w-full lg:w-80 shrink-0">
        <IntelligenceRightPanel
          spatialContext={currentState.spatial_context}
          currentState={currentState}
          onNavigateTab={onNavigateTab}
          onTriggerQuickAction={(actionName) => {
            handleSendMessage(`Perform ${actionName} for this ecological context.`);
          }}
          onSelectRecentAnalysis={(title) => {
            handleSendMessage(`Inspect recent assessment: ${title}`);
          }}
        />
      </div>
    </div>
  );
};
