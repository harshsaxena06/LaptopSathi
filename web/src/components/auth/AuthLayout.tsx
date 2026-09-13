import React from 'react';
import { Link } from 'react-router-dom';
import { AuthIllustration } from '../AuthIllustration';
import { CheckIcon, SunIcon, MoonIcon } from '../Icons';
import { useTheme } from '@/context/ThemeContext';

const FEATURES = [
  'AI Powered Recommendations',
  'Semantic Search',
  'Budget Optimization',
  'Explainable AI',
  'Personalized Suggestions',
  'Hardware Comparison',
];

interface AuthLayoutProps {
  children: React.ReactNode;
}

export function AuthLayout({ children }: AuthLayoutProps) {
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="auth-shell">
      <aside className="auth-side">
        <Link to="/login" className="auth-brand" style={{ textDecoration: 'none', color: 'inherit' }}>
          <div className="auth-brand-mark" aria-hidden="true"><img src="/logo-mark.png" alt="" /></div>
          <div className="auth-brand-name">Laptop<span>Sathi</span> AI</div>
        </Link>

        <div>
          <div className="auth-illustration">
            <AuthIllustration />
          </div>
          <h1 className="auth-tagline">
            Your <em>Intelligent</em> Laptop Decision Platform
          </h1>
          <p className="auth-subtagline">
            Explainable, AI-powered recommendations built on a real knowledge base —
            not another affiliate comparison site.
          </p>
          <ul className="feature-list">
            {FEATURES.map((f) => (
              <li key={f}>
                <span className="check" aria-hidden="true">
                  <CheckIcon width={12} height={12} />
                </span>
                {f}
              </li>
            ))}
          </ul>
        </div>

        <div className="auth-side-footer">
          <span className="credit">
            Built by <strong>Harsh Saxena</strong>
          </span>
          <span>v1.0 · AI-Powered</span>
        </div>
      </aside>

      <div className="auth-form-side">
        <button
          type="button"
          className="auth-theme-toggle"
          onClick={toggleTheme}
          aria-label={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
        >
          {theme === 'dark' ? <SunIcon width={16} height={16} /> : <MoonIcon width={16} height={16} />}
        </button>

        <div className="auth-card-wrap">
          <div className="auth-card-mobile-brand">
            <div className="auth-brand-mark" aria-hidden="true"><img src="/logo-mark.png" alt="" /></div>
            <div className="auth-brand-name">Laptop<span>Sathi</span> AI</div>
          </div>
          {children}
        </div>
      </div>
    </div>
  );
}
