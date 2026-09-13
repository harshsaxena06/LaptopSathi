import React, { useState } from 'react';
import { EyeIcon, EyeOffIcon, LockIcon } from '../Icons';

interface PasswordInputProps {
  id: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  autoComplete?: string;
  error?: string;
}

export function PasswordInput({ id, value, onChange, placeholder, autoComplete, error }: PasswordInputProps) {
  const [visible, setVisible] = useState(false);

  return (
    <div>
      <div className="password-input-wrap">
        <LockIcon width={15} height={15} className="control-icon" aria-hidden="true" />
        <input
          id={id}
          className="control"
          type={visible ? 'text' : 'password'}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder || 'Enter your password'}
          autoComplete={autoComplete || 'current-password'}
          aria-invalid={!!error}
          aria-describedby={error ? `${id}-error` : undefined}
        />
        <button
          type="button"
          className="password-toggle-btn"
          onClick={() => setVisible((v) => !v)}
          aria-label={visible ? 'Hide password' : 'Show password'}
          tabIndex={-1}
        >
          {visible ? <EyeOffIcon width={16} height={16} /> : <EyeIcon width={16} height={16} />}
        </button>
      </div>
      {error && (
        <p className="field-error" id={`${id}-error`} role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
