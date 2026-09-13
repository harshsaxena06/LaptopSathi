import React, { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { AppShell } from '@/components/AppShell';
import { LaptopCard } from '@/components/console/LaptopCard';
import { EmptyState, ErrorState } from '@/components/console/StateBlocks';
import { WalletIcon } from '@/components/Icons';
import { domainApi } from '@/api/domainApi';
import { ApiError } from '@/types/auth';
import { BudgetOptimizeResponse } from '@/types/domain';

export function BudgetOptimizerPage() {
  const [searchParams] = useSearchParams();
  const [laptopId, setLaptopId] = useState(searchParams.get('laptop_id') || '');
  const [flexibility, setFlexibility] = useState(10000);
  const [result, setResult] = useState<BudgetOptimizeResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runOptimize() {
    const id = parseInt(laptopId, 10);
    if (!id) {
      setError('Enter a laptop ID.');
      setResult(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await domainApi.budgetOptimize(id, flexibility);
      setResult(res);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not optimize right now.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (searchParams.get('laptop_id')) runOptimize();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <AppShell>
      <div className="page-head">
        <div>
          <h1>Budget Optimizer</h1>
          <p>See nearby upgrade and downgrade trade-offs for a specific laptop.</p>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 20 }}>
        <div className="grid cols-2">
          <div className="field">
            <label htmlFor="budget-laptop-id">Laptop ID</label>
            <input id="budget-laptop-id" className="control" type="number" value={laptopId} onChange={(e) => setLaptopId(e.target.value)} placeholder="e.g. 12" />
          </div>
          <div className="field">
            <label htmlFor="budget-flex">Flexibility (± ₹)</label>
            <input id="budget-flex" className="control" type="number" value={flexibility} onChange={(e) => setFlexibility(Number(e.target.value) || 10000)} />
          </div>
        </div>
        <button type="button" className="btn btn-primary" style={{ width: 'auto' }} onClick={runOptimize} disabled={loading}>
          {loading ? 'Optimizing…' : 'Optimize'}
        </button>
      </div>

      {loading && <div className="skel-card" style={{ height: 180 }} />}
      {!loading && error && <ErrorState message={error} onRetry={runOptimize} />}
      {!loading && !error && !result && (
        <EmptyState icon={<WalletIcon width={20} height={20} />} title="Enter a laptop ID" message='Use the ID shown on any laptop card (e.g. "#12").' />
      )}
      {!loading && !error && result && (
        <>
          <div className="card" style={{ marginBottom: 16 }}>
            Base laptop: <strong>{result.base_laptop.brand} {result.base_laptop.model_name}</strong> — ₹{Math.round(result.base_laptop.price_inr).toLocaleString('en-IN')}
          </div>

          <h3 style={{ margin: '20px 0 12px' }}>⬆ Upgrades</h3>
          {result.upgrades.length ? result.upgrades.map((u) => (
            <LaptopCard key={u.laptop.id} laptop={u.laptop} extra={<div className="explain"><em>{u.tradeoff_summary}</em></div>} />
          )) : <EmptyState title="None found in range" message="Try widening the flexibility amount." />}

          <h3 style={{ margin: '20px 0 12px' }}>⬇ Downgrades</h3>
          {result.downgrades.length ? result.downgrades.map((d) => (
            <LaptopCard key={d.laptop.id} laptop={d.laptop} extra={<div className="explain"><em>{d.tradeoff_summary}</em></div>} />
          )) : <EmptyState title="None found in range" message="Try widening the flexibility amount." />}
        </>
      )}
    </AppShell>
  );
}
