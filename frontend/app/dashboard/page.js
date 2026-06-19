"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Activity, Users, ShieldAlert, TrendingUp, AlertCircle, Loader, BarChart3, ChevronRight } from 'lucide-react';
import { api, getToken } from '@/utils/api';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, AreaChart, Area, XAxis, YAxis, CartesianGrid } from 'recharts';
import Link from 'next/link';

const CustomPieTooltip = ({ active, payload, total }) => {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    const percentage = total > 0 ? ((data.value / total) * 100).toFixed(0) : 0;
    
    return (
      <div className="bg-slate-900/95 text-white dark:bg-white/95 dark:text-slate-900 px-3 py-2.5 rounded-xl shadow-xl border border-slate-800 dark:border-slate-200 text-xs font-semibold space-y-1 select-none pointer-events-none z-50">
        <div className="flex items-center space-x-1.5 font-bold">
          <div className="h-2 w-2 rounded-full" style={{ backgroundColor: data.color }} />
          <span>{data.name}</span>
        </div>
        <div className="text-slate-300 dark:text-slate-600 font-medium">
          <span>Count: </span>
          <span className="font-extrabold text-white dark:text-slate-900">{data.value}</span>
          <span className="mx-1.5">•</span>
          <span className="font-extrabold text-brand-400 dark:text-brand-600">{percentage}%</span>
        </div>
      </div>
    );
  }
  return null;
};

export default function Dashboard() {
  const router = useRouter();
  const [analytics, setAnalytics] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  // Retrain states
  const [retrainStatus, setRetrainStatus] = useState(null);
  const [polling, setPolling] = useState(false);
  const [actionError, setActionError] = useState('');
  const [trialsPerModel, setTrialsPerModel] = useState(15);

  useEffect(() => {
    const checkAuthAndFetch = async () => {
      const token = getToken();
      if (!token) {
        router.push('/login');
        return;
      }

      // Check if user has admin privileges
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        if (!payload.is_admin) {
          router.push('/predict');
          return;
        }
      } catch (_) {
        router.push('/login');
        return;
      }

      try {
        const data = await api.get('/predictions/analytics');
        setAnalytics(data);

        const status = await api.get('/admin/retrain/status');
        setRetrainStatus(status);
        if (status.is_training) {
          setPolling(true);
        }
      } catch (err) {
        setError(err.message || 'Failed to fetch analytics statistics.');
      } finally {
        setLoading(false);
      }
    };

    checkAuthAndFetch();
  }, [router]);

  useEffect(() => {
    let intervalId = null;
    if (polling) {
      intervalId = setInterval(async () => {
        try {
          const status = await api.get('/admin/retrain/status');
          setRetrainStatus(status);
          if (!status.is_training) {
            setPolling(false);
            // Refresh stats on complete
            const freshAnalytics = await api.get('/predictions/analytics');
            setAnalytics(freshAnalytics);
          }
        } catch (err) {
          console.error("Polling retrain status failed:", err);
        }
      }, 1500);
    }
    return () => {
      if (intervalId) clearInterval(intervalId);
    };
  }, [polling]);

  const handleRetrain = async () => {
    setActionError('');
    try {
      await api.post('/admin/retrain', { trials_per_model: parseInt(trialsPerModel) });
      setPolling(true);
      const status = await api.get('/admin/retrain/status');
      setRetrainStatus(status);
    } catch (err) {
      setActionError(err.message || 'Failed to trigger model retraining.');
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-3">
        <Loader className="h-10 w-10 animate-spin text-brand-600 dark:text-brand-500" />
        <span className="text-sm text-slate-500 font-medium">Compiling aggregate analytics reports...</span>
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

  // Map Donut chart data
  const pieData = [
    { name: 'Low Risk', value: analytics.risk_distribution?.Low || 0, color: '#10b981' },
    { name: 'Medium Risk', value: analytics.risk_distribution?.Medium || 0, color: '#f59e0b' },
    { name: 'High Risk', value: analytics.risk_distribution?.High || 0, color: '#ef4444' }
  ].filter(d => d.value > 0);

  // Map weekly trends data
  const trendData = (analytics.trends || []).map(t => {
    // Format YYYY-MM-DD to "Jun 15"
    const dateParts = t.date.split('-');
    const formattedDate = dateParts.length === 3 
      ? new Date(dateParts[0], dateParts[1] - 1, dateParts[2]).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })
      : t.date;
    return {
      date: formattedDate,
      Assessments: t.count
    };
  });

  const getRiskBadgeClass = (risk) => {
    if (risk === 'Low') return 'badge-low';
    if (risk === 'Medium') return 'badge-medium';
    return 'badge-high';
  };

  return (
    <div className="space-y-8">
      {/* Title */}
      <div className="pb-4 border-b border-slate-200/60 dark:border-slate-900">
        <h1 className="text-3xl font-extrabold text-slate-800 dark:text-white flex items-center space-x-2">
          <BarChart3 className="h-7 w-7 text-brand-600 dark:text-brand-500" />
          <span>Clinician Cockpit</span>
        </h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Real-time stats, weekly load charts, and risk splits</p>
      </div>

      {/* Numerical Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="glass-card p-6 flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Total Assessments</span>
            <h2 className="text-3xl font-extrabold text-slate-800 dark:text-white">{analytics.total_assessments}</h2>
          </div>
          <div className="p-3 bg-brand-50 dark:bg-brand-500/15 text-brand-600 dark:text-brand-500 rounded-2xl">
            <Users className="h-6 w-6" />
          </div>
        </div>

        <div className="glass-card p-6 flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">High Risk Alerts</span>
            <h2 className="text-3xl font-extrabold text-red-600 dark:text-red-400">{analytics.risk_distribution?.High || 0}</h2>
          </div>
          <div className="p-3 bg-red-50 dark:bg-red-950/10 text-red-600 dark:text-red-400 rounded-2xl">
            <ShieldAlert className="h-6 w-6" />
          </div>
        </div>

        <div className="glass-card p-6 flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Weekly Queries</span>
            <h2 className="text-3xl font-extrabold text-slate-800 dark:text-white">
              {trendData.reduce((acc, curr) => acc + curr.Assessments, 0)}
            </h2>
          </div>
          <div className="p-3 bg-blue-50 dark:bg-blue-950/20 text-blue-600 dark:text-blue-400 rounded-2xl">
            <TrendingUp className="h-6 w-6" />
          </div>
        </div>
      </div>

      {/* Graphical Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Weekly Area Trend Chart */}
        <div className="glass-card p-6 lg:col-span-8 space-y-4">
          <div>
            <h3 className="text-base font-bold text-slate-700 dark:text-slate-300">Assessment Load Trends</h3>
            <p className="text-xs text-slate-400 mt-0.5">Frequency volume of assessments queried over the last 7 days</p>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorAssessments" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#0d9488" stopOpacity={0.25}/>
                    <stop offset="95%" stopColor="#0d9488" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" className="dark:stroke-slate-800" />
                <XAxis dataKey="date" tick={{ fill: '#94a3b8', fontSize: 10 }} tickLine={false} axisLine={false} />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 10 }} tickLine={false} axisLine={false} allowDecimals={false} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#0f172a', border: 'none', borderRadius: '8px', fontSize: '11px', color: '#fff' }}
                />
                <Area type="monotone" dataKey="Assessments" stroke="#0d9488" strokeWidth={2.5} fillOpacity={1} fill="url(#colorAssessments)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Risk Donut Chart */}
        <div className="glass-card p-6 lg:col-span-4 space-y-4 flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-700 dark:text-slate-300">Risk Profile Split</h3>
            <p className="text-xs text-slate-400 mt-0.5">Aggregate user records sliced by output classification</p>
          </div>
          
          <div className="h-44 w-full relative flex items-center justify-center">
            {pieData.length === 0 ? (
              <div className="text-xs font-semibold text-slate-400">No diagnostic data logged.</div>
            ) : (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={pieData}
                    cx="50%"
                    cy="50%"
                    innerRadius={52}
                    outerRadius={68}
                    paddingAngle={4}
                    stroke="none"
                    cornerRadius={4}
                    shapeRendering="geometricPrecision"
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} stroke="none" />
                    ))}
                  </Pie>
                  <Tooltip 
                    content={<CustomPieTooltip total={analytics.total_assessments} />}
                    allowEscapeViewBox={{ x: true, y: true }}
                    wrapperStyle={{ zIndex: 100 }}
                  />
                </PieChart>
              </ResponsiveContainer>
            )}
            {pieData.length > 0 && (
              <div className="absolute flex flex-col items-center">
                <span className="text-2xl font-black text-slate-800 dark:text-white">{analytics.total_assessments}</span>
                <span className="text-[9px] font-bold text-slate-400 uppercase tracking-widest">Records</span>
              </div>
            )}
          </div>

          <div className="space-y-2 pt-2 border-t border-slate-200/50 dark:border-slate-900">
            {['Low', 'Medium', 'High'].map(risk => {
              const count = analytics.risk_distribution?.[risk] || 0;
              const percent = analytics.total_assessments > 0 ? ((count / analytics.total_assessments) * 100).toFixed(0) : 0;
              const colorMap = { Low: 'bg-emerald-500', Medium: 'bg-amber-500', High: 'bg-red-500' };
              return (
                <div key={risk} className="flex items-center justify-between text-xs">
                  <div className="flex items-center space-x-2">
                    <div className={`h-2.5 w-2.5 rounded-full ${colorMap[risk]}`} />
                    <span className="font-medium text-slate-500 dark:text-slate-400">{risk} Risk</span>
                  </div>
                  <span className="font-bold text-slate-700 dark:text-slate-200">{count} ({percent}%)</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Admin Retrain Widget */}
      <div className="glass-card p-6 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-200/50 dark:border-slate-800/80 pb-4">
          <div>
            <h3 className="text-base font-bold text-slate-700 dark:text-slate-300 flex items-center space-x-2">
              <Activity className="h-5 w-5 text-brand-600 dark:text-brand-500 animate-pulse" />
              <span>OncoRisk ML Engine Administration</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">Retrain models and run hyperparameter tuning with Optuna optimization</p>
          </div>
          <div className="flex items-center space-x-3 self-start sm:self-auto">
            <div className="flex items-center space-x-1.5 bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 px-3 py-1.5 rounded-xl">
              <label className="text-[10px] uppercase font-bold text-slate-400 whitespace-nowrap">Trials / Model:</label>
              <input
                type="number"
                min="5"
                max="100"
                className="w-10 text-xs font-bold text-center bg-transparent border-none focus:outline-none text-slate-800 dark:text-slate-200"
                value={trialsPerModel}
                onChange={(e) => setTrialsPerModel(Math.max(5, Math.min(100, parseInt(e.target.value) || 5)))}
                disabled={polling || (retrainStatus && retrainStatus.is_training)}
              />
            </div>
            <button
              onClick={handleRetrain}
              disabled={polling || (retrainStatus && retrainStatus.is_training)}
              className="px-5 py-2.5 bg-brand-600 hover:bg-brand-700 dark:bg-brand-500 dark:hover:bg-brand-600 disabled:opacity-50 text-white font-bold rounded-xl shadow-md transition-all active:scale-[0.98] text-xs flex items-center justify-center space-x-1.5"
            >
              <span>Retrain ML Engine</span>
            </button>
          </div>
        </div>

        {actionError && (
          <div className="text-xs text-red-500 bg-red-50 dark:bg-red-950/20 p-3.5 rounded-xl border border-red-200/50">
            {actionError}
          </div>
        )}

        {retrainStatus && (retrainStatus.is_training || retrainStatus.winner_model !== "None") && (
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-stretch">
            {/* Status summaries */}
            <div className="lg:col-span-5 flex flex-col justify-between space-y-4">
              <div className="space-y-4">
                <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-900 pb-2 text-xs">
                  <span className="text-slate-400 font-medium">Status:</span>
                  <span className={`font-bold ${retrainStatus.is_training ? 'text-brand-600 dark:text-brand-400 animate-pulse' : 'text-emerald-500'}`}>
                    {retrainStatus.is_training ? `Training - ${retrainStatus.current_step}` : 'Successfully Completed'}
                  </span>
                </div>
                
                <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-900 pb-2 text-xs">
                  <span className="text-slate-400 font-medium">Study Trials:</span>
                  <span className="font-bold text-slate-700 dark:text-slate-200">
                    {retrainStatus.current_trial} / {retrainStatus.total_trials} (Optuna Search)
                  </span>
                </div>

                <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-900 pb-2 text-xs">
                  <span className="text-slate-400 font-medium">Best Random Forest F1:</span>
                  <span className="font-bold text-slate-700 dark:text-slate-200">
                    {retrainStatus.best_rf_f1 > 0 ? retrainStatus.best_rf_f1.toFixed(4) : "Pending"}
                  </span>
                </div>

                <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-900 pb-2 text-xs">
                  <span className="text-slate-400 font-medium">Best XGBoost F1:</span>
                  <span className="font-bold text-slate-700 dark:text-slate-200">
                    {retrainStatus.best_xgb_f1 > 0 ? retrainStatus.best_xgb_f1.toFixed(4) : "Pending"}
                  </span>
                </div>
              </div>

              {retrainStatus.winner_model !== "None" && (
                <div className="bg-brand-50/50 dark:bg-brand-950/10 border border-brand-200/40 dark:border-brand-900/30 p-4 rounded-2xl space-y-1">
                  <span className="text-[10px] uppercase tracking-wider font-bold text-brand-600 dark:text-brand-400">Deployed Winner Model</span>
                  <div className="text-lg font-black text-slate-800 dark:text-white flex items-center justify-between">
                    <span>{retrainStatus.winner_model}</span>
                    <span className="text-emerald-500 font-bold text-sm">F1: {retrainStatus.best_f1.toFixed(4)}</span>
                  </div>
                </div>
              )}
            </div>

            {/* Terminal console logger */}
            <div className="lg:col-span-7 flex flex-col">
              <div className="relative flex flex-col flex-1 p-4 bg-slate-950 border border-slate-900 rounded-2xl w-full h-56 font-mono text-[10px] leading-relaxed shadow-inner select-none text-slate-400 overflow-y-auto overflow-x-hidden">
                <div className="flex items-center justify-between pb-2 border-b border-slate-900 mb-2 text-slate-500 text-[9px] uppercase tracking-wider">
                  <span>Optuna Trials Console Log</span>
                  {retrainStatus.is_training && <span className="h-2 w-2 rounded-full bg-brand-600 dark:bg-brand-400 animate-ping" />}
                </div>
                <div className="space-y-1">
                  {retrainStatus.logs?.length === 0 ? (
                    <p className="text-slate-400">Console idle. Awaiting command execution...</p>
                  ) : (
                    retrainStatus.logs?.slice(-100).map((log, i) => (
                      <p key={i} className={log.includes("ERROR") ? "text-red-400" : log.includes("Winner") || log.includes("completed") ? "text-emerald-400" : "text-slate-300"}>
                        {log}
                      </p>
                    ))
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Recent Activity Table */}
      <div className="glass-card p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-700 dark:text-slate-300">Recent Assessments</h3>
            <p className="text-xs text-slate-400 mt-0.5">Top 10 recently processed patient risk profiles</p>
          </div>
          <Link href="/history" className="text-xs font-bold text-brand-600 dark:text-brand-500 flex items-center space-x-0.5 hover:underline">
            <span>View Audit Logs</span>
            <ChevronRight className="h-3.5 w-3.5" />
          </Link>
        </div>

        <div className="overflow-x-auto rounded-xl border border-slate-200/50 dark:border-slate-900">
          <table className="min-w-full divide-y divide-slate-200/60 dark:divide-slate-900 text-left text-sm">
            <thead className="bg-slate-50 dark:bg-slate-900/60 text-slate-500 dark:text-slate-400 text-xs font-semibold uppercase tracking-wider">
              <tr>
                <th className="px-4 py-3">Audit ID</th>
                <th className="px-4 py-3">Suspected Cancer</th>
                <th className="px-4 py-3">Patient Age</th>
                <th className="px-4 py-3">Risk Assessment</th>
                <th className="px-4 py-3">Model Confidence</th>
                <th className="px-4 py-3">Query Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200/40 dark:divide-slate-900/80 text-slate-600 dark:text-slate-300">
              {analytics.recent_runs?.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-4 py-6 text-center text-slate-400">No patient assessments run yet.</td>
                </tr>
              ) : (
                analytics.recent_runs?.map((run) => (
                  <tr key={run.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-900/20 transition-all">
                    <td className="px-4 py-3 font-semibold text-xs text-slate-500">#LOG-{run.id}</td>
                    <td className="px-4 py-3 font-medium">{run.cancer_type}</td>
                    <td className="px-4 py-3">{run.age || 'N/A'}</td>
                    <td className="px-4 py-3">
                      <span className={getRiskBadgeClass(run.risk_level)}>{run.risk_level}</span>
                    </td>
                    <td className="px-4 py-3 font-bold text-slate-800 dark:text-slate-200">{(run.confidence * 100).toFixed(0)}%</td>
                    <td className="px-4 py-3 text-xs text-slate-500">
                      {new Date(run.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
