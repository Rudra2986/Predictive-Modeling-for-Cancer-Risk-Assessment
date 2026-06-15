"use client";

import Link from 'next/link';
import { motion } from 'framer-motion';
import { Shield, BrainCircuit, Activity, Database, Sparkles, ArrowRight, CheckCircle2 } from 'lucide-react';

export default function Home() {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.15 }
    }
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { y: 0, opacity: 1, transition: { duration: 0.5, ease: 'easeOut' } }
  };

  const features = [
    {
      title: "Optimized ML Engine",
      desc: "XGBoost and Random Forest classifiers fine-tuned using Optuna, resolving class imbalance with SMOTE for high-precision patient classification.",
      icon: BrainCircuit,
      color: "text-brand-600 dark:text-brand-400 bg-brand-50 dark:bg-brand-950/30"
    },
    {
      title: "Clinical Explainability",
      desc: "Mathematical feature importances translated by a custom rule engine into clear plain-English diagnostic narratives and contribution score charts.",
      icon: Sparkles,
      color: "text-amber-600 dark:text-amber-400 bg-amber-50 dark:bg-amber-950/30"
    },
    {
      title: "Auditable Data Persistence",
      desc: "Decoupled PostgreSQL persistent database storage mapping history logs, recent assessment runs, and aggregated time-series query counts.",
      icon: Database,
      color: "text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-950/30"
    },
    {
      title: "Rigorous Security Protocols",
      desc: "Defended against SQL Injections using parameterized query binding, secure bcrypt hashing contexts, and signed JWT authentication sessions.",
      icon: Shield,
      color: "text-emerald-600 dark:text-emerald-400 bg-emerald-50 dark:bg-emerald-950/30"
    }
  ];

  return (
    <div className="space-y-16 py-4">
      {/* Hero Section */}
      <motion.div 
        className="text-center max-w-4xl mx-auto space-y-6"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <span className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-full text-xs font-semibold bg-brand-50 dark:bg-brand-950/20 text-brand-700 dark:text-brand-400 border border-brand-200/50 dark:border-brand-900/30">
          <Activity className="h-3.5 w-3.5" />
          <span>Clinical Decision Support Platform</span>
        </span>
        <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-slate-900 dark:text-white leading-[1.15]">
          Predictive Modeling for <br />
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-600 to-teal-400 dark:from-brand-400 dark:to-teal-300">
            Cancer Risk Assessment
          </span>
        </h1>
        <p className="text-lg sm:text-xl text-slate-500 dark:text-slate-400 max-w-2xl mx-auto leading-relaxed">
          OncoRisk AI integrates clinical and lifestyle patient datasets with optimized machine learning pipelines to assist clinicians with diagnostic insights.
        </p>

        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
          <Link
            href="/predict"
            className="w-full sm:w-auto px-6 py-3.5 bg-brand-600 hover:bg-brand-700 text-white rounded-xl font-bold shadow-md hover:shadow-lg transition-all active:scale-[0.98] flex items-center justify-center space-x-2"
          >
            <span>Start Assessment</span>
            <ArrowRight className="h-4 w-4" />
          </Link>
          <Link
            href="/register"
            className="w-full sm:w-auto px-6 py-3.5 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 hover:bg-slate-50 dark:hover:bg-slate-850 text-slate-700 dark:text-slate-200 rounded-xl font-bold shadow-sm transition-all"
          >
            Register Account
          </Link>
        </div>
      </motion.div>

      {/* Feature Cards Grid */}
      <motion.div 
        className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6"
        variants={containerVariants}
        initial="hidden"
        animate="visible"
      >
        {features.map((feature, idx) => {
          const Icon = feature.icon;
          return (
            <motion.div 
              key={idx}
              className="glass-card p-6 flex items-start space-x-4 hover:translate-y-[-2px]"
              variants={itemVariants}
            >
              <div className={`p-3 rounded-xl ${feature.color} flex-shrink-0`}>
                <Icon className="h-6 w-6" />
              </div>
              <div className="space-y-1.5">
                <h3 className="text-lg font-bold text-slate-800 dark:text-slate-100">{feature.title}</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed">{feature.desc}</p>
              </div>
            </motion.div>
          );
        })}
      </motion.div>

      {/* Platform Security & Validation section */}
      <motion.div 
        className="glass-card p-8 bg-gradient-to-br from-white to-slate-50 dark:from-slate-900 dark:to-slate-950 border border-slate-200/50 dark:border-slate-800/80 shadow-md rounded-3xl"
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        transition={{ duration: 0.5 }}
      >
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          <div className="lg:col-span-7 space-y-4">
            <div className="flex items-center space-x-2 text-emerald-600 dark:text-emerald-400 font-semibold text-sm">
              <Shield className="h-5 w-5" />
              <span>Full Security Compliance Verified</span>
            </div>
            <h2 className="text-2xl sm:text-3xl font-bold text-slate-900 dark:text-white">
              Secured Against Cyber Risks & SQL Injections
            </h2>
            <p className="text-sm sm:text-base text-slate-500 dark:text-slate-400 leading-relaxed">
              We employ military-grade security safeguards at both application and data persistence layers to audit logs and patient data securely:
            </p>
            
            <ul className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm font-medium">
              {[
                "Parameterized SQL Bindings (ORM)",
                "Cryptographic bcrypt Password Hashing",
                "Restricted Access CORS Policy",
                "Signed JWT Session Verification Tokens"
              ].map((text, i) => (
                <li key={i} className="flex items-center space-x-2 text-slate-600 dark:text-slate-350">
                  <CheckCircle2 className="h-4.5 w-4.5 text-emerald-500 flex-shrink-0" />
                  <span>{text}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="lg:col-span-5 flex justify-center">
            <div className="relative p-6 bg-slate-100 dark:bg-slate-950 border border-slate-200/70 dark:border-slate-800 rounded-2xl w-full max-w-sm font-mono text-[11px] leading-relaxed shadow-inner select-none text-slate-600 dark:text-slate-400">
              <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800 mb-3 text-slate-400">
                <span className="flex items-center space-x-1.5"><div className="h-2 w-2 rounded-full bg-red-400" /><div className="h-2 w-2 rounded-full bg-yellow-400" /><div className="h-2 w-2 rounded-full bg-green-400" /></span>
                <span>api_security_audit.log</span>
              </div>
              <p className="text-brand-600 dark:text-brand-400">INFO: Database: Connected to PostgreSQL</p>
              <p className="text-emerald-500">INFO: Schemas: Bind checks complete [No Raw SQL]</p>
              <p>INFO: API: Mounting CORS restrictions origin:3000</p>
              <p className="text-purple-500">INFO: Auth: passlib.bcrypt CryptContext loaded</p>
              <p className="text-slate-400 mt-2"># Request sanitization active via Pydantic</p>
              <p className="text-slate-400"># SQL injection queries escaped by query-compiler</p>
            </div>
          </div>
        </div>
      </motion.div>
    </div>
  );
}
