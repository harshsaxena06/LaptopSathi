import React, { useEffect, useState } from 'react';
import { AppShell } from '@/components/AppShell';
import { SkeletonStats, SkeletonBars, ErrorState } from '@/components/console/StateBlocks';
import { GaugeIcon, WalletIcon, ColumnsIcon, ChartIcon } from '@/components/Icons';
import { domainApi } from '@/api/domainApi';
import { ApiError } from '@/types/auth';
import { AnalyticsResponse } from '@/types/domain';

function BarGroup({ title, dist }: { title: string; dist: Record<string, number> }) {
  const entries = Object.entries(dist).sort((a, b) => b[1] - a[1]).slice(0, 10);
  const max = Math.max(...entries.map((e) => e[1]), 1);
  return (
    <div className="card">
      <h3 style={{ marginBottom: 10 }}>{title}</h3>
      {entries.length === 0 && <p style={{ color: 'var(--text-2)', fontSize: 13 }}>No data</p>}
      {entries.map(([k, v]) => (
        <div className="bar-row" key={k}>
          <div className="name" title={k}>{k}</div>
          <div className="bar-track"><div className="bar-fill" style={{ width: `${(v / max) * 100}%` }} /></div>
          <div className="n">{v}</div>
        </div>
      ))}
    </div>
  );
}

export function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function load() {
    setLoading(true);
    setError(null);
    try {
      setData(await domainApi.getAnalytics());
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not load analytics.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  return (
    <AppShell>
      <div className="page-head">
        <div>
          <h1>Analytics Dashboard <span style={{ color: 'var(--text-2)', fontSize: 13, fontWeight: 400 }}>(Admin)</span></h1>
          <p>Dataset-level statistics computed by the backend.</p>
        </div>
        <button type="button" className="btn btn-ghost" style={{ width: 'auto' }} onClick={load}>Refresh</button>
      </div>

      {loading && (
        <>
          <div className="grid cols-4" style={{ marginBottom: 16 }}><SkeletonStats /></div>
          <div className="grid cols-2"><SkeletonBars /><SkeletonBars /></div>
        </>
      )}
      {!loading && error && <ErrorState message={error} onRetry={load} />}
      {!loading && !error && data && (
        <>
          <div className="grid cols-4" style={{ marginBottom: 16 }}>
            <div className="card stat-card"><div className="icon-wrap"><GaugeIcon width={16} height={16} /></div><div className="num">{data.total_laptops}</div><div className="lab">Total laptops</div></div>
            <div className="card stat-card"><div className="icon-wrap"><WalletIcon width={16} height={16} /></div><div className="num">₹{Math.round(data.avg_price).toLocaleString('en-IN')}</div><div className="lab">Average price</div></div>
            <div className="card stat-card"><div className="icon-wrap"><ColumnsIcon width={16} height={16} /></div><div className="num">{Object.keys(data.brand_distribution).length}</div><div className="lab">Brands</div></div>
            <div className="card stat-card"><div className="icon-wrap"><ChartIcon width={16} height={16} /></div><div className="num">{data.kb_version || '—'}</div><div className="lab">KB version</div></div>
          </div>
          <div className="grid cols-2">
            <BarGroup title="Brand distribution" dist={data.brand_distribution} />
            <BarGroup title="Price bucket distribution" dist={data.price_distribution} />
            <BarGroup title="Top CPUs" dist={data.cpu_distribution} />
            <BarGroup title="Top GPUs" dist={data.gpu_distribution} />
          </div>
        </>
      )}
    </AppShell>
  );
}
