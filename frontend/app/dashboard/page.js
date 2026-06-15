"use client";

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Activity, Users, ShieldAlert, TrendingUp, AlertCircle, Loader, BarChart3, ChevronRight } from 'lucide-react';
import { api, getToken } from '../../utils/api';
import { ResponsiveContainer, PieChart, Pie, Cell, Tooltip, AreaChart, Area, XAxis, YAxis, CartesianGrid } from 'recharts';
import Link from 'next/link';

export default function Dashboard() {
  const router = useRouter();
  const [analytics, setAnalytics] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuthAndFetch = async () => {
      const token = getToken();
      if (!token) {
        router.push('/login');
        return;
      }

      try {
        const data = await api.get('/predictions/analytics');
        setAnalytics(data);
      } catch (err) {
        setError(err.message || 'Failed to fetch analytics statistics.');
      } finally {
        setLoading(false);
      }
    };

    checkAuthAndFetch();
  }, [router]);

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
      <div className="flex items-center space-x-2 text-sm text-red-650 bg-red-50 dark:bg-red-950/20 dark:text-red-400 p-4 rounded-xl border border-red-200/50 dark:border-red-900/30 max-w-xl mx-auto mt-10">
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
          <div className="p-3 bg-brand-50 dark:bg-brand-950/20 text-brand-600 dark:text-brand-450 rounded-2xl">
            <Users className="h-6 w-6" />
          </div>
        </div>

        <div className="glass-card p-6 flex items-center justify-between">
          <div className="space-y-1">
            <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">High Risk Alerts</span>
            <h2 className="text-3xl font-extrabold text-red-550 dark:text-red-400">{analytics.risk_distribution?.High || 0}</h2>
          </div>
          <div className="p-3 bg-red-50 dark:bg-red-950/10 text-red-550 dark:text-red-400 rounded-2xl">
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
          <div className="p-3 bg-blue-50 dark:bg-blue-950/20 text-blue-600 dark:text-blue-450 rounded-2xl">
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
            <p className="text-xs text-slate-450 mt-0.5">Frequency volume of assessments queried over the last 7 days</p>
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
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" className="dark:stroke-slate-850" />
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
            <p className="text-xs text-slate-450 mt-0.5">Aggregate user records sliced by output classification</p>
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
                    paddingAngle={3}
                    dataKey="value"
                  >
                    {pieData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', border: 'none', borderRadius: '8px', fontSize: '11px', color: '#fff' }}
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

      {/* Recent Activity Table */}
      <div className="glass-card p-6 space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-700 dark:text-slate-300">Recent Assessments</h3>
            <p className="text-xs text-slate-450 mt-0.5">Top 10 recently processed patient risk profiles</p>
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
                  <td colSpan={6} className="px-4 py-6 text-center text-slate-450">No patient assessments run yet.</td>
                </tr>
              ) : (
                analytics.recent_runs?.map((run) => (
                  <tr key={run.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-900/20 transition-all">
                    <td className="px-4 py-3 font-semibold text-xs text-slate-450">#LOG-{run.id}</td>
                    <td className="px-4 py-3 font-medium">{run.cancer_type}</td>
                    <td className="px-4 py-3">{run.age || 'N/A'}</td>
                    <td className="px-4 py-3">
                      <span className={getRiskBadgeClass(run.risk_level)}>{run.risk_level}</span>
                    </td>
                    <td className="px-4 py-3 font-bold text-slate-800 dark:text-slate-200">{(run.confidence * 100).toFixed(0)}%</td>
                    <td className="px-4 py-3 text-xs text-slate-450">
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
