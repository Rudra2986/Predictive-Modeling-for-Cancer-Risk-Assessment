"use client";

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, Send, Bot, User, Loader, HelpCircle, Activity, Sparkles, Dumbbell, Plus, Trash2, ThumbsUp, ThumbsDown, Check } from 'lucide-react';
import { api, getToken } from '@/utils/api';

export default function ChatbotPage() {
  const router = useRouter();
  const messagesEndRef = useRef(null);
  
  const [sessions, setSessions] = useState([]);
  const [activeSessionUuid, setActiveSessionUuid] = useState(null);
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'bot',
      text: "Hello! I am your OncoRisk AI Health Assistant. I am here to help you understand your cancer risk assessments, explain the SHAP contributing factors, and provide educational lifestyle guidelines.\n\nWhat would you like to discuss today?",
      confidence: 'HIGH',
      sources: [],
      suggestions: [],
      feedbackType: null
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [sessionListLoading, setSessionListLoading] = useState(false);
  const [error, setError] = useState('');

  // Suggestions for fast clinician queries (initial state only)
  const suggestionChips = [
    { label: "Why did I get my risk level?", icon: Sparkles },
    { label: "What lifestyle improvements should I make?", icon: Dumbbell },
    { label: "What screenings should I consider?", icon: Activity },
    { label: "General cancer risk factors", icon: HelpCircle }
  ];

  // Fetch all sessions
  const fetchSessions = async (selectLatest = false) => {
    setSessionListLoading(true);
    try {
      const list = await api.get('/chatbot/sessions');
      setSessions(list);
      if (selectLatest && list.length > 0) {
        setActiveSessionUuid(list[0].session_uuid);
        fetchSessionMessages(list[0].session_uuid);
      }
    } catch (err) {
      setError(err.message || 'Failed to retrieve chat sessions.');
    } finally {
      setSessionListLoading(false);
    }
  };

  // Fetch historical messages for a session
  const fetchSessionMessages = async (sessionUuid) => {
    setLoading(true);
    setError('');
    try {
      const msgs = await api.get(`/chatbot/sessions/${sessionUuid}/messages`);
      const mapped = msgs.map((m, index) => ({
        id: m.id || `${m.role}-${index}`,
        sender: m.role === 'user' ? 'user' : 'bot',
        text: m.message,
        confidence: m.confidence,
        sources: m.sources || [],
        suggestions: m.suggestions || [],
        feedbackType: m.feedback_type
      }));
      if (mapped.length === 0) {
        setMessages([
          {
            id: 'welcome',
            sender: 'bot',
            text: "Hello! I am your OncoRisk AI Health Assistant. I am here to help you understand your cancer risk assessments, explain the SHAP contributing factors, and provide educational lifestyle guidelines.\n\nWhat would you like to discuss today?",
            confidence: 'HIGH',
            sources: [],
            suggestions: [],
            feedbackType: null
          }
        ]);
      } else {
        setMessages(mapped);
      }
    } catch (err) {
      setError(err.message || 'Failed to load messages for this session.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = getToken();
    if (!token) {
      router.push('/login');
    } else {
      fetchSessions(true);
    }
  }, [router]);

  // Scroll to bottom helper
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleNewChat = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await api.post('/chatbot/sessions', { title: 'New Chat' });
      const newSess = {
        session_uuid: response.session_uuid,
        title: response.title,
        created_at: new Date().toISOString()
      };
      setSessions(prev => [newSess, ...prev]);
      setActiveSessionUuid(response.session_uuid);
      setMessages([
        {
          id: 'welcome',
          sender: 'bot',
          text: "Hello! I am your OncoRisk AI Health Assistant. I am here to help you understand your cancer risk assessments, explain the SHAP contributing factors, and provide educational lifestyle guidelines.\n\nWhat would you like to discuss today?",
          confidence: 'HIGH',
          sources: [],
          suggestions: [],
          feedbackType: null
        }
      ]);
    } catch (err) {
      setError(err.message || 'Failed to create a new session. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSession = async (sessionUuid, e) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this session?")) return;
    try {
      await api.delete(`/chatbot/sessions/${sessionUuid}`);
      setSessions(prev => prev.filter(s => s.session_uuid !== sessionUuid));
      if (activeSessionUuid === sessionUuid) {
        const remaining = sessions.filter(s => s.session_uuid !== sessionUuid);
        if (remaining.length > 0) {
          setActiveSessionUuid(remaining[0].session_uuid);
          fetchSessionMessages(remaining[0].session_uuid);
        } else {
          setActiveSessionUuid(null);
          setMessages([
            {
              id: 'welcome',
              sender: 'bot',
              text: "Hello! I am your OncoRisk AI Health Assistant. I am here to help you understand your cancer risk assessments, explain the SHAP contributing factors, and provide educational lifestyle guidelines.\n\nWhat would you like to discuss today?",
              confidence: 'HIGH',
              sources: [],
              suggestions: [],
              feedbackType: null
            }
          ]);
        }
      }
    } catch (err) {
      setError(err.message || 'Failed to delete the session.');
    }
  };

  const handleFeedback = async (messageId, feedbackType) => {
    if (!messageId || messageId === 'welcome') return;
    try {
      await api.post('/chatbot/feedback', {
        message_id: messageId,
        feedback_type: feedbackType
      });
      setMessages(prev => prev.map(msg => {
        if (msg.id === messageId) {
          return { ...msg, feedbackType };
        }
        return msg;
      }));
    } catch (err) {
      setError(err.message || 'Failed to submit feedback.');
    }
  };

  const handleSend = async (textToSend) => {
    const queryText = textToSend || input.trim();
    if (!queryText) return;

    setError('');
    if (!textToSend) setInput('');

    // Append user message
    const userMsg = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: queryText
    };
    setMessages(prev => [...prev, userMsg]);
    setLoading(true);

    try {
      const payload = { message: queryText };
      if (activeSessionUuid) {
        payload.session_uuid = activeSessionUuid;
      }
      
      const response = await api.post('/chatbot/message', payload);
      
      const botMsg = {
        id: response.message_id || `bot-${Date.now()}`,
        sender: 'bot',
        text: response.answer,
        confidence: response.confidence,
        sources: response.sources || [],
        suggestions: response.suggestions || [],
        feedbackType: null
      };
      setMessages(prev => [...prev, botMsg]);

      // If this was the first user message in the session, refresh the sessions list to pull the generated title
      const isFirstUserMessage = messages.filter(m => m.sender === 'user').length === 0;
      if (isFirstUserMessage) {
        fetchSessions(activeSessionUuid ? false : true);
      }
    } catch (err) {
      setError(err.message || 'Failed to communicate with chatbot service. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const getConfidenceBadge = (level) => {
    if (level === 'HIGH') {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[9px] font-bold uppercase tracking-wider bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
          Personalized Analysis
        </span>
      );
    }
    if (level === 'MEDIUM') {
      return (
        <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[9px] font-bold uppercase tracking-wider bg-amber-500/10 text-amber-400 border border-amber-500/20">
          Educational Guidance
        </span>
      );
    }
    return (
      <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[9px] font-bold uppercase tracking-wider bg-red-500/10 text-red-400 border border-red-500/20">
        General Context
      </span>
    );
  };

  return (
    <div className="flex flex-col md:flex-row h-[calc(100vh-10rem)] max-w-6xl mx-auto gap-6 bg-slate-50/50 dark:bg-slate-900/10 p-2 rounded-3xl border border-slate-200/50 dark:border-slate-800/40 backdrop-blur-xl shadow-lg">
      
      {/* Sessions Sidebar - Left side on desktop, hidden on mobile */}
      <div className="w-72 bg-white/70 dark:bg-slate-950/70 border border-slate-200/60 dark:border-slate-900 rounded-2xl p-4 flex flex-col justify-between flex-shrink-0 h-full hidden md:flex backdrop-blur-md shadow-sm">
        <div className="space-y-4 flex-1 flex flex-col min-h-0">
          <button
            onClick={handleNewChat}
            className="w-full px-4 py-3 text-sm font-bold rounded-xl border border-dashed border-brand-500/30 hover:border-brand-500 bg-brand-50/20 dark:bg-brand-500/5 hover:bg-brand-50/50 dark:hover:bg-brand-500/10 text-brand-600 dark:text-brand-400 transition-all flex items-center justify-center space-x-2 active:scale-95"
          >
            <Plus className="h-4 w-4" />
            <span>New Chat Session</span>
          </button>
          
          <div className="flex-shrink-0 text-[10px] font-bold text-slate-400 uppercase tracking-wider px-1">
            Recent Conversations
          </div>

          <div className="flex-1 overflow-y-auto min-h-0 space-y-1.5 custom-scrollbar pr-1">
            {sessionListLoading ? (
              <div className="flex items-center justify-center h-20 text-xs text-slate-400">
                <Loader className="h-4.5 w-4.5 animate-spin mr-2 text-brand-500" />
                <span>Loading sessions...</span>
              </div>
            ) : sessions.length === 0 ? (
              <div className="text-center text-xs text-slate-400/80 py-8">
                No chat history found
              </div>
            ) : (
              sessions.map((sess) => (
                <div
                  key={sess.session_uuid}
                  onClick={() => {
                    setActiveSessionUuid(sess.session_uuid);
                    fetchSessionMessages(sess.session_uuid);
                  }}
                  className={`group flex items-center justify-between px-3 py-2.5 rounded-xl cursor-pointer transition-all border ${
                    activeSessionUuid === sess.session_uuid
                      ? 'bg-brand-500/10 dark:bg-brand-500/20 border-brand-500/30 text-brand-700 dark:text-brand-300 font-semibold'
                      : 'border-transparent text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-900/60'
                  }`}
                >
                  <div className="flex items-center space-x-2.5 truncate">
                    <MessageSquare className={`h-4 w-4 flex-shrink-0 ${
                      activeSessionUuid === sess.session_uuid ? 'text-brand-500' : 'text-slate-400 group-hover:text-slate-500'
                    }`} />
                    <span className="text-xs truncate">{sess.title}</span>
                  </div>
                  <button
                    onClick={(e) => handleDeleteSession(sess.session_uuid, e)}
                    className="p-1 rounded-md text-slate-400 hover:text-red-500 dark:hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
                    title="Delete session"
                  >
                    <Trash2 className="h-3.5 w-3.5" />
                  </button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Main Chat Assistant Interface - Right side */}
      <div className="flex-1 flex flex-col justify-between h-full bg-white/40 dark:bg-slate-950/20 border border-slate-200/50 dark:border-slate-900 rounded-2xl p-4 min-w-0">
        
        {/* Mobile Sessions Selector Dropdown - only visible on mobile */}
        {sessions.length > 0 && (
          <div className="md:hidden flex-shrink-0 mb-3">
            <label className="block text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-1">Select Chat Session:</label>
            <div className="flex gap-2 items-center">
              <select
                value={activeSessionUuid || ''}
                onChange={(e) => {
                  const val = e.target.value;
                  if (val) {
                    setActiveSessionUuid(val);
                    fetchSessionMessages(val);
                  }
                }}
                className="flex-1 text-xs bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl px-3 py-2 text-slate-600 dark:text-slate-400 font-medium"
              >
                {sessions.map(s => (
                  <option key={s.session_uuid} value={s.session_uuid}>{s.title}</option>
                ))}
              </select>
              <button
                onClick={handleNewChat}
                className="p-2 rounded-xl border border-slate-200 dark:border-slate-800 text-brand-600 dark:text-brand-400 bg-white dark:bg-slate-900 active:scale-95"
                title="New session"
              >
                <Plus className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}

        {/* Page Header */}
        <div className="pb-3.5 border-b border-slate-200/60 dark:border-slate-900 flex-shrink-0 flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-extrabold text-slate-800 dark:text-white flex items-center space-x-2">
              <MessageSquare className="h-6 w-6 text-brand-600 dark:text-brand-500" />
              <span>Chat Assistant</span>
            </h1>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              Discuss clinical variables, lifestyle choices, and get educational screening insights
            </p>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 dark:bg-red-950/20 border border-red-200/50 dark:border-red-900/30 text-red-600 dark:text-red-400 text-xs p-3 rounded-xl flex items-center space-x-2 flex-shrink-0 mt-3">
            <span>{error}</span>
          </div>
        )}

        {/* Messages Window */}
        <div className="flex-1 overflow-y-auto p-4 rounded-2xl border border-slate-200/60 dark:border-slate-900 bg-white/40 dark:bg-slate-950/40 backdrop-blur-md custom-scrollbar space-y-4 my-4">
          {messages.map((msg, index) => {
            const isBot = msg.sender === 'bot';
            const isLatest = index === messages.length - 1;

            return (
              <div key={msg.id} className="space-y-2">
                <motion.div
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                  className={`flex items-start gap-3 max-w-[88%] ${
                    isBot ? 'mr-auto' : 'ml-auto flex-row-reverse'
                  }`}
                >
                  {/* Avatar Icon */}
                  <div
                    className={`p-2 rounded-xl flex-shrink-0 shadow-sm border ${
                      isBot
                        ? 'bg-brand-50 dark:bg-brand-500/10 text-brand-600 dark:text-brand-400 border-brand-200/30 dark:border-brand-500/20'
                        : 'bg-slate-800 dark:bg-slate-900 text-white border-slate-700/50'
                    }`}
                  >
                    {isBot ? <Bot className="h-4 w-4" /> : <User className="h-4 w-4" />}
                  </div>

                  {/* Message Bubble */}
                  <div className="space-y-1.5 w-full">
                    {isBot && msg.confidence && (
                      <div className="flex items-center justify-between gap-2">
                        <span className="text-[9px] uppercase tracking-wider font-bold text-slate-400">OncoRisk Advisor</span>
                        {getConfidenceBadge(msg.confidence)}
                      </div>
                    )}
                    
                    <div
                      className={`p-3.5 rounded-2xl text-sm leading-relaxed border shadow-sm ${
                        isBot
                          ? 'bg-white dark:bg-slate-900/80 text-slate-700 dark:text-slate-200 border-slate-200/60 dark:border-slate-800/80 whitespace-pre-wrap'
                          : 'bg-brand-600 dark:bg-brand-500 text-white border-brand-700/50 dark:border-brand-600/30 shadow-brand-500/5'
                      }`}
                    >
                      <div>{msg.text}</div>

                      {/* Citations Badging */}
                      {isBot && msg.sources && msg.sources.length > 0 && (
                        <div className="mt-3 flex flex-wrap gap-1.5 items-center border-t border-slate-100/50 dark:border-slate-800/40 pt-2.5">
                          <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider mr-1">Sources:</span>
                          {msg.sources.map((src, idx) => (
                            <span
                              key={idx}
                              className="inline-flex items-center px-1.5 py-0.5 rounded bg-slate-100 dark:bg-slate-850 text-slate-505 dark:text-slate-400 border border-slate-200/60 dark:border-slate-850 text-[9px] font-semibold"
                            >
                              {src}
                            </span>
                          ))}
                        </div>
                      )}

                      {/* Feedback Voting Controls */}
                      {isBot && msg.id !== 'welcome' && (
                        <div className="flex items-center justify-between border-t border-slate-100/50 dark:border-slate-800/40 pt-2.5 mt-2.5">
                          <div className="flex items-center space-x-1">
                            <button
                              onClick={() => handleFeedback(msg.id, 'HELPFUL')}
                              className={`p-1 rounded-lg transition-all active:scale-90 ${
                                msg.feedbackType === 'HELPFUL'
                                  ? 'bg-emerald-500/10 text-emerald-500'
                                  : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-900'
                              }`}
                              title="Helpful"
                            >
                              <ThumbsUp className="h-3 w-3" />
                            </button>
                            <button
                              onClick={() => handleFeedback(msg.id, 'NOT_HELPFUL')}
                              className={`p-1 rounded-lg transition-all active:scale-90 ${
                                msg.feedbackType === 'NOT_HELPFUL'
                                  ? 'bg-red-500/10 text-red-500'
                                  : 'text-slate-400 hover:text-slate-600 dark:hover:text-slate-200 hover:bg-slate-50 dark:hover:bg-slate-900'
                              }`}
                              title="Not helpful"
                            >
                              <ThumbsDown className="h-3 w-3" />
                            </button>
                            {msg.feedbackType && (
                              <span className="text-[9px] text-slate-400/80 font-bold flex items-center gap-1 pl-1">
                                <Check className="h-3 w-3 text-emerald-500" />
                                Feedback received
                              </span>
                            )}
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>

                {/* Suggestions chips under the latest message bubble */}
                {isBot && isLatest && !loading && msg.suggestions && msg.suggestions.length > 0 && (
                  <div className="flex flex-wrap gap-2 pl-12 mt-1">
                    {msg.suggestions.map((suggestion, sIdx) => (
                      <button
                        key={sIdx}
                        onClick={() => handleSend(suggestion)}
                        className="text-[11px] bg-white hover:bg-brand-50 dark:bg-slate-900 dark:hover:bg-brand-500/10 hover:text-brand-600 dark:hover:text-brand-400 border border-slate-200 dark:border-slate-800 hover:border-brand-500/30 rounded-full px-3 py-1 font-semibold transition-all active:scale-[0.97] shadow-sm"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            );
          })}

          {/* Loading / Typing Indicator */}
          {loading && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-start gap-3 mr-auto max-w-[85%]"
            >
              <div className="p-2 rounded-xl flex-shrink-0 bg-brand-50 dark:bg-brand-500/10 text-brand-600 dark:text-brand-400 border border-brand-200/30 dark:border-brand-500/20 shadow-sm">
                <Bot className="h-4 w-4" />
              </div>
              <div className="p-3.5 rounded-2xl border border-slate-200/60 dark:border-slate-800/80 bg-white dark:bg-slate-900/80 flex items-center space-x-2 text-xs font-semibold text-slate-500 shadow-sm">
                <Loader className="h-3.5 w-3.5 animate-spin text-brand-500" />
                <span>Analyzing clinical database parameters...</span>
              </div>
            </motion.div>
          )}

          {/* Scroll Target */}
          <div ref={messagesEndRef} />
        </div>

        {/* Initial Suggestion Chips (when chat is empty/just started) */}
        {messages.length === 1 && !loading && (
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 flex-shrink-0 mb-3">
            {suggestionChips.map((chip, idx) => {
              const Icon = chip.icon;
              return (
                <button
                  key={idx}
                  onClick={() => handleSend(chip.label)}
                  className="flex items-center space-x-1.5 p-3 rounded-xl border border-slate-200/60 dark:border-slate-900 hover:border-brand-500/30 bg-white dark:bg-slate-900/40 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 transition-all hover:bg-slate-50 dark:hover:bg-slate-900 duration-200 group active:scale-[0.98] shadow-sm"
                >
                  <Icon className="h-4 w-4 text-brand-500 flex-shrink-0 group-hover:scale-110 transition-transform" />
                  <span className="truncate">{chip.label}</span>
                </button>
              );
            })}
          </div>
        )}

        {/* Input controls form */}
        <div className="flex gap-3 items-center flex-shrink-0">
          <div className="relative flex-1">
            <textarea
              rows="1"
              className="clinical-input pr-12 custom-scrollbar resize-none py-3.5 align-middle"
              placeholder="Type your question about cancer risk factors or results here..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />
          </div>
          <button
            onClick={() => handleSend()}
            disabled={loading || !input.trim()}
            className="p-3.5 rounded-xl bg-brand-600 hover:bg-brand-700 dark:bg-brand-500 dark:hover:bg-brand-600 text-white font-bold transition-all disabled:opacity-40 disabled:scale-100 active:scale-[0.97]"
          >
            <Send className="h-5 w-5" />
          </button>
        </div>
        
        {/* Disclaimer Footer */}
        <div className="text-center text-[10px] text-slate-400 dark:text-slate-505 pb-1 mt-2">
          OncoRisk Assistant provides educational information only and does not replace professional medical advice.
        </div>
      </div>
    </div>
  );
}
