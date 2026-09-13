import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { useToast } from '@/context/ToastContext';
import { ApiError } from '@/types/auth';
import { isValidEmail } from '@/lib/validators';
import { PasswordInput } from './PasswordInput';
import { ArrowLeftIcon, ShieldIcon, MailIcon } from '../Icons';

interface AdminLoginFormProps {
  onSwitchToUser: () => void;
}

export function AdminLoginForm({ onSwitchToUser }: AdminLoginFormProps) {
  const { adminLogin } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  function validate(): boolean {
    const next: typeof errors = {};
    if (!isValidEmail(email)) next.email = 'Enter a valid email address';
    if (!password) next.password = 'Password is required';
    setErrors(next);
    return Object.keys(next).length === 0;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setFormError(null);
    if (!validate()) return;

    setIsSubmitting(true);
    try {
      await adminLogin(email, password);
      showToast('Welcome back, admin.', 'success');
      navigate('/admin');
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : 'Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <>
      <h2 className="auth-heading">
        <span style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
          <ShieldIcon width={20} height={20} style={{ color: 'var(--accent)' }} />
          Admin Login
        </span>
      </h2>
      <p className="auth-subheading">Restricted access — administrators only</p>

      <div className="admin-toggle-row">
        <button type="button" className="admin-toggle-link" onClick={onSwitchToUser}>
          <ArrowLeftIcon width={13} height={13} /> Back to User Login
        </button>
      </div>

      {formError && (
        <p className="field-error" role="alert" style={{ marginBottom: 14 }}>
          {formError}
        </p>
      )}

      <form onSubmit={handleSubmit} noValidate>
        <div className="field">
          <label htmlFor="admin-email">Admin Email</label>
          <div className="control-icon-wrap">
            <MailIcon width={15} height={15} className="control-icon" aria-hidden="true" />
            <input
              id="admin-email"
              className="control"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="admin@laptopsathi.ai"
              autoComplete="email"
              aria-invalid={!!errors.email}
            />
          </div>
          {errors.email && <p className="field-error" role="alert">{errors.email}</p>}
        </div>

        <div className="field">
          <label htmlFor="admin-password">Password</label>
          <PasswordInput
            id="admin-password"
            value={password}
            onChange={setPassword}
            autoComplete="current-password"
            error={errors.password}
          />
        </div>

        <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
          {isSubmitting ? 'Signing in…' : 'Login'}
        </button>
      </form>
    </>
  );
}
