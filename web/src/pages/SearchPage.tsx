import React, { useCallback, useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppShell } from '@/components/AppShell';
import { LaptopCard } from '@/components/console/LaptopCard';
import { SkeletonCards, EmptyState, ErrorState } from '@/components/console/StateBlocks';
import { SearchIcon, CloseIcon } from '@/components/Icons';
import { domainApi } from '@/api/domainApi';
import { ApiError } from '@/types/auth';
import { SearchResultItem } from '@/types/domain';
import { useToast } from '@/context/ToastContext';

const EXAMPLE_QUERIES = [
  'Lightweight laptop for AI under ₹90,000',
  'Best laptop for Android development',
  'Gaming laptop with excellent battery',
  'Business ultrabook under 1.3kg',
  'Video editing laptop with 4K display',
];

export function SearchPage() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResultItem[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const navigate = useNavigate();
  const { showToast } = useToast();

  const runSearch = useCallback(async (q: string) => {
    const trimmed = q.trim();
    if (!trimmed) {
      setResults(null);
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await domainApi.search(trimmed, 10);
      setResults(res.results);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not search right now.');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    if (query.trim().length >= 3) {
      debounceRef.current = setTimeout(() => runSearch(query), 600);
    }
    return () => { if (debounceRef.current) clearTimeout(debounceRef.current); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [query]);

  async function handleSave(id: number) {
    try {
      await domainApi.saveLaptop(id);
      showToast(`Saved laptop #${id}.`, 'success');
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : 'Could not save.', 'error');
    }
  }

  function handleAddToCompare(id: number) {
    navigate(`/compare?ids=${id}`);
  }
  function handleBudgetOptimize(id: number) {
    navigate(`/budget?laptop_id=${id}`);
  }

  return (
    <AppShell>
      <div className="page-head">
        <div>
          <h1>AI Search</h1>
          <p>Natural-language semantic search over the knowledge base, powered by Sentence Transformers + FAISS.</p>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 20 }}>
        <div style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
          <div className="field search-input-wrap" style={{ marginBottom: 0, flex: 1 }}>
            <span className="search-icon-left" aria-hidden="true"><SearchIcon width={16} height={16} /></span>
            <input
              className="control"
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') runSearch(query); }}
              placeholder='"Best laptop for Android development"'
              aria-label="Search query"
            />
            {query && (
              <button type="button" className="search-clear" aria-label="Clear search" onClick={() => { setQuery(''); setResults(null); }}>
                <CloseIcon width={14} height={14} />
              </button>
            )}
          </div>
          <button type="button" className="btn btn-primary" style={{ width: 'auto' }} onClick={() => runSearch(query)}>
            Search
          </button>
        </div>
        <div className="chip-group">
          {EXAMPLE_QUERIES.map((q) => (
            <button key={q} type="button" className="chip" onClick={() => { setQuery(q); runSearch(q); }}>
              {q}
            </button>
          ))}
        </div>
      </div>

      {loading && <SkeletonCards count={3} />}
      {!loading && error && <ErrorState message={error} onRetry={() => runSearch(query)} />}
      {!loading && !error && results === null && (
        <EmptyState icon={<SearchIcon width={20} height={20} />} title="Search the knowledge base" message="Type a natural-language query above, or try one of the examples." />
      )}
      {!loading && !error && results !== null && results.length === 0 && (
        <EmptyState title="No matches found" message="Try a broader query or a different use case." />
      )}
      {!loading && !error && results && results.length > 0 && results.map((r) => (
        <LaptopCard
          key={r.laptop.id}
          laptop={r.laptop}
          onSave={handleSave}
          onAddToCompare={handleAddToCompare}
          onBudgetOptimize={handleBudgetOptimize}
          extra={
            <div style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent)', fontSize: 12, marginTop: 10 }}>
              Similarity match: {(r.similarity_score * 100).toFixed(1)}%
            </div>
          }
        />
      ))}
    </AppShell>
  );
}
