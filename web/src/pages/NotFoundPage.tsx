import React from 'react';
import { Link } from 'react-router-dom';

export function NotFoundPage() {
  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 12 }}>
      <h1 style={{ fontSize: 48 }}>404</h1>
      <p style={{ color: 'var(--text-2)' }}>This page doesn&apos;t exist.</p>
      <Link to="/dashboard" className="btn-link">Go back home</Link>
    </div>
  );
}
