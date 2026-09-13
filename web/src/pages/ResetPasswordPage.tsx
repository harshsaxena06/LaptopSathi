import React, { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { AuthLayout } from '@/components/auth/AuthLayout';
import { AuthCard } from '@/components/auth/AuthCard';
import { PasswordInput } from '@/components/auth/PasswordInput';
import { PasswordStrengthMeter } from '@/components/auth/PasswordStrengthMeter';
import { authApi } from '@/api/authApi';
import { ApiError } from '@/types/auth';
import { passwordIssues } from '@/lib/validators';

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') || '';
  const navigate = useNavigate();

  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  function validate(): boolean {
    const next: Record<string, string> = {};
    const issues = passwordIssues(password);
    if (issues.length) next.password = `Password needs: ${issues.join(', ').toLowerCase()}`;
    if (password !== confirmPassword) next.confirmPassword = 'Passwords do not match';
    setErrors(next);
    return Object.keys(next).length === 0;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setFormError(null);
    if (!token) {
      setFormError('This reset link is missing its token. Please request a new one.');
      return;
    }
    if (!validate()) return;

    setIsSubmitting(true);
    try {
      await authApi.resetPassword(token, password);
      setSuccess(true);
      setTimeout(() => navigate('/login'), 2000);
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : 'Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <AuthLayout>
      <AuthCard>
        {success ? (
          <div style={{ textAlign: 'center', padding: '12px 0' }}>
            <h2 className="auth-heading" style={{ textAlign: 'center' }}>Password reset</h2>
            <p className="auth-subheading" style={{ textAlign: 'center' }}>
              Redirecting you to login…
            </p>
          </div>
        ) : (
          <>
            <h2 className="auth-heading">Reset Password</h2>
            <p className="auth-subheading">Choose a new password for your account.</p>

            {formError && (
              <p className="field-error" role="alert" style={{ marginBottom: 14 }}>{formError}</p>
            )}

            <form onSubmit={handleSubmit} noValidate>
              <div className="field">
                <label htmlFor="reset-password">New password</label>
                <PasswordInput
                  id="reset-password"
                  value={password}
                  onChange={setPassword}
                  autoComplete="new-password"
                  error={errors.password}
                />
                <PasswordStrengthMeter password={password} />
              </div>
              <div className="field">
                <label htmlFor="reset-confirm">Confirm new password</label>
                <PasswordInput
                  id="reset-confirm"
                  value={confirmPassword}
                  onChange={setConfirmPassword}
                  autoComplete="new-password"
                  error={errors.confirmPassword}
                />
              </div>
              <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
                {isSubmitting ? 'Resetting…' : 'Reset password'}
              </button>
            </form>

            <p className="auth-switch-row">
              <Link to="/login" className="btn-link">Back to login</Link>
            </p>
          </>
        )}
      </AuthCard>
    </AuthLayout>
  );
}
