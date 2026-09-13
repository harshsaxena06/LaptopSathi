import React, { useEffect, useState } from 'react';
import { AppShell } from '@/components/AppShell';
import { LaptopCard } from '@/components/console/LaptopCard';
import { SkeletonCards, EmptyState, ErrorState } from '@/components/console/StateBlocks';
import { BookmarkIcon } from '@/components/Icons';
import { domainApi } from '@/api/domainApi';
import { ApiError } from '@/types/auth';
import { Laptop } from '@/types/domain';
import { useToast } from '@/context/ToastContext';

export function SavedLaptopsPage() {
  const [laptops, setLaptops] = useState<Laptop[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { showToast } = useToast();

  async function load() {
    setLoading(true);
    setError(null);
    try {
      const prefs = await domainApi.getPreferences();
      const items = await Promise.all(prefs.saved_laptop_ids.map((id) => domainApi.getLaptop(id)));
      setLaptops(items);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not load saved laptops.');
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { load(); }, []);

  async function handleUnsave(id: number) {
    try {
      await domainApi.unsaveLaptop(id);
      setLaptops((prev) => prev?.filter((l) => l.id !== id) ?? null);
      showToast(`Removed laptop #${id} from saved.`, 'success');
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : 'Could not remove.', 'error');
    }
  }

  return (
    <AppShell>
      <div className="page-head">
        <div>
          <h1>Saved Laptops</h1>
          <p>Laptops you&apos;ve bookmarked.</p>
        </div>
        <button type="button" className="btn btn-ghost" style={{ width: 'auto' }} onClick={load}>Refresh</button>
      </div>

      {loading && <SkeletonCards count={2} />}
      {!loading && error && <ErrorState message={error} onRetry={load} />}
      {!loading && !error && laptops && laptops.length === 0 && (
        <EmptyState icon={<BookmarkIcon width={20} height={20} />} title="No saved laptops yet" message='Use the "Save" button on any laptop card to bookmark it here.' />
      )}
      {!loading && !error && laptops && laptops.map((lp) => (
        <LaptopCard key={lp.id} laptop={lp} onSave={handleUnsave} saved />
      ))}
    </AppShell>
  );
}
