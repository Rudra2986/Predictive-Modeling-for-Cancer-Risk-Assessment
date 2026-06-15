import { Inter, Outfit } from 'next/font/google';
import '../styles/globals.css';
import Navbar from '../components/Navbar';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const outfit = Outfit({
  subsets: ['latin'],
  variable: '--font-outfit',
  display: 'swap',
});

export const metadata = {
  title: 'OncoRisk AI | Predictive Cancer Risk Assessment',
  description: 'Production-grade healthcare AI platform for predictive modeling and explainable clinical cancer risk assessment using patient lifestyle and genetic profiles.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${inter.variable} ${outfit.variable}`}>
      <head>
        <script dangerouslySetInnerHTML={{__html: `
          (function() {
            try {
              const theme = localStorage.getItem('theme');
              if (theme === 'dark' || (!theme && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
                document.documentElement.classList.add('dark');
              } else {
                document.documentElement.classList.remove('dark');
              }
            } catch (e) {}
          })();
        `}} />
      </head>
      <body className="min-h-screen flex flex-col bg-slate-50/40 text-slate-850 dark:bg-slate-950 dark:text-slate-100">
        <Navbar />
        <main className="flex-1 w-full max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
          {children}
        </main>
        <footer className="py-6 border-t border-slate-200/50 dark:border-slate-900 bg-white/40 dark:bg-slate-950 text-center text-xs text-slate-400">
          <p>© {new Date().getFullYear()} OncoRisk AI. All rights reserved. Clinical Decision Support System. Not a diagnostic replacement.</p>
        </footer>
      </body>
    </html>
  );
}
