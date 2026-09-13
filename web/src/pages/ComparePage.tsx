import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { AppShell } from '@/components/AppShell';
import { EmptyState, ErrorState } from '@/components/console/StateBlocks';
import { ColumnsIcon } from '@/components/Icons';
import { domainApi } from '@/api/domainApi';
import { ApiError } from '@/types/auth';
import { CompareResponse } from '@/types/domain';

export function ComparePage() {
  const [searchParams] = useSearchParams();
  const [idsInput, setIdsInput] = useState(searchParams.get('ids') || '');
  const [result, setResult] = useState<CompareResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runCompare() {
    const ids = idsInput.split(',').map((s) => parseInt(s.trim(), 10)).filter((n) => !isNaN(n));
    if (ids.length < 2) {
      setError('Enter at least 2 laptop IDs.');
      setResult(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await domainApi.compare(ids);
      setResult(res);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not compare right now.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (searchParams.get('ids')) runCompare();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const rows: [string, (l: CompareResponse['laptops'][number]) => string | number][] = [
    ['Price', (l) => `₹${Math.round(l.price_inr).toLocaleString('en-IN')}`],
    ['CPU', (l) => l.cpu_name || '—'],
    ['GPU', (l) => l.gpu_name || '—'],
    ['RAM', (l) => `${l.ram_gb}GB`],
    ['Storage', (l) => `${l.storage_gb}GB ${l.storage_type}`],
    ['Display', (l) => `${l.display_size_inch}" ${l.display_resolution} @${l.refresh_rate_hz}Hz`],
    ['Battery', (l) => `${l.battery_life_hours || '—'}h`],
    ['Weight', (l) => `${l.weight_kg || '—'}kg`],
    ['Gaming score', (l) => (l.scores.gaming_score || 0).toFixed(0)],
    ['AI/ML score', (l) => (l.scores.ai_ml_score || 0).toFixed(0)],
    ['Future-proof', (l) => (l.scores.future_proof_score || 0).toFixed(0)],
  ];

  return (
    <AppShell>
      <div className="page-head">
        <div>
          <h1>Laptop Comparison</h1>
          <p>Compare laptops by ID across specs, benchmarks and feature-store scores.</p>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 20 }}>
        <label htmlFor="compare-ids">Laptop IDs to compare (comma-separated)</label>
        <div style={{ display: 'flex', gap: 10 }}>
          <input id="compare-ids" className="control" value={idsInput} onChange={(e) => setIdsInput(e.target.value)} placeholder="e.g. 1, 2, 3" />
          <button type="button" className="btn btn-primary" style={{ width: 'auto' }} onClick={runCompare} disabled={loading}>
            {loading ? 'Comparing…' : 'Compare'}
          </button>
        </div>
      </div>

      {loading && <div className="card skel" style={{ height: 220 }} />}
      {!loading && error && <ErrorState message={error} onRetry={runCompare} />}
      {!loading && !error && !result && (
        <EmptyState icon={<ColumnsIcon width={20} height={20} />} title="Add at least 2 laptops" message='Enter two or more laptop IDs above, e.g. from a "#12" shown on any card.' />
      )}
      {!loading && !error && result && (
        <>
          <div className="card table-scroll" style={{ marginBottom: 16 }}>
            <table className="data-table">
              <thead>
                <tr>
                  <th></th>
                  {result.laptops.map((l) => <th key={l.id}>{l.brand} {l.model_name}</th>)}
                </tr>
              </thead>
              <tbody>
                {rows.map(([label, fn]) => (
                  <tr key={label}>
                    <th>{label}</th>
                    {result.laptops.map((l) => <td key={l.id}>{fn(l)}</td>)}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="card" style={{ marginBottom: 16 }}>
            <h3 style={{ marginBottom: 12 }}>Category winners</h3>
            {Object.entries(result.winner_by_category).map(([cat, name]) => (
              <div className="bar-row" key={cat}>
                <div className="name">{cat}</div>
                <div style={{ color: 'var(--accent)', fontWeight: 600 }}>{name}</div>
              </div>
            ))}
          </div>
          <div className="card"><strong>Overall:</strong> {result.overall_recommendation}</div>
        </>
      )}
    </AppShell>
  );
}
