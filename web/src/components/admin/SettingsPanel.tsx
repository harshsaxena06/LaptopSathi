import React, { useEffect, useState } from 'react';
import { adminApi, SystemSettings } from '@/api/adminApi';
import { ApiError } from '@/types/auth';

const WEIGHT_LABELS: Record<string, string> = {
  semantic: 'Semantic search',
  budget: 'Budget fit',
  compatibility: 'Compatibility',
  benchmark: 'Benchmark performance',
  brand_preference: 'Brand preference',
  future_proof: 'Future-proofing',
};

export function SettingsPanel() {
  const [settings, setSettings] = useState<SystemSettings | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await adminApi.getSettings();
        if (!cancelled) setSettings(data);
      } catch (err) {
        if (!cancelled) setError(err instanceof ApiError ? err.message : 'Could not load settings.');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  if (loading) return <p style={{ color: 'var(--text-2)', fontSize: 13 }}>Loading…</p>;
  if (error) return <p className="field-error">{error}</p>;
  if (!settings) return null;

  const rows: Array<[string, string | number]> = [
    ['Environment', settings.env],
    ['Embedding model', settings.embedding_model],
    ['Access token lifetime', `${settings.access_token_expire_minutes} min`],
    ['Refresh token lifetime', `${settings.refresh_token_expire_days} days`],
    ['Max failed logins', settings.max_failed_login_attempts],
    ['Account lock duration', `${settings.account_lock_minutes} min`],
  ];

  return (
    <div className="grid cols-2" style={{ alignItems: 'start' }}>
      <div className="card">
        <h3 style={{ marginBottom: 4 }}>{settings.app_name}</h3>
        <p style={{ fontSize: 12.5, color: 'var(--text-2)', marginBottom: 16 }}>
          Live configuration, read directly from the running server. Change these via environment
          variables and restart to apply — not editable here to avoid a config drifting out of
          sync with what's actually deployed.
        </p>
        <table className="data-table">
          <tbody>
            {rows.map(([label, value]) => (
              <tr key={label}>
                <th style={{ fontWeight: 500, color: 'var(--text-2)', textTransform: 'none', letterSpacing: 0, fontSize: 13 }}>
                  {label}
                </th>
                <td style={{ fontFamily: 'var(--font-mono)' }}>{value}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="card">
        <h3 style={{ marginBottom: 4 }}>Recommendation weights</h3>
        <p style={{ fontSize: 12.5, color: 'var(--text-2)', marginBottom: 16 }}>
          How much each factor influences a ranked recommendation.
        </p>
        {Object.entries(settings.recommendation_weights).map(([key, value]) => (
          <div className="bar-row" key={key}>
            <span className="name">{WEIGHT_LABELS[key] ?? key}</span>
            <div className="bar-track"><div className="bar-fill" style={{ width: `${Math.round(value * 100)}%` }} /></div>
            <span className="n">{Math.round(value * 100)}%</span>
          </div>
        ))}
      </div>
    </div>
  );
}
