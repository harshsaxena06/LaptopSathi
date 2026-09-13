import React, { useEffect, useState } from 'react';
import { adminApi, LogEntry } from '@/api/adminApi';
import { ApiError } from '@/types/auth';
import { RefreshIcon } from '@/components/Icons';

const LEVEL_COLOR: Record<string, string> = {
  ERROR: 'var(--red)',
  CRITICAL: 'var(--red)',
  WARNING: 'var(--amber)',
  INFO: 'var(--text-2)',
  DEBUG: 'var(--text-3)',
};

export function LogsPanel() {
  const [logs, setLogs] = useState<LogEntry[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const data = await adminApi.getLogs(300);
      setLogs(data.slice().reverse()); // newest first
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not load logs.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    load();
  }, []);

  return (
    <div className="card">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 4 }}>
        <h3>Recent server logs</h3>
        <button type="button" className="btn btn-ghost" style={{ width: 'auto', padding: '7px 12px' }} onClick={load}>
          <RefreshIcon width={13} height={13} /> Refresh
        </button>
      </div>
      <p style={{ fontSize: 12.5, color: 'var(--text-2)', marginBottom: 14 }}>
        The most recent in-memory log lines from this server process (resets on restart) —
        useful for confirming an upload or index rebuild actually succeeded.
      </p>
      {loading && <p style={{ color: 'var(--text-2)', fontSize: 13 }}>Loading…</p>}
      {error && <p className="field-error">{error}</p>}
      {logs && logs.length === 0 && (
        <p style={{ color: 'var(--text-2)', fontSize: 13 }}>No log entries yet.</p>
      )}
      {logs && logs.length > 0 && (
        <div
          style={{
            maxHeight: 480, overflowY: 'auto', background: 'var(--bg)', border: '1px solid var(--border)',
            borderRadius: 'var(--r-sm)', padding: '10px 14px', fontFamily: 'var(--font-mono)', fontSize: 11.5,
          }}
        >
          {logs.map((l, i) => (
            <div key={i} style={{ padding: '3px 0', borderBottom: '1px solid var(--border)', lineHeight: 1.6 }}>
              <span style={{ color: 'var(--text-3)' }}>{new Date(`${l.timestamp}Z`).toLocaleTimeString()}</span>{' '}
              <span style={{ color: LEVEL_COLOR[l.level] ?? 'var(--text-2)', fontWeight: 700 }}>[{l.level}]</span>{' '}
              <span style={{ color: 'var(--text-3)' }}>{l.logger}</span>{' '}
              <span style={{ color: 'var(--text)' }}>{l.message}</span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
