"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { Sun, Moon, Activity, LogOut, User, Menu, X, BarChart3, History, Shield } from 'lucide-react';
import { getToken, setToken } from '@/utils/api';

export default function Navbar() {
  const pathname = usePathname();
  const router = useRouter();
  const [theme, setTheme] = useState('light');
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userLabel, setUserLabel] = useState('');
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);

  useEffect(() => {
    // Sync login state
    const syncAuthState = () => {
      const token = getToken();
      setIsAuthenticated(!!token);
      if (token) {
        try {
          const payload = JSON.parse(atob(token.split('.')[1]));
          setUserLabel(payload.sub ? `ID: ${payload.sub}` : 'Clinician');
          setIsAdmin(!!payload.is_admin);
        } catch (_) {
          setUserLabel('Clinician');
          setIsAdmin(false);
        }
      } else {
        setUserLabel('');
        setIsAdmin(false);
      }
    };

    syncAuthState();

    // Init theme
    const isDark = document.documentElement.classList.contains('dark');
    setTheme(isDark ? 'dark' : 'light');

    // Watch for custom state updates
    window.addEventListener('auth-change', syncAuthState);
    return () => window.removeEventListener('auth-change', syncAuthState);
  }, []);

  const toggleTheme = () => {
    const root = document.documentElement;
    if (root.classList.contains('dark')) {
      root.classList.remove('dark');
      localStorage.setItem('theme', 'light');
      setTheme('light');
    } else {
      root.classList.add('dark');
      localStorage.setItem('theme', 'dark');
      setTheme('dark');
    }
  };

  const handleLogout = () => {
    setToken(null);
    window.dispatchEvent(new Event('auth-change'));
    setIsMobileMenuOpen(false);
    router.push('/');
  };

  const navLinks = [
    { name: 'Run Assessment', href: '/predict', icon: Activity },
    ...(isAuthenticated ? [
      ...(isAdmin ? [{ name: 'Dashboard', href: '/dashboard', icon: BarChart3 }] : []),
      { name: 'History', href: '/history', icon: History }
    ] : [])
  ];

  return (
    <nav className="sticky top-0 z-50 bg-white/80 dark:bg-slate-950/80 backdrop-blur-md border-b border-slate-200/60 dark:border-slate-900 transition-colors duration-300">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo / Brand */}
          <div className="flex items-center">
            <Link href="/" className="flex items-center space-x-2 text-brand-600 dark:text-brand-500 font-bold text-xl group">
              <Activity className="h-6 w-6 stroke-[2.5] transition-transform duration-300 group-hover:scale-110" />
              <span className="font-heading tracking-tight text-slate-800 dark:text-slate-100">OncoRisk <span className="text-brand-600 dark:text-brand-500">AI</span></span>
            </Link>
          </div>

          {/* Desktop Navigation Links */}
          <div className="hidden md:flex items-center space-x-6">
            {navLinks.map((link) => {
              const Icon = link.icon;
              const isActive = pathname === link.href;
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className={`flex items-center space-x-1 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'text-brand-700 bg-brand-50/60 dark:text-brand-400 dark:bg-brand-500/15'
                      : 'text-slate-600 dark:text-slate-300 hover:text-brand-600 dark:hover:text-brand-400 hover:bg-slate-100/50 dark:hover:bg-slate-900/40'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{link.name}</span>
                </Link>
              );
            })}
          </div>

          {/* Right Action Items */}
          <div className="hidden md:flex items-center space-x-4">
            {/* Theme Toggle Button */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-900 hover:text-slate-800 dark:hover:text-slate-100 transition-all duration-200"
              aria-label="Toggle Theme"
            >
              {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </button>

            {/* Profile / Auth Operations */}
            {isAuthenticated ? (
              <div className="flex items-center space-x-4 border-l border-slate-200 dark:border-slate-800 pl-4">
                <span className="flex items-center space-x-1.5 text-xs font-semibold text-slate-500 dark:text-slate-400 bg-slate-100 dark:bg-slate-900 px-2.5 py-1.5 rounded-lg">
                  <User className="h-3.5 w-3.5" />
                  <span>{userLabel}</span>
                </span>
                <button
                  onClick={handleLogout}
                  className="flex items-center space-x-1 text-sm font-medium text-slate-600 dark:text-slate-400 hover:text-red-500 dark:hover:text-red-400 hover:bg-red-50/40 dark:hover:bg-red-950/10 px-3 py-2 rounded-lg transition-all duration-200"
                >
                  <LogOut className="h-4 w-4" />
                  <span>Logout</span>
                </button>
              </div>
            ) : (
              <div className="flex items-center space-x-3 border-l border-slate-200 dark:border-slate-800 pl-4">
                <Link
                  href="/login"
                  className="text-sm font-semibold text-slate-700 dark:text-slate-300 hover:text-brand-600 dark:hover:text-brand-400 px-3 py-2 transition-all"
                >
                  Login
                </Link>
                <Link
                  href="/register"
                  className="px-4 py-2 text-sm font-semibold text-white bg-brand-600 hover:bg-brand-700 dark:bg-brand-500 dark:hover:bg-brand-600 rounded-lg shadow-sm hover:shadow active:scale-[0.98] transition-all duration-150"
                >
                  Sign Up
                </Link>
              </div>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden flex items-center space-x-2">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-lg text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-900"
            >
              {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
            </button>
            <button
              onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
              className="p-2 rounded-lg text-slate-600 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-900"
            >
              {isMobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer Navigation Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t border-slate-200 dark:border-slate-900 bg-white dark:bg-slate-950 px-4 pt-2 pb-4 space-y-1 shadow-inner">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setIsMobileMenuOpen(false)}
                className={`flex items-center space-x-2 px-3 py-3 rounded-lg text-base font-medium transition-all ${
                  isActive
                    ? 'text-brand-700 bg-brand-50 dark:text-brand-400 dark:bg-brand-500/15'
                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-900'
                }`}
              >
                <Icon className="h-5 w-5" />
                <span>{link.name}</span>
              </Link>
            );
          })}

          {isAuthenticated ? (
            <div className="pt-4 border-t border-slate-200 dark:border-slate-800 space-y-2">
              <div className="flex items-center space-x-2 px-3 py-2 text-slate-500 dark:text-slate-400 text-sm font-semibold">
                <User className="h-4 w-4" />
                <span>{userLabel}</span>
              </div>
              <button
                onClick={handleLogout}
                className="flex w-full items-center space-x-2 px-3 py-3 rounded-lg text-base font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-950/20 transition-all"
              >
                <LogOut className="h-5 w-5" />
                <span>Logout</span>
              </button>
            </div>
          ) : (
            <div className="pt-4 border-t border-slate-200 dark:border-slate-800 grid grid-cols-2 gap-2">
              <Link
                href="/login"
                onClick={() => setIsMobileMenuOpen(false)}
                className="flex items-center justify-center px-4 py-2.5 border border-slate-200 dark:border-slate-800 rounded-xl text-slate-700 dark:text-slate-300 text-sm font-medium hover:bg-slate-50 dark:hover:bg-slate-900"
              >
                Login
              </Link>
              <Link
                href="/register"
                onClick={() => setIsMobileMenuOpen(false)}
                className="flex items-center justify-center px-4 py-2.5 bg-brand-600 dark:bg-brand-500 rounded-xl text-white text-sm font-semibold hover:bg-brand-700"
              >
                Sign Up
              </Link>
            </div>
          )}
        </div>
      )}
    </nav>
  );
}
