import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { AppShell } from '@/components/AppShell';
import { useAuth } from '@/context/AuthContext';
import { api } from '@/api/client';
import { ApiError } from '@/types/auth';
import {
  SearchIcon, SparkleIcon, ColumnsIcon, WalletIcon, BookmarkIcon, StarIcon,
} from '@/components/Icons';

interface Preferences {
  budget_min: number;
  budget_max: number;
  preferred_brands: string[];
  primary_use_case: string | null;
  saved_laptop_ids: number[];
}

const ACTIONS = [
  { to: '/search', label: 'AI Search', desc: 'Describe what you need in plain words.', icon: SearchIcon },
  { to: '/recommend', label: 'Recommendations', desc: 'Ranked picks with a plain-English "why".', icon: SparkleIcon },
  { to: '/compare', label: 'Compare', desc: 'Put up to 6 laptops side by side.', icon: ColumnsIcon },
  { to: '/budget', label: 'Budget Optimizer', desc: 'See what a little more (or less) buys.', icon: WalletIcon },
];

function greeting(): string {
  const h = new Date().getHours();
  if (h < 12) return 'Good morning';
  if (h < 17) return 'Good afternoon';
  return 'Good evening';
}

export function DashboardPage() {
  const { user } = useAuth();
  const [prefs, setPrefs] = useState<Preferences | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await api.get<Preferences>('/api/users/me/preferences');
        if (!cancelled) setPrefs(data);
      } catch (err) {
        if (!cancelled) setError(err instanceof ApiError ? err.message : 'Could not load your data.');
      }
    })();
    return () => { cancelled = true; };
  }, []);

  return (
    <AppShell>
      {/* ---- Hero ---- */}
      <div className="hero-panel">
        <div className="hero-greeting">
          <div className="hero-avatar">
            <img src="/logo-mark.png" alt="" />
          </div>
          <div>
            <h1 style={{ fontSize: 'var(--fs-xl)', marginBottom: 4 }}>
              {greeting()}{user?.full_name ? `, ${user.full_name.split(' ')[0]}` : ''} 👋
            </h1>
            <p style={{ color: 'var(--text-2)', fontSize: 13 }}>
              Signed in as <strong style={{ color: 'var(--text)' }}>{user?.email}</strong>
            </p>
          </div>
        </div>
      </div>

      {error && <p className="field-error" style={{ marginBottom: 16 }}>{error}</p>}

      {/* ---- Stats ---- */}
      <div className="grid cols-4" style={{ marginBottom: 22 }}>
        <div className="card stat-card">
          <div className="icon-wrap"><WalletIcon width={16} height={16} /></div>
          <div className="num" style={{ fontSize: 18 }}>
            ₹{((prefs?.budget_min ?? 0) / 1000).toFixed(0)}k–₹{((prefs?.budget_max ?? 300000) / 1000).toFixed(0)}k
          </div>
          <div className="lab">Your budget range</div>
        </div>
        <div className="card stat-card">
          <div className="icon-wrap"><StarIcon width={16} height={16} /></div>
          <div className="num">{prefs?.preferred_brands.length ?? 0}</div>
          <div className="lab">Preferred brands</div>
        </div>
        <div className="card stat-card">
          <div className="icon-wrap"><BookmarkIcon width={16} height={16} /></div>
          <div className="num">{prefs?.saved_laptop_ids.length ?? 0}</div>
          <div className="lab">Saved laptops</div>
        </div>
        <div className="card stat-card">
          <div className="icon-wrap"><SparkleIcon width={16} height={16} /></div>
          <div className="num" style={{ fontSize: 15, textTransform: 'capitalize' }}>
            {prefs?.primary_use_case || 'Not set'}
          </div>
          <div className="lab">Primary use case</div>
        </div>
      </div>

      {/* ---- Quick actions ---- */}
      <h3 style={{ fontSize: 14, color: 'var(--text-2)', margin: '0 0 10px', fontWeight: 600 }}>Jump in</h3>
      <div className="grid cols-4">
        {ACTIONS.map((a) => (
          <Link key={a.to} to={a.to} className="card action-card">
            <div className="icon-wrap"><a.icon width={17} height={17} /></div>
            <h4>{a.label}</h4>
            <p>{a.desc}</p>
          </Link>
        ))}
      </div>
    </AppShell>
  );
}
