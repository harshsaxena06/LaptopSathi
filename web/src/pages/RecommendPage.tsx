import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppShell } from '@/components/AppShell';
import { LaptopCard } from '@/components/console/LaptopCard';
import { ExplanationBlock } from '@/components/console/ExplanationBlock';
import { SkeletonCards, EmptyState, ErrorState } from '@/components/console/StateBlocks';
import { SparkleIcon } from '@/components/Icons';
import { domainApi } from '@/api/domainApi';
import { ApiError } from '@/types/auth';
import { RecommendationItem } from '@/types/domain';
import { useToast } from '@/context/ToastContext';

export function RecommendPage() {
  const [recQuery, setRecQuery] = useState('');
  const [budgetMin, setBudgetMin] = useState(0);
  const [budgetMax, setBudgetMax] = useState(120000);
  const [useCase, setUseCase] = useState('');
  const [results, setResults] = useState<RecommendationItem[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  const { showToast } = useToast();

  async function runRecommend() {
    setLoading(true);
    setError(null);
    try {
      const res = await domainApi.recommend({
        query: recQuery.trim() || null,
        budget_min: budgetMin,
        budget_max: budgetMax,
        use_case: useCase || null,
        top_k: 5,
      });
      setResults(res.recommendations);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : 'Could not get recommendations right now.');
    } finally {
      setLoading(false);
    }
  }

  async function handleSave(id: number) {
    try {
      await domainApi.saveLaptop(id);
      showToast(`Saved laptop #${id}.`, 'success');
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : 'Could not save.', 'error');
    }
  }

  return (
    <AppShell>
      <div className="page-head">
        <div>
          <h1>AI Recommendations</h1>
          <p>The hybrid engine blends semantic fit, budget, compatibility, benchmarks, brand affinity and future-proofing into one ranked, explained list.</p>
        </div>
      </div>

      <div className="card" style={{ marginBottom: 20 }}>
        <div className="field">
          <label htmlFor="rec-query">Optional description of what you need</label>
          <input
            id="rec-query" className="control" type="text" value={recQuery}
            onChange={(e) => setRecQuery(e.target.value)}
            placeholder="e.g. a laptop for competitive gaming with good battery life"
          />
        </div>
        <div className="grid cols-3">
          <div className="field">
            <label htmlFor="rec-budget-min">Budget min (₹)</label>
            <input id="rec-budget-min" className="control" type="number" value={budgetMin} onChange={(e) => setBudgetMin(Number(e.target.value) || 0)} />
          </div>
          <div className="field">
            <label htmlFor="rec-budget-max">Budget max (₹)</label>
            <input id="rec-budget-max" className="control" type="number" value={budgetMax} onChange={(e) => setBudgetMax(Number(e.target.value) || 300000)} />
          </div>
          <div className="field">
            <label htmlFor="rec-use-case">Primary use case</label>
            <select id="rec-use-case" className="control" value={useCase} onChange={(e) => setUseCase(e.target.value)}>
              <option value="">— any —</option>
              <option value="programming">Programming</option>
              <option value="ai_ml">AI &amp; ML</option>
              <option value="gaming">Gaming</option>
              <option value="video_editing">Video Editing</option>
              <option value="business">Business</option>
              <option value="student">Student</option>
            </select>
          </div>
        </div>
        <button type="button" className="btn btn-primary" style={{ width: 'auto' }} disabled={loading} onClick={runRecommend}>
          {loading ? 'Ranking…' : 'Get recommendations'}
        </button>
      </div>

      {loading && <SkeletonCards count={3} />}
      {!loading && error && <ErrorState message={error} onRetry={runRecommend} />}
      {!loading && !error && results === null && (
        <EmptyState icon={<SparkleIcon width={20} height={20} />} title="Set your criteria above" message="Add a budget range and (optionally) a use case, then get your ranked recommendations." />
      )}
      {!loading && !error && results !== null && results.length === 0 && (
        <EmptyState title="No matches in this budget" message="Try widening your budget range or clearing the use case filter." />
      )}
      {!loading && !error && results && results.map((r) => (
        <LaptopCard
          key={r.laptop.id}
          laptop={r.laptop}
          onSave={handleSave}
          onAddToCompare={(id) => navigate(`/compare?ids=${id}`)}
          onBudgetOptimize={(id) => navigate(`/budget?laptop_id=${id}`)}
          retailerLinks={r.retailer_links}
          extra={<ExplanationBlock explanation={r.explanation} hybridScore={r.hybrid_score} />}
        />
      ))}
    </AppShell>
  );
}
