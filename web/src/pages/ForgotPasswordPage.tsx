import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { AuthLayout } from '@/components/auth/AuthLayout';
import { AuthCard } from '@/components/auth/AuthCard';
import { authApi } from '@/api/authApi';
import { ApiError } from '@/types/auth';
import { isValidEmail } from '@/lib/validators';
import { ArrowLeftIcon, CheckIcon } from '@/components/Icons';

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!isValidEmail(email)) {
      setError('Enter a valid email address');
      return;
    }
    setIsSubmitting(true);
    try {
      await authApi.forgotPassword(email);
      setSubmitted(true);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthLayout>
      <AuthCard>
        {submitted ? (
          <div style={{ textAlign: 'center', padding: '12px 0' }}>
            <div
              style={{
                width: 48, height: 48, borderRadius: '50%', background: 'var(--green-soft)', color: 'var(--green)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px',
              }}
            >
              <CheckIcon width={22} height={22} />
            </div>
            <h2 className="auth-heading" style={{ textAlign: 'center' }}>Check your email</h2>
            <p className="auth-subheading" style={{ textAlign: 'center' }}>
              If an account exists for <strong>{email}</strong>, a password reset link has been sent.
            </p>
            <Link to="/login" className="btn btn-ghost" style={{ marginTop: 8, textDecoration: 'none' }}>
              Back to login
            </Link>
          </div>
        ) : (
          <>
            <h2 className="auth-heading">Forgot Password?</h2>
            <p className="auth-subheading">
              Enter the email associated with your account and we&apos;ll send you a reset link.
            </p>

            {error && (
              <p className="field-error" role="alert" style={{ marginBottom: 14 }}>{error}</p>
            )}

            <form onSubmit={handleSubmit} noValidate>
              <div className="field">
                <label htmlFor="forgot-email">Email</label>
                <input
                  id="forgot-email"
                  className="control"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="you@example.com"
                  autoComplete="email"
                />
              </div>
              <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
                {isSubmitting ? 'Sending…' : 'Send reset link'}
              </button>
            </form>

            <p className="auth-switch-row">
              <Link to="/login" className="btn-link" style={{ display: 'inline-flex', alignItems: 'center', gap: 6 }}>
                <ArrowLeftIcon width={13} height={13} /> Back to login
              </Link>
            </p>
          </>
        )}
      </AuthCard>
    </AuthLayout>
  );
}
