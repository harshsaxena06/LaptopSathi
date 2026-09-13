import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useTheme } from '@/context/ThemeContext';
import { AuthCard } from '@/components/auth/AuthCard';
import { RegisterForm } from '@/components/auth/RegisterForm';
import { CloseIcon, SunIcon, MoonIcon } from '@/components/Icons';

/**
 * Same presentation as the Sign In dialog (AuthModal) — a centered card over
 * a soft branded backdrop — just reached by navigating to /register directly
 * instead of opening as an overlay. Closing returns to the landing page.
 */
export function RegisterPage() {
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();

  return (
    <div className="auth-page-backdrop">
      <button
        type="button"
        className="auth-page-theme-toggle"
        onClick={toggleTheme}
        aria-label={theme === 'dark' ? 'Switch to light theme' : 'Switch to dark theme'}
      >
        {theme === 'dark' ? <SunIcon width={16} height={16} /> : <MoonIcon width={16} height={16} />}
      </button>

      <div className="auth-modal-dialog auth-page-dialog">
        <button
          type="button"
          className="auth-modal-close"
          onClick={() => navigate('/login')}
          aria-label="Close"
        >
          <CloseIcon width={16} height={16} />
        </button>
        <AuthCard>
          <RegisterForm />
        </AuthCard>
      </div>
    </div>
  );
}
