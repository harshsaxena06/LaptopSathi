import React from 'react';
import { AlertIcon, InboxIcon } from '../Icons';

export function SkeletonCards({ count = 3 }: { count?: number }) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div className="skel-card" key={i}>
          <div className="skel skel-line" style={{ width: '45%', height: 16 }} />
          <div className="skel skel-line" style={{ width: '70%' }} />
          <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
            {Array.from({ length: 5 }).map((__, j) => (
              <div className="skel" key={j} style={{ width: 54, height: 54, borderRadius: '50%' }} />
            ))}
          </div>
        </div>
      ))}
    </>
  );
}

export function SkeletonStats({ count = 4 }: { count?: number }) {
  return (
    <>
      {Array.from({ length: count }).map((_, i) => (
        <div className="card skel skel-stat" key={i} />
      ))}
    </>
  );
}

export function SkeletonBars() {
  return (
    <div className="card">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="skel skel-line" style={{ width: `${40 + Math.random() * 50}%` }} />
      ))}
    </div>
  );
}

interface EmptyStateProps {
  icon?: React.ReactNode;
  title: string;
  message?: string;
  action?: React.ReactNode;
}

export function EmptyState({ icon, title, message, action }: EmptyStateProps) {
  return (
    <div className="state-block">
      <div className="state-icon">{icon || <InboxIcon width={22} height={22} />}</div>
      <h3>{title}</h3>
      {message && <p>{message}</p>}
      {action}
    </div>
  );
}

export function ErrorState({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div className="state-block error-state" role="alert">
      <div className="state-icon"><AlertIcon width={22} height={22} /></div>
      <h3>Something went wrong</h3>
      <p>{message}</p>
      <button type="button" className="btn btn-ghost" style={{ width: 'auto' }} onClick={onRetry}>
        Try again
      </button>
    </div>
  );
}
