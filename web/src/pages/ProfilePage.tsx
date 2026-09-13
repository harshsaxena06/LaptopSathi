import React, { useEffect, useState } from 'react';
import { AppShell } from '@/components/AppShell';
import { useAuth } from '@/context/AuthContext';
import { useToast } from '@/context/ToastContext';
import { api } from '@/api/client';
import { ApiError } from '@/types/auth';
import { AlertIcon, CheckIcon } from '@/components/Icons';

interface Preferences {
  budget_min: number;
  budget_max: number;
  preferred_brands: string[];
  primary_use_case: string;
}

function initials(name: string | null, email: string): string {
  if (name && name.trim()) {
    const parts = name.trim().split(/\s+/);
    return (parts[0][0] + (parts[1]?.[0] ?? '')).toUpperCase();
  }
  return email[0]?.toUpperCase() ?? '?';
}

export function ProfilePage() {
  const { user } = useAuth();
  const { showToast } = useToast();

  const [brands, setBrands] = useState('');
  const [budgetMin, setBudgetMin] = useState('');
  const [budgetMax, setBudgetMax] = useState('');
  const [useCase, setUseCase] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await api.get<Preferences>('/api/users/me/preferences');
        if (cancelled) return;
        setBrands((data.preferred_brands || []).join(', '));
        setBudgetMin(String(data.budget_min ?? ''));
        setBudgetMax(String(data.budget_max ?? ''));
        setUseCase(data.primary_use_case || '');
      } catch {
        /* first-time users have no preferences row yet — defaults are fine */
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    try {
      await api.put('/api/users/me/preferences', {
        preferred_brands: brands.split(',').map((b) => b.trim()).filter(Boolean),
        budget_min: budgetMin ? Number(budgetMin) : null,
        budget_max: budgetMax ? Number(budgetMax) : null,
        primary_use_case: useCase || null,
      });
      showToast('Preferences saved.', 'success');
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : 'Could not save preferences.', 'error');
    } finally {
      setSaving(false);
    }
  }

  return (
    <AppShell>
      <div className="page-head">
        <div>
          <h1>Your Profile</h1>
          <p>Manage your account details and personalize what gets recommended to you.</p>
        </div>
      </div>

      <div className="grid cols-2" style={{ alignItems: 'start' }}>
        <div className="card profile-account-card">
          <div className="profile-avatar" aria-hidden="true">
            {initials(user?.full_name ?? null, user?.email ?? '?')}
          </div>
          <h3 style={{ marginBottom: 2 }}>{user?.full_name || 'No name set'}</h3>
          <p style={{ color: 'var(--text-2)', fontSize: 13 }}>{user?.email}</p>

          <div className="hero-meta" style={{ justifyContent: 'center', marginTop: 12 }}>
            <span className="status-chip role">{user?.role === 'admin' ? 'Admin' : 'Member'}</span>
            {user?.is_verified ? (
              <span className="status-chip" style={{ color: 'var(--green)' }}>
                <CheckIcon width={11} height={11} /> Verified
              </span>
            ) : (
              <span className="status-chip warn">
                <AlertIcon width={11} height={11} /> Unverified
              </span>
            )}
          </div>

          <div className="profile-meta-list">
            <div className="profile-meta-row">
              <span>Member since</span>
              <strong>{user ? new Date(`${user.created_at}Z`).toLocaleDateString() : '—'}</strong>
            </div>
            <div className="profile-meta-row">
              <span>Account role</span>
              <strong style={{ textTransform: 'capitalize' }}>{user?.role}</strong>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 style={{ marginBottom: 4 }}>Preferences</h3>
          <p style={{ fontSize: 12.5, color: 'var(--text-2)', marginBottom: 16 }}>
            These sharpen every search and recommendation — no need to repeat yourself each time.
          </p>
          {loading ? (
            <p style={{ color: 'var(--text-2)', fontSize: 13 }}>Loading…</p>
          ) : (
            <form onSubmit={handleSave}>
              <div className="field">
                <label htmlFor="prof-brands">Preferred brands</label>
                <input
                  id="prof-brands" className="control" value={brands}
                  onChange={(e) => setBrands(e.target.value)} placeholder="Dell, Asus, Apple"
                />
              </div>
              <div style={{ display: 'flex', gap: 10 }}>
                <div className="field" style={{ flex: 1 }}>
                  <label htmlFor="prof-min">Budget min (₹)</label>
                  <input id="prof-min" className="control" type="number" min={0} value={budgetMin} onChange={(e) => setBudgetMin(e.target.value)} />
                </div>
                <div className="field" style={{ flex: 1 }}>
                  <label htmlFor="prof-max">Budget max (₹)</label>
                  <input id="prof-max" className="control" type="number" min={0} value={budgetMax} onChange={(e) => setBudgetMax(e.target.value)} />
                </div>
              </div>
              <div className="field">
                <label htmlFor="prof-use-case">Primary use case</label>
                <select id="prof-use-case" className="control" value={useCase} onChange={(e) => setUseCase(e.target.value)}>
                  <option value="">— unset —</option>
                  <option value="programming">Programming</option>
                  <option value="ai_ml">AI &amp; ML</option>
                  <option value="gaming">Gaming</option>
                  <option value="video_editing">Video Editing</option>
                  <option value="business">Business</option>
                  <option value="student">Student</option>
                </select>
              </div>
              <button type="submit" className="btn btn-primary" disabled={saving}>
                {saving ? 'Saving…' : 'Save preferences'}
              </button>
            </form>
          )}
        </div>
      </div>
    </AppShell>
  );
}
