import React from 'react';
import { Explanation } from '@/types/domain';

export function ExplanationBlock({ explanation, hybridScore }: { explanation: Explanation; hybridScore?: number }) {
  const confPct = Math.round((explanation.confidence_score || 0) * 100);
  return (
    <div className="explain">
      {hybridScore !== undefined && (
        <span className="hybrid-score-tag" style={{ fontFamily: 'var(--font-mono)' }}>
          Hybrid score {(hybridScore * 100).toFixed(1)}
        </span>
      )}
      <div style={{ marginTop: 10 }}>
        <strong>Recommended because</strong>
        <ul>
          {(explanation.reasons.length ? explanation.reasons : ['General fit for your criteria']).map((r, i) => (
            <li key={i}>{r}</li>
          ))}
        </ul>
      </div>
      <div className="explain-cols">
        <div className="pros-block">
          <strong>Pros</strong>
          <ul>{explanation.pros.map((p, i) => <li key={i}>{p}</li>)}</ul>
        </div>
        <div className="cons-block">
          <strong>Cons</strong>
          <ul>{explanation.cons.map((c, i) => <li key={i}>{c}</li>)}</ul>
        </div>
      </div>
      {explanation.budget_tradeoffs.length > 0 && (
        <div>
          <strong>Budget trade-offs</strong>
          <ul>{explanation.budget_tradeoffs.map((t, i) => <li key={i}>{t}</li>)}</ul>
        </div>
      )}
      <div className="confidence-tag">
        <span>Confidence {confPct}%</span>
        <span className="confidence-track">
          <span className="confidence-fill" style={{ width: `${confPct}%`, display: 'block' }} />
        </span>
      </div>
    </div>
  );
}
