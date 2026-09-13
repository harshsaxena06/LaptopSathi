import React from 'react';

const SCORE_LABELS: Record<string, string> = {
  programming_score: 'PROG', ai_ml_score: 'AI/ML', gaming_score: 'GAME',
  video_editing_score: 'VIDEO', battery_score: 'BATT', portability_score: 'PORT',
  business_score: 'BIZ', student_score: 'STUD', future_proof_score: 'FUTURE',
};

function Dial({ label, value }: { label: string; value: number }) {
  const v = Math.max(0, Math.min(100, value || 0));
  const r = 20;
  const c = 2 * Math.PI * r;
  const offset = c * (1 - v / 100);
  return (
    <div className="dial" title={`${label}: ${v.toFixed(0)}`}>
      <svg width="52" height="52" viewBox="0 0 52 52" aria-hidden="true">
        <circle cx="26" cy="26" r={r} style={{ stroke: 'var(--border)' }} strokeWidth="5" fill="none" />
        <circle
          cx="26" cy="26" r={r} style={{ stroke: 'var(--accent)' }} strokeWidth="5" fill="none"
          strokeDasharray={c} strokeDashoffset={offset} strokeLinecap="round"
          transform="rotate(-90 26 26)"
        />
        <text x="26" y="30" textAnchor="middle" fontFamily="IBM Plex Mono" fontSize="11" style={{ fill: 'var(--text)' }}>
          {v.toFixed(0)}
        </text>
      </svg>
      <div className="lab">{label}</div>
    </div>
  );
}

export function ScoreDials({ scores }: { scores: Record<string, number> }) {
  return (
    <div className="dials">
      {Object.entries(SCORE_LABELS).map(([key, label]) => (
        <Dial key={key} label={label} value={scores?.[key]} />
      ))}
    </div>
  );
}
