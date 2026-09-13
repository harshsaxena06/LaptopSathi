import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { useToast } from '@/context/ToastContext';
import { ApiError } from '@/types/auth';
import { isValidEmail, passwordIssues } from '@/lib/validators';
import { PasswordInput } from './PasswordInput';
import { PasswordStrengthMeter } from './PasswordStrengthMeter';
import { MailIcon } from '../Icons';

const RESEND_COOLDOWN_SECONDS = 30;

export function RegisterForm() {
  const { registerStart, verifyRegistrationOtp, resendRegistrationOtp } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [agreeToTerms, setAgreeToTerms] = useState(false);

  const [errors, setErrors] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Step 2: OTP entry, shown once step 1 succeeds
  const [pendingEmail, setPendingEmail] = useState<string | null>(null);
  const [otp, setOtp] = useState('');
  const [otpError, setOtpError] = useState<string | null>(null);
  const [verifying, setVerifying] = useState(false);
  const [resendCooldown, setResendCooldown] = useState(0);
  const [resending, setResending] = useState(false);

  function validate(): boolean {
    const next: Record<string, string> = {};
    if (!fullName.trim()) next.fullName = 'Enter your name';
    if (!isValidEmail(email)) next.email = 'Enter a valid email address';
    const issues = passwordIssues(password);
    if (issues.length) next.password = `Password needs: ${issues.join(', ').toLowerCase()}`;
    if (password !== confirmPassword) next.confirmPassword = 'Passwords do not match';
    if (!agreeToTerms) next.agreeToTerms = 'You must accept the terms to continue';
    setErrors(next);
    return Object.keys(next).length === 0;
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setFormError(null);
    if (!validate()) return;

    setIsSubmitting(true);
    try {
      const result = await registerStart(email, password, fullName);
      setPendingEmail(result.email);
      startResendCooldown();
      showToast('We sent a verification code to your email.', 'success');
    } catch (err) {
      setFormError(err instanceof ApiError ? err.message : 'Something went wrong. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  }

  function startResendCooldown() {
    setResendCooldown(RESEND_COOLDOWN_SECONDS);
    const interval = setInterval(() => {
      setResendCooldown((prev) => {
        if (prev <= 1) {
          clearInterval(interval);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  }

  async function handleVerifyOtp(e: React.FormEvent) {
    e.preventDefault();
    setOtpError(null);
    if (!pendingEmail) return;
    if (!/^\d{4,8}$/.test(otp.trim())) {
      setOtpError('Enter the code we emailed you.');
      return;
    }
    setVerifying(true);
    try {
      await verifyRegistrationOtp(pendingEmail, otp.trim());
      showToast('Email verified! Welcome to LaptopSathi AI.', 'success');
      navigate('/dashboard');
    } catch (err) {
      setOtpError(err instanceof ApiError ? err.message : 'That code is incorrect or has expired.');
    } finally {
      setVerifying(false);
    }
  }

  async function handleResend() {
    if (!pendingEmail || resendCooldown > 0) return;
    setResending(true);
    try {
      await resendRegistrationOtp(pendingEmail);
      showToast('A new code has been sent to your email.', 'success');
      startResendCooldown();
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : 'Could not resend the code.', 'error');
    } finally {
      setResending(false);
    }
  }

  if (pendingEmail) {
    return (
      <>
        <h2 className="auth-heading">Verify Your Email</h2>
        <p className="auth-subheading">
          Enter the 6-digit code we sent to <strong>{pendingEmail}</strong>
        </p>

        <form onSubmit={handleVerifyOtp} noValidate>
          <div className="field">
            <label htmlFor="reg-otp">Verification code</label>
            <input
              id="reg-otp"
              className="control otp-code-input"
              value={otp}
              onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
              placeholder="••••••"
              inputMode="numeric"
              autoComplete="one-time-code"
              autoFocus
              maxLength={8}
              aria-invalid={!!otpError}
            />
            {otpError && <p className="field-error" role="alert">{otpError}</p>}
          </div>

          <button type="submit" className="btn btn-primary" disabled={verifying}>
            {verifying ? 'Verifying…' : 'Verify and create account'}
          </button>
        </form>

        <div className="otp-links">
          <button
            type="button"
            className="btn-link"
            onClick={handleResend}
            disabled={resendCooldown > 0 || resending}
          >
            {resendCooldown > 0 ? `Resend code (${resendCooldown}s)` : resending ? 'Resending…' : 'Resend code'}
          </button>
          <button type="button" className="btn-link" onClick={() => setPendingEmail(null)}>
            Use a different email
          </button>
        </div>
      </>
    );
  }

  return (
    <>
      <h2 className="auth-heading">Create Account</h2>
      <p className="auth-subheading">Start making smarter laptop decisions with AI</p>

      {formError && (
        <p className="field-error" role="alert" style={{ marginBottom: 14 }}>
          {formError}
        </p>
      )}

      <form onSubmit={handleSubmit} noValidate>
        <div className="field">
          <label htmlFor="reg-name">Full name</label>
          <input
            id="reg-name"
            className="control"
            type="text"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            placeholder="Jordan Rivera"
            autoComplete="name"
          />
          {errors.fullName && <p className="field-error" role="alert">{errors.fullName}</p>}
        </div>

        <div className="field">
          <label htmlFor="reg-email">Email</label>
          <div className="control-icon-wrap">
            <MailIcon width={15} height={15} className="control-icon" aria-hidden="true" />
            <input
              id="reg-email"
              className="control"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="you@example.com"
              autoComplete="email"
            />
          </div>
          <p className="field-hint">We'll send a verification code here — make sure it's real.</p>
          {errors.email && <p className="field-error" role="alert">{errors.email}</p>}
        </div>

        <div className="field">
          <label htmlFor="reg-password">Password</label>
          <PasswordInput
            id="reg-password"
            value={password}
            onChange={setPassword}
            autoComplete="new-password"
            error={errors.password}
          />
          <PasswordStrengthMeter password={password} />
        </div>

        <div className="field">
          <label htmlFor="reg-confirm-password">Confirm password</label>
          <PasswordInput
            id="reg-confirm-password"
            value={confirmPassword}
            onChange={setConfirmPassword}
            autoComplete="new-password"
            error={errors.confirmPassword}
          />
        </div>

        <div className="field" style={{ display: 'flex', alignItems: 'flex-start', gap: 8 }}>
          <input
            id="agree-terms"
            type="checkbox"
            checked={agreeToTerms}
            onChange={(e) => setAgreeToTerms(e.target.checked)}
            style={{ marginTop: 3, accentColor: 'var(--accent)' }}
          />
          <label htmlFor="agree-terms" style={{ margin: 0, cursor: 'pointer' }}>
            I agree to the{' '}
            <Link to="/terms" target="_blank" rel="noopener noreferrer" className="btn-link">Terms of Service</Link>
            {' '}and{' '}
            <Link to="/privacy" target="_blank" rel="noopener noreferrer" className="btn-link">Privacy Policy</Link>
          </label>
        </div>
        {errors.agreeToTerms && <p className="field-error" role="alert">{errors.agreeToTerms}</p>}

        <button type="submit" className="btn btn-primary" disabled={isSubmitting} style={{ marginTop: 6 }}>
          {isSubmitting ? 'Sending code…' : 'Create Account'}
        </button>
      </form>

      <p className="auth-switch-row">
        Already have an account? <Link to="/login" className="btn-link">Sign in</Link>
      </p>
    </>
  );
}
