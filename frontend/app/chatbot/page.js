"use client";

import { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, Send, Bot, User, Loader, HelpCircle, Activity, Sparkles, Dumbbell } from 'lucide-react';
import { api, getToken } from '@/utils/api';

export default function ChatbotPage() {
  const router = useRouter();
  const messagesEndRef = useRef(null);
  
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'bot',
      text: "Hello! I am your OncoRisk AI Health Assistant. I am here to help you understand your cancer risk assessments, explain the SHAP contributing factors, and provide educational lifestyle guidelines.\n\nWhat would you like to discuss today?",
      confidence: 'HIGH'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Suggestions for fast clinician queries
  const suggestionChips = [
    { label: "Why did I get my risk level?", icon: Sparkles },
    { label: "What lifestyle improvements should I make?", icon: Dumbbell },
    { label: "What screenings should I consider?", icon: Activity },
    { label: "General cancer risk factors", icon: HelpCircle }
  ];

  useEffect(() => {
    // Session Guard: redirect to login if no auth token is active
    const token = getToken();
    if (!token) {
      router.push('/login');
    }
  }, [router]);

  // Scroll to bottom helper
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

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
      const response = await api.post('/chatbot/message', { message: queryText });
      
      const botMsg = {
        id: `bot-${Date.now()}`,
        sender: 'bot',
        text: response.answer,
        confidence: response.confidence
      };
      setMessages(prev => [...prev, botMsg]);
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
    <div className="max-w-4xl mx-auto space-y-6 flex flex-col h-[calc(100vh-10rem)]">
      {/* Page Header */}
      <div className="pb-4 border-b border-slate-200/60 dark:border-slate-900 flex-shrink-0">
        <h1 className="text-3xl font-extrabold text-slate-800 dark:text-white flex items-center space-x-2">
          <MessageSquare className="h-7 w-7 text-brand-600 dark:text-brand-500" />
          <span>Chat Assistant</span>
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
          Discuss clinical variables, lifestyle choices, and get educational screening insights
        </p>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-950/20 border border-red-200/50 dark:border-red-900/30 text-red-600 dark:text-red-400 text-xs p-3.5 rounded-xl flex items-center space-x-2 flex-shrink-0">
          <span>{error}</span>
        </div>
      )}

      {/* Messages Window */}
      <div className="flex-1 overflow-y-auto p-4 rounded-2xl border border-slate-200/60 dark:border-slate-900 bg-white/40 dark:bg-slate-950/40 backdrop-blur-md custom-scrollbar space-y-4">
        {messages.map((msg) => {
          const isBot = msg.sender === 'bot';
          return (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.2 }}
              className={`flex items-start gap-3.5 max-w-[85%] ${
                isBot ? 'mr-auto' : 'ml-auto flex-row-reverse'
              }`}
            >
              {/* Avatar Icon */}
              <div
                className={`p-2.5 rounded-xl flex-shrink-0 shadow-sm border ${
                  isBot
                    ? 'bg-brand-50 dark:bg-brand-500/10 text-brand-600 dark:text-brand-400 border-brand-200/30 dark:border-brand-500/20'
                    : 'bg-slate-800 dark:bg-slate-900 text-white border-slate-700/50'
                }`}
              >
                {isBot ? <Bot className="h-4.5 w-4.5" /> : <User className="h-4.5 w-4.5" />}
              </div>

              {/* Message Bubble */}
              <div className="space-y-1.5 w-full">
                {isBot && msg.confidence && (
                  <div className="flex items-center justify-between gap-2">
                    <span className="text-[10px] uppercase tracking-wider font-bold text-slate-400">OncoRisk Advisor</span>
                    {getConfidenceBadge(msg.confidence)}
                  </div>
                )}
                
                <div
                  className={`p-4 rounded-2xl text-sm leading-relaxed border shadow-sm ${
                    isBot
                      ? 'bg-white dark:bg-slate-900/80 text-slate-700 dark:text-slate-200 border-slate-200/60 dark:border-slate-800/80 whitespace-pre-wrap'
                      : 'bg-brand-600 dark:bg-brand-500 text-white border-brand-700/50 dark:border-brand-600/30 shadow-brand-500/5'
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            </motion.div>
          );
        })}

        {/* Loading / Typing Indicator */}
        {loading && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-start gap-3.5 mr-auto max-w-[85%]"
          >
            <div className="p-2.5 rounded-xl flex-shrink-0 bg-brand-50 dark:bg-brand-500/10 text-brand-600 dark:text-brand-400 border border-brand-200/30 dark:border-brand-500/20 shadow-sm">
              <Bot className="h-4.5 w-4.5" />
            </div>
            <div className="p-4 rounded-2xl border border-slate-200/60 dark:border-slate-800/80 bg-white dark:bg-slate-900/80 flex items-center space-x-2 text-xs font-semibold text-slate-500 shadow-sm">
              <Loader className="h-3.5 w-3.5 animate-spin text-brand-500" />
              <span>Analyzing clinical database parameters...</span>
            </div>
          </motion.div>
        )}

        {/* Scroll Target */}
        <div ref={messagesEndRef} />
      </div>

      {/* Suggested Prompt Chips */}
      {messages.length === 1 && !loading && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 flex-shrink-0">
          {suggestionChips.map((chip, idx) => {
            const Icon = chip.icon;
            return (
              <button
                key={idx}
                onClick={() => handleSend(chip.label)}
                className="flex items-center space-x-1.5 p-3 rounded-xl border border-slate-200/60 dark:border-slate-900 hover:border-brand-500/30 bg-white dark:bg-slate-900/40 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 transition-all hover:bg-slate-50 dark:hover:bg-slate-900 duration-200 group active:scale-[0.98]"
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
    </div>
  );
}
