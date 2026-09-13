import React from 'react';
import { calculatePasswordStrength } from '@/lib/passwordStrength';

const SEGMENT_COLORS = ['var(--red)', 'var(--red)', 'var(--amber)', 'var(--accent)', 'var(--green)'];

export function PasswordStrengthMeter({ password }: { password: string }) {
  if (!password) return null;
  const { score, label } = calculatePasswordStrength(password);

  return (
    <div className="strength-meter" aria-live="polite">
      <div className="strength-track">
        {[0, 1, 2, 3].map((i) => (
          <div
            key={i}
            className="strength-seg"
            style={{ background: i < score ? SEGMENT_COLORS[score] : undefined }}
          />
        ))}
      </div>
      <div className="strength-label" style={{ color: score >= 3 ? 'var(--green)' : undefined }}>
        {label}
      </div>
    </div>
  );
}
