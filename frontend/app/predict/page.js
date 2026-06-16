"use client";

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Activity, Loader, AlertCircle, ArrowLeft, Heart, Sparkles, User, Dumbbell, ShieldAlert, Award } from 'lucide-react';
import { api } from '@/utils/api';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';

export default function PredictPage() {
  // 1. Inputs state mapping the PatientPredictionInput schema
  const [formData, setFormData] = useState({
    Age: 55,
    Gender: 1,
    Smoking: 5,
    Alcohol_Use: 5,
    Obesity: 5,
    Family_History: 0,
    Diet_Red_Meat: 5,
    Diet_Salted_Processed: 5,
    Fruit_Veg_Intake: 5,
    Physical_Activity: 5,
    Air_Pollution: 5,
    Occupational_Hazards: 5,
    BRCA_Mutation: 0,
    H_Pylori_Infection: 0,
    Calcium_Intake: 5,
    BMI: 24.5,
    Physical_Activity_Level: 5,
    Cancer_Type: "Breast"
  });

  const [activeTab, setActiveTab] = useState(0); // 0: Demographics, 1: Lifestyle & Diet, 2: Medical & Environmental
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const validateStep = (step) => {
    if (step === 0) {
      if (!formData.Cancer_Type) {
        setError("Please select a suspected Cancer Type.");
        return false;
      }
      const ageVal = parseInt(formData.Age);
      if (isNaN(ageVal) || ageVal < 1 || ageVal > 120) {
        setError("Please enter a valid Patient Age between 1 and 120.");
        return false;
      }
      const bmiVal = parseFloat(formData.BMI);
      if (isNaN(bmiVal) || bmiVal < 10.0 || bmiVal > 60.0) {
        setError("Please enter a valid Body Mass Index (BMI) between 10.0 and 60.0.");
        return false;
      }
    }
    return true;
  };

  const tabs = [
    { label: "Demographics & Vitals", icon: User },
    { label: "Lifestyle & Diet", icon: Dumbbell },
    { label: "Clinical & Environment", icon: ShieldAlert }
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // If not on the final step, advance step instead of submitting
    if (activeTab < tabs.length - 1) {
      if (validateStep(activeTab)) {
        setActiveTab(prev => prev + 1);
      }
      return;
    }

    // Run all step validations before final submit
    for (let i = 0; i <= activeTab; i++) {
      if (!validateStep(i)) {
        setActiveTab(i);
        return;
      }
    }

    setLoading(true);
    setResult(null);

    // Prepare inputs: parse numbers to correct types
    const payload = {
      ...formData,
      Age: parseInt(formData.Age),
      Gender: parseInt(formData.Gender),
      Smoking: parseInt(formData.Smoking),
      Alcohol_Use: parseInt(formData.Alcohol_Use),
      Obesity: parseInt(formData.Obesity),
      Family_History: parseInt(formData.Family_History),
      Diet_Red_Meat: parseInt(formData.Diet_Red_Meat),
      Diet_Salted_Processed: parseInt(formData.Diet_Salted_Processed),
      Fruit_Veg_Intake: parseInt(formData.Fruit_Veg_Intake),
      Physical_Activity: parseInt(formData.Physical_Activity),
      Air_Pollution: parseInt(formData.Air_Pollution),
      Occupational_Hazards: parseInt(formData.Occupational_Hazards),
      BRCA_Mutation: parseInt(formData.BRCA_Mutation),
      H_Pylori_Infection: parseInt(formData.H_Pylori_Infection),
      Calcium_Intake: parseInt(formData.Calcium_Intake),
      BMI: parseFloat(formData.BMI),
      Physical_Activity_Level: parseInt(formData.Physical_Activity_Level)
    };

    try {
      const data = await api.post('/predict', payload);
      setResult(data);
    } catch (err) {
      setError(err.message || 'Failed to generate assessment. Please check input values.');
    } finally {
      setLoading(false);
    }
  };

  // SVG Gauge calculations
  const getCircleParams = (score) => {
    const radius = 50;
    const strokeWidth = 10;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (score * circumference);
    return { strokeWidth, circumference, offset, radius };
  };

  const getRiskColorClass = (risk) => {
    if (risk === 'Low') return 'text-emerald-500 border-emerald-500/20 bg-emerald-50 dark:bg-emerald-950/20';
    if (risk === 'Medium') return 'text-amber-500 border-amber-500/20 bg-amber-50 dark:bg-amber-950/20';
    return 'text-red-500 border-red-500/20 bg-red-50 dark:bg-red-950/20';
  };

  const getBarColor = (impactLevel) => {
    if (impactLevel === 'High') return '#ef4444'; // red
    if (impactLevel === 'Medium') return '#f59e0b'; // amber
    return '#10b981'; // emerald
  };

  return (
    <div className="max-w-5xl mx-auto space-y-8">
      {/* Header text */}
      <div className="flex items-center justify-between pb-4 border-b border-slate-200/60 dark:border-slate-900">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-800 dark:text-white flex items-center space-x-2">
            <Activity className="h-7 w-7 text-brand-600 dark:text-brand-500" />
            <span>Patient Risk Assessment</span>
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Input patient parameters to execute predictive machine learning evaluation</p>
        </div>
        {result && (
          <button 
            onClick={() => setResult(null)} 
            className="flex items-center space-x-1.5 px-4 py-2 rounded-xl border border-slate-200/60 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-900 text-sm font-semibold text-slate-600 dark:text-slate-300 transition-all"
          >
            <ArrowLeft className="h-4 w-4" />
            <span>New Patient</span>
          </button>
        )}
      </div>

      {error && (
        <div className="flex items-center space-x-2 text-sm text-red-600 bg-red-50 dark:bg-red-950/20 dark:text-red-400 p-4 rounded-xl border border-red-200/50 dark:border-red-900/30">
          <AlertCircle className="h-5 w-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <AnimatePresence mode="wait">
        {!result ? (
          // Input Form View
          <motion.form 
            onSubmit={handleSubmit}
            className="space-y-6"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
          >
            {/* Tabs Navigation */}
            <div className="flex border-b border-slate-200 dark:border-slate-900 overflow-x-auto gap-2">
              {tabs.map((tab, idx) => {
                const Icon = tab.icon;
                const isSelected = activeTab === idx;
                return (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => {
                      setError('');
                      if (idx > activeTab) {
                        if (!validateStep(activeTab)) return;
                        for (let i = activeTab; i < idx; i++) {
                          if (!validateStep(i)) return;
                        }
                      }
                      setActiveTab(idx);
                    }}
                    className={`flex items-center space-x-1.5 px-4 py-3 border-b-2 font-medium text-sm transition-all whitespace-nowrap ${
                      isSelected
                        ? 'border-brand-600 text-brand-700 dark:text-brand-400 dark:border-brand-500'
                        : 'border-transparent text-slate-500 hover:text-slate-700 dark:hover:text-slate-300'
                    }`}
                  >
                    <Icon className="h-4.5 w-4.5" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </div>

            {/* Tab Panels */}
            <div className="glass-card p-6">
              {activeTab === 0 && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-1">
                    <label className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Suspected Cancer Type</label>
                    <select
                      className="clinical-input"
                      value={formData.Cancer_Type}
                      onChange={(e) => handleInputChange('Cancer_Type', e.target.value)}
                    >
                      {["Breast", "Prostate", "Lung", "Colon", "Skin"].map(type => (
                        <option key={type} value={type}>{type}</option>
                      ))}
                    </select>
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Patient Age</label>
                    <div className="flex items-center space-x-4">
                      <input
                        type="range"
                        min="1"
                        max="120"
                        className="w-full accent-brand-600 dark:accent-brand-500"
                        value={formData.Age}
                        onChange={(e) => handleInputChange('Age', e.target.value)}
                      />
                      <span className="w-12 text-center text-sm font-bold bg-slate-100 dark:bg-slate-900 px-2 py-1 rounded-lg border border-slate-200/50 dark:border-slate-800">{formData.Age}</span>
                    </div>
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Patient Gender</label>
                    <div className="grid grid-cols-2 gap-3">
                      {[
                        { label: "Female", val: 0 },
                        { label: "Male", val: 1 }
                      ].map(g => (
                        <button
                          key={g.val}
                          type="button"
                          onClick={() => handleInputChange('Gender', g.val)}
                          className={`px-4 py-2.5 rounded-xl border text-sm font-medium transition-all ${
                            formData.Gender === g.val
                              ? 'bg-brand-50 dark:bg-brand-950/20 border-brand-500 text-brand-700 dark:text-brand-400 font-bold'
                              : 'border-slate-200 hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-900 text-slate-600 dark:text-slate-400'
                          }`}
                        >
                          {g.label}
                        </button>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-1">
                    <label className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Body Mass Index (BMI)</label>
                    <input
                      type="number"
                      step="0.1"
                      min="10"
                      max="60"
                      className="clinical-input"
                      value={formData.BMI}
                      onChange={(e) => handleInputChange('BMI', e.target.value)}
                    />
                  </div>
                </div>
              )}

              {activeTab === 1 && (
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {[
                      { field: "Smoking", label: "Smoking habits Index" },
                      { field: "Alcohol_Use", label: "Alcohol consumption Index" },
                      { field: "Obesity", label: "Obesity profile Index" },
                      { field: "Physical_Activity", label: "Physical activity frequency" },
                      { field: "Physical_Activity_Level", label: "Active exercise level" },
                      { field: "Calcium_Intake", label: "Dietary Calcium Intake" },
                      { field: "Fruit_Veg_Intake", label: "Fruits & Vegetables Intake" },
                      { field: "Diet_Red_Meat", label: "Red Meat Diet Frequency" },
                      { field: "Diet_Salted_Processed", label: "Salted & Processed Diet Frequency" }
                    ].map(item => (
                      <div key={item.field} className="space-y-1.5">
                        <label className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider block">{item.label}</label>
                        <div className="flex items-center space-x-4">
                          <input
                            type="range"
                            min="0"
                            max="10"
                            className="w-full accent-brand-600 dark:accent-brand-500"
                            value={formData[item.field]}
                            onChange={(e) => handleInputChange(item.field, e.target.value)}
                          />
                          <span className="w-10 text-center text-sm font-bold bg-slate-100 dark:bg-slate-900 px-2 py-1 rounded-lg border border-slate-200/50 dark:border-slate-800">{formData[item.field]}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 2 && (
                <div className="space-y-6">
                  {/* Binary Genetic & Infection Toggles */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                    {[
                      { field: "Family_History", label: "Family Cancer History" },
                      { field: "BRCA_Mutation", label: "BRCA Genetic Mutation" },
                      { field: "H_Pylori_Infection", label: "Active H. Pylori Infection" }
                    ].map(item => (
                      <div key={item.field} className="space-y-2">
                        <label className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider block">{item.label}</label>
                        <div className="grid grid-cols-2 gap-2">
                          {[
                            { label: "Absent", val: 0 },
                            { label: "Present", val: 1 }
                          ].map(opt => (
                            <button
                              key={opt.val}
                              type="button"
                              onClick={() => handleInputChange(item.field, opt.val)}
                              className={`px-3 py-2 rounded-xl border text-sm font-medium transition-all ${
                                formData[item.field] === opt.val
                                  ? 'bg-brand-50 dark:bg-brand-950/20 border-brand-500 text-brand-700 dark:text-brand-400 font-bold'
                                  : 'border-slate-200 hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-900 text-slate-600 dark:text-slate-400'
                              }`}
                            >
                              {opt.label}
                            </button>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>

                  <hr className="border-slate-200/50 dark:border-slate-800" />

                  {/* Sliders for environmental triggers */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {[
                      { field: "Air_Pollution", label: "Environmental Air Pollution" },
                      { field: "Occupational_Hazards", label: "Workplace Occupational Hazards" }
                    ].map(item => (
                      <div key={item.field} className="space-y-1.5">
                        <label className="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider block">{item.label}</label>
                        <div className="flex items-center space-x-4">
                          <input
                            type="range"
                            min="0"
                            max="10"
                            className="w-full accent-brand-600 dark:accent-brand-500"
                            value={formData[item.field]}
                            onChange={(e) => handleInputChange(item.field, e.target.value)}
                          />
                          <span className="w-10 text-center text-sm font-bold bg-slate-100 dark:bg-slate-900 px-2 py-1 rounded-lg border border-slate-200/50 dark:border-slate-800">{formData[item.field]}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Navigation and Submit Buttons */}
            <div className="flex justify-between items-center pt-2">
              <button
                key="btn-prev"
                type="button"
                disabled={activeTab === 0}
                onClick={() => {
                  setError('');
                  setActiveTab(prev => Math.max(0, prev - 1));
                }}
                className="px-5 py-2.5 rounded-xl border border-slate-200 hover:bg-slate-50 dark:border-slate-800 dark:hover:bg-slate-900 text-sm font-semibold text-slate-600 dark:text-slate-300 disabled:opacity-40"
              >
                Previous
              </button>

              {activeTab < tabs.length - 1 ? (
                <button
                  key="btn-next"
                  type="button"
                  onClick={() => {
                    setError('');
                    if (validateStep(activeTab)) {
                      setActiveTab(prev => Math.min(tabs.length - 1, prev + 1));
                    }
                  }}
                  className="px-5 py-2.5 rounded-xl bg-slate-800 hover:bg-slate-900 text-white dark:bg-slate-900 dark:hover:bg-slate-800 text-sm font-semibold"
                >
                  Next Section
                </button>
              ) : (
                <button
                  key="btn-submit"
                  type="submit"
                  disabled={loading}
                  className="px-6 py-3 bg-brand-600 hover:bg-brand-700 dark:bg-brand-500 dark:hover:bg-brand-600 text-white font-bold rounded-xl shadow hover:shadow-md transition-all active:scale-[0.98] flex items-center space-x-2 disabled:opacity-50"
                >
                  {loading ? (
                    <>
                      <Loader className="h-5 w-5 animate-spin" />
                      <span>Processing clinical variables...</span>
                    </>
                  ) : (
                    <>
                      <Heart className="h-5 w-5" />
                      <span>Compute Risk Profile</span>
                    </>
                  )}
                </button>
              )}
            </div>
          </motion.form>
        ) : (
          // Prediction Result Dashboard View
          <motion.div
            className="grid grid-cols-1 lg:grid-cols-12 gap-8"
            initial={{ opacity: 0, scale: 0.98 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            {/* Left Column - Gauges and Narrative */}
            <div className="lg:col-span-5 space-y-6">
              <div className="glass-card p-6 text-center space-y-6 flex flex-col items-center">
                <h3 className="text-sm font-bold text-slate-400 uppercase tracking-widest">Diagnostic Outcome</h3>
                
                {/* Risk Level Badge */}
                <div className={`px-4 py-2 border rounded-2xl text-lg font-extrabold ${getRiskColorClass(result.prediction)}`}>
                  {result.prediction} Risk Level
                </div>

                {/* SVG circular confidence gauge */}
                {(() => {
                  const score = result.confidence_score;
                  const { strokeWidth, circumference, offset, radius } = getCircleParams(score);
                  return (
                    <div className="relative flex items-center justify-center h-32 w-32">
                      <svg className="h-32 w-32 transform -rotate-90">
                        <circle
                          cx="64"
                          cy="64"
                          r={radius}
                          strokeWidth={strokeWidth}
                          stroke="rgba(0,0,0,0.05)"
                          className="dark:stroke-slate-800"
                          fill="transparent"
                        />
                        <circle
                          cx="64"
                          cy="64"
                          r={radius}
                          strokeWidth={strokeWidth}
                          stroke={getBarColor(result.prediction)}
                          strokeDasharray={circumference}
                          strokeDashoffset={offset}
                          strokeLinecap="round"
                          fill="transparent"
                          className="transition-all duration-1000"
                        />
                      </svg>
                      <div className="absolute flex flex-col items-center">
                        <span className="text-3xl font-extrabold text-slate-800 dark:text-white">{(score * 100).toFixed(0)}%</span>
                        <span className="text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">Confidence</span>
                      </div>
                    </div>
                  );
                })()}
              </div>

              {/* Explainer Narrative Card */}
              <div className="glass-card p-6 space-y-4">
                <h3 className="text-sm font-bold text-slate-700 dark:text-slate-300 flex items-center space-x-1.5">
                  <Sparkles className="h-4.5 w-4.5 text-brand-600 dark:text-brand-500" />
                  <span>Clinical Narrative</span>
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed italic bg-slate-50 dark:bg-slate-900/40 p-4 rounded-xl border border-slate-200/40 dark:border-slate-800">
                  "{result.explanation_narrative}"
                </p>
              </div>
            </div>
            {/* Right Column - Clinical SHAP Explainability Chart */}
            <div className="lg:col-span-7 space-y-6">
              <div className="glass-card p-6 space-y-4 flex flex-col h-full justify-between">
                <div className="space-y-1.5">
                  <h3 className="text-sm font-bold text-slate-700 dark:text-slate-300 flex items-center space-x-1.5">
                    <Award className="h-5 w-5 text-brand-600 dark:text-brand-500" />
                    <span>Clinical SHAP Explainability</span>
                  </h3>
                  <p className="text-xs text-slate-400">Relative risk impact (positive values drive risk up, negative values drive risk down)</p>
                </div>

                {/* Recharts Bar Chart */}
                <div className="h-72 w-full mt-4">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={result.contributing_factors}
                      layout="vertical"
                      margin={{ top: 5, right: 30, left: 10, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" horizontal={true} vertical={true} stroke="#e2e8f0" className="dark:stroke-slate-800" />
                      <XAxis type="number" tick={{ fill: '#94a3b8', fontSize: 10 }} axisLine={false} tickLine={false} />
                      <YAxis 
                        dataKey="factor" 
                        type="category" 
                        tick={{ fill: '#94a3b8', fontSize: 11 }} 
                        width={150} 
                        axisLine={false}
                        tickLine={false}
                      />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: '#0f172a', 
                          border: 'none', 
                          borderRadius: '8px', 
                          fontSize: '11px',
                          color: '#fff'
                        }}
                        labelStyle={{ color: '#94a3b8' }}
                        formatter={(value) => [value.toFixed(4), "SHAP Contribution"]}
                      />
                      <Bar dataKey="shap_value" radius={4} barSize={14}>
                        {result.contributing_factors.map((entry, index) => (
                          <Cell 
                            key={`cell-${index}`} 
                            fill={entry.shap_value > 0 ? '#ef4444' : '#10b981'} 
                          />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </div>

                {/* Factors Legend */}
                <div className="flex items-center justify-end space-x-6 text-[10px] uppercase font-bold tracking-widest pt-4 border-t border-slate-200/50 dark:border-slate-800">
                  <span className="flex items-center space-x-1.5 text-emerald-500"><div className="h-2 w-2 rounded-full bg-emerald-500" /><span>Protective (Mitigates Risk)</span></span>
                  <span className="flex items-center space-x-1.5 text-red-500"><div className="h-2 w-2 rounded-full bg-red-500" /><span>Promoting (Increases Risk)</span></span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
