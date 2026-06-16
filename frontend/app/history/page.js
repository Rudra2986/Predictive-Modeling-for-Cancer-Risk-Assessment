"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { History, Search, Filter, Eye, X, Loader, AlertCircle, Info, Calendar } from 'lucide-react';
import { api, getToken } from '@/utils/api';

export default function HistoryPage() {
  const router = useRouter();
  const [history, setHistory] = useState([]);
  const [filteredHistory, setFilteredHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [riskFilter, setRiskFilter] = useState('All');
  const [selectedItem, setSelectedItem] = useState(null);

  useEffect(() => {
    const fetchHistory = async () => {
      const token = getToken();
      if (!token) {
        router.push('/login');
        return;
      }

      try {
        const data = await api.get('/predictions/history');
        setHistory(data);
        setFilteredHistory(data);
      } catch (err) {
        setError(err.message || 'Failed to retrieve prediction logs history.');
      } finally {
        setLoading(false);
      }
    };

    fetchHistory();
  }, [router]);

  // Handle client-side search & filtering
  useEffect(() => {
    let result = history;

    // Term search filter (Log ID or Cancer Type)
    if (searchTerm.trim() !== '') {
      const term = searchTerm.toLowerCase();
      result = result.filter(item => 
        item.patient_data?.Cancer_Type?.toLowerCase().includes(term) ||
        `#log-${item.id}`.toLowerCase().includes(term)
      );
    }

    // Risk level dropdown filter
    if (riskFilter !== 'All') {
      result = result.filter(item => item.predicted_class === riskFilter);
    }

    setFilteredHistory(result);
  }, [searchTerm, riskFilter, history]);

  const getRiskBadgeClass = (risk) => {
    if (risk === 'Low') return 'badge-low';
    if (risk === 'Medium') return 'badge-medium';
    return 'badge-high';
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-3">
        <Loader className="h-10 w-10 animate-spin text-brand-600 dark:text-brand-500" />
        <span className="text-sm text-slate-500 font-medium">Loading historical clinical logs...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center space-x-2 text-sm text-red-600 bg-red-50 dark:bg-red-950/20 dark:text-red-400 p-4 rounded-xl border border-red-200/50 dark:border-red-900/30 max-w-xl mx-auto mt-10">
        <AlertCircle className="h-5 w-5 flex-shrink-0" />
        <span>{error}</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="pb-4 border-b border-slate-200/60 dark:border-slate-900 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-800 dark:text-white flex items-center space-x-2">
            <History className="h-7 w-7 text-brand-600 dark:text-brand-500" />
            <span>Audit History Logs</span>
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Review, search, and inspect past patient risk predictions</p>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="grid grid-cols-1 sm:grid-cols-12 gap-4">
        <div className="sm:col-span-8 relative">
          <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400">
            <Search className="h-4.5 w-4.5" />
          </span>
          <input
            type="text"
            className="clinical-input pl-10"
            placeholder="Search by Cancer Type or Log ID (e.g. Lung, #LOG-1)..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>

        <div className="sm:col-span-4 relative">
          <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400">
            <Filter className="h-4.5 w-4.5" />
          </span>
          <select
            className="clinical-input pl-10"
            value={riskFilter}
            onChange={(e) => setRiskFilter(e.target.value)}
          >
            <option value="All">All Risk Classes</option>
            <option value="Low">Low Risk</option>
            <option value="Medium">Medium Risk</option>
            <option value="High">High Risk</option>
          </select>
        </div>
      </div>

      {/* Logs Table */}
      <div className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200/60 dark:divide-slate-900 text-left text-sm">
            <thead className="bg-slate-50 dark:bg-slate-900/60 text-slate-500 dark:text-slate-400 text-xs font-semibold uppercase tracking-wider">
              <tr>
                <th className="px-5 py-3">Audit ID</th>
                <th className="px-5 py-3">Cancer Type</th>
                <th className="px-5 py-3">Patient Profile</th>
                <th className="px-5 py-3">Assessment Outcome</th>
                <th className="px-5 py-3">Confidence</th>
                <th className="px-5 py-3">Timestamp</th>
                <th className="px-5 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200/40 dark:divide-slate-900/80 text-slate-600 dark:text-slate-300">
              {filteredHistory.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-5 py-12 text-center text-slate-400 font-medium">
                    No prediction log audits matched current criteria.
                  </td>
                </tr>
              ) : (
                filteredHistory.map((item) => (
                  <tr key={item.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-900/20 transition-all">
                    <td className="px-5 py-4 font-semibold text-xs text-slate-500">#LOG-{item.id}</td>
                    <td className="px-5 py-4 font-semibold text-slate-800 dark:text-slate-200">
                      {item.patient_data?.Cancer_Type || 'Unknown'}
                    </td>
                    <td className="px-5 py-4 text-xs">
                      <span>Age: {item.patient_data?.Age}</span>
                      <span className="mx-1.5">•</span>
                      <span>Gender: {item.patient_data?.Gender === 1 ? 'Male' : 'Female'}</span>
                    </td>
                    <td className="px-5 py-4">
                      <span className={getRiskBadgeClass(item.predicted_class)}>{item.predicted_class}</span>
                    </td>
                    <td className="px-5 py-4 font-bold text-slate-800 dark:text-slate-200">
                      {(item.confidence_score * 100).toFixed(0)}%
                    </td>
                    <td className="px-5 py-4 text-xs text-slate-500">
                      {new Date(item.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="px-5 py-4 text-right">
                      <button
                        onClick={() => setSelectedItem(item)}
                        className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg border border-slate-200/60 dark:border-slate-800 hover:bg-brand-50 dark:hover:bg-brand-950/20 hover:text-brand-600 dark:hover:text-brand-400 text-xs font-semibold text-slate-500 dark:text-slate-400 transition-all"
                      >
                        <Eye className="h-3.5 w-3.5" />
                        <span>Inspect</span>
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Inspection Detail Modal */}
      <AnimatePresence>
        {selectedItem && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-950/40 backdrop-blur-sm">
            {/* Modal backdrop */}
            <motion.div
              className="absolute inset-0 bg-transparent"
              onClick={() => setSelectedItem(null)}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            />

            {/* Modal Card */}
            <motion.div
              className="glass-card w-full max-w-2xl max-h-[90vh] overflow-y-auto flex flex-col p-6 space-y-6 relative z-10 shadow-2xl border border-slate-200/80 dark:border-slate-800"
              initial={{ scale: 0.95, opacity: 0, y: 10 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 10 }}
              transition={{ duration: 0.2 }}
            >
              {/* Close Button */}
              <button
                onClick={() => setSelectedItem(null)}
                className="absolute top-4 right-4 p-1.5 rounded-lg text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-800 hover:text-slate-800 dark:hover:text-slate-100 transition-all"
              >
                <X className="h-5 w-5" />
              </button>

              {/* Modal Header */}
              <div className="pb-4 border-b border-slate-200/50 dark:border-slate-800 pr-8">
                <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest block">Audit Detail Record</span>
                <h2 className="text-xl font-bold text-slate-800 dark:text-white mt-1">
                  Prediction log: #LOG-{selectedItem.id} ({selectedItem.patient_data?.Cancer_Type || 'Unknown'})
                </h2>
              </div>

              {/* Outcome Highlights */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 bg-slate-50 dark:bg-slate-900/35 p-4 rounded-2xl border border-slate-200/20 dark:border-slate-800">
                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-xl bg-white dark:bg-slate-950 text-slate-500 border border-slate-200/50 dark:border-slate-800">
                    <Info className="h-5 w-5" />
                  </div>
                  <div>
                    <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Risk Level</span>
                    <span className={`text-sm font-extrabold ${selectedItem.predicted_class === 'High' ? 'text-red-500' : selectedItem.predicted_class === 'Medium' ? 'text-amber-500' : 'text-emerald-500'}`}>
                      {selectedItem.predicted_class} Risk
                    </span>
                  </div>
                </div>

                <div className="flex items-center space-x-3">
                  <div className="p-2 rounded-xl bg-white dark:bg-slate-950 text-slate-500 border border-slate-200/50 dark:border-slate-800">
                    <Calendar className="h-5 w-5" />
                  </div>
                  <div>
                    <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Assessed On</span>
                    <span className="text-sm font-bold text-slate-700 dark:text-slate-200">
                      {new Date(selectedItem.created_at).toLocaleDateString(undefined, { month: 'long', day: 'numeric', year: 'numeric' })}
                    </span>
                  </div>
                </div>
              </div>

              {/* Explainer Narrative */}
              <div className="space-y-2">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Medical Explanation</h3>
                <p className="text-sm text-slate-600 dark:text-slate-300 leading-relaxed italic bg-slate-50 dark:bg-slate-900/40 p-4 rounded-xl border border-slate-200/20 dark:border-slate-800">
                  "{selectedItem.explanation_narrative}"
                </p>
              </div>

              {/* Patient Variables Grid */}
              <div className="space-y-3">
                <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Logged Patient Metrics</h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 max-h-56 overflow-y-auto pr-2 custom-scrollbar text-xs font-medium border border-slate-200/30 dark:border-slate-800 rounded-xl p-3 bg-white/40 dark:bg-slate-900/20">
                  {Object.entries(selectedItem.patient_data || {}).map(([key, val]) => {
                    // Prettify name
                    const name = key.replace(/_/g, ' ');
                    let displayVal = val;
                    if (key === 'Gender') displayVal = val === 1 ? 'Male' : 'Female';
                    if (['Family_History', 'BRCA_Mutation', 'H_Pylori_Infection'].includes(key)) {
                      displayVal = val === 1 ? 'Present' : 'Absent';
                    }
                    return (
                      <div key={key} className="flex flex-col p-2 bg-slate-50/50 dark:bg-slate-900/40 border border-slate-200/30 dark:border-slate-800 rounded-lg">
                        <span className="text-[10px] text-slate-400 font-bold uppercase truncate">{name}</span>
                        <span className="text-slate-800 dark:text-slate-200 font-extrabold mt-0.5">{displayVal}</span>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* Footer CTA */}
              <div className="flex justify-end pt-2 border-t border-slate-200/60 dark:border-slate-800">
                <button
                  onClick={() => setSelectedItem(null)}
                  className="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-900 text-white dark:bg-slate-900 dark:hover:bg-slate-800 text-xs font-bold"
                >
                  Close Record
                </button>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}
