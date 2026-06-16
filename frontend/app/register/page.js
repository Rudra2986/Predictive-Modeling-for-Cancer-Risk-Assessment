"use client";

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { Lock, Mail, Activity, AlertCircle, Loader, UserPlus } from 'lucide-react';
import { api, setToken } from '../../utils/api';

export default function Register() {
  const router = useRouter();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Client-side validations
    if (password.length < 8) {
      setError('Password must be at least 8 characters long.');
      return;
    }
    if (!/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/[0-9]/.test(password)) {
      setError('Password must contain at least one uppercase letter, one lowercase letter, and one digit.');
      return;
    }
    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);

    try {
      // 1. Call registration API
      await api.post('/auth/register', { email, password });
      
      // 2. Automatically log in after registration
      const loginData = await api.post('/auth/login', { email, password });
      setToken(loginData.access_token);
      
      // Synchronize navbar auth state
      window.dispatchEvent(new Event('auth-change'));
      router.push('/dashboard');
    } catch (err) {
      setError(err.message || 'Registration failed. Email might already be registered.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-[75vh]">
      <motion.div
        className="glass-card p-8 w-full max-w-md space-y-6"
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.3 }}
      >
        {/* Branding header */}
        <div className="text-center space-y-2">
          <div className="inline-flex p-3 rounded-full bg-brand-50 dark:bg-brand-950/30 text-brand-600 dark:text-brand-400 mb-1">
            <UserPlus className="h-8 w-8" />
          </div>
          <h1 className="text-2xl font-extrabold text-slate-800 dark:text-white">Create Account</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400">Register a clinician account to audit patient runs</p>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="flex items-center space-x-2 text-sm text-red-600 bg-red-50 dark:bg-red-950/20 dark:text-red-400 p-3.5 rounded-xl border border-red-200/50 dark:border-red-900/30">
            <AlertCircle className="h-5 w-5 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* Input Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-500 dark:text-slate-400 block">Email Address</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400">
                <Mail className="h-4 w-4" />
              </span>
              <input
                type="email"
                required
                className="clinical-input pl-10"
                placeholder="clinician@hospital.org"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-500 dark:text-slate-400 block">Password</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400">
                <Lock className="h-4 w-4" />
              </span>
              <input
                type="password"
                required
                className="clinical-input pl-10"
                placeholder="Min 8 characters (A-Z, a-z, 0-9)"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-xs font-semibold text-slate-500 dark:text-slate-400 block">Confirm Password</label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-slate-400">
                <Lock className="h-4 w-4" />
              </span>
              <input
                type="password"
                required
                className="clinical-input pl-10"
                placeholder="Retype password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full interactive-button bg-brand-600 hover:bg-brand-700 dark:bg-brand-500 dark:hover:bg-brand-600 text-white font-semibold flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader className="h-5 w-5 animate-spin" />
                <span>Creating account...</span>
              </>
            ) : (
              <span>Sign Up</span>
            )}
          </button>
        </form>

        <div className="text-center pt-2 text-sm text-slate-500 dark:text-slate-400">
          <span>Already have an account? </span>
          <Link href="/login" className="font-bold text-brand-600 dark:text-brand-500 hover:text-brand-700 dark:hover:text-brand-400 transition-colors">
            Sign In
          </Link>
        </div>
      </motion.div>
    </div>
  );
}
