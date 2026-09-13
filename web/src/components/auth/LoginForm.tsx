import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { useToast } from '@/context/ToastContext';
import { ApiError } from '@/types/auth';
import { isValidEmail } from '@/lib/validators';
import { PasswordInput } from './PasswordInput';
import { RememberMeCheckbox } from './RememberMeCheckbox';
import { MailIcon } from '../Icons';

interface LoginFormProps {
  onSwitchToAdmin: () => void;
}

export function LoginForm({ onSwitchToAdmin }: LoginFormProps) {
  const { login } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
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
      await login(email, password, rememberMe);
      showToast('Welcome back!', 'success');
      navigate('/dashboard');
    } catch (err) {
      if (err instanceof ApiError) {
        setFormError(err.message);
      } else {
        setFormError('Something went wrong. Please try again.');
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <>
      <h2 className="auth-heading">Welcome Back</h2>
      <p className="auth-subheading">Sign in to continue to LaptopSathi AI</p>

      <div className="admin-toggle-row">
        <button type="button" className="admin-toggle-link" onClick={onSwitchToAdmin}>
          Click here for Admin Login →
        </button>
      </div>

      {formError && (
        <p className="field-error" role="alert" style={{ marginBottom: 14 }}>
          {formError}
        </p>
      )}

      <form onSubmit={handleSubmit} noValidate>
        <div className="field">
          <label htmlFor="login-email">Email</label>
          <div className="control-icon-wrap">
            <MailIcon width={15} height={15} className="control-icon" aria-hidden="true" />
            <input
              id="login-email"
              className="control"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              autoComplete="email"
              aria-invalid={!!errors.email}
            />
          </div>
          {errors.email && <p className="field-error" role="alert">{errors.email}</p>}
        </div>

        <div className="field">
          <label htmlFor="login-password">Password</label>
          <PasswordInput
            id="login-password"
            value={password}
            onChange={setPassword}
            autoComplete="current-password"
            error={errors.password}
          />
        </div>

        <div className="form-row-between">
          <RememberMeCheckbox checked={rememberMe} onChange={setRememberMe} />
          <Link to="/forgot-password" className="btn-link">Forgot Password?</Link>
        </div>

        <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
          {isSubmitting ? 'Signing in…' : 'Login'}
        </button>
      </form>

      <p className="auth-switch-row">
        Don&apos;t have an account? <Link to="/register" className="btn-link">Create Account</Link>
      </p>
    </>
  );
}
