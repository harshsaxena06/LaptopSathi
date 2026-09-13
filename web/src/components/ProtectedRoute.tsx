import React from 'react';
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';

/** Wrap protected routes with this. Redirects to /login (preserving the
 * intended destination) if there's no authenticated session, and shows a
 * lightweight full-page loader while the silent-refresh boot check runs. */
export function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <div style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="sr-only">Loading your session…</div>
        <div
          aria-hidden="true"
          style={{
            width: 32, height: 32, borderRadius: '50%',
            border: '3px solid var(--border)', borderTopColor: 'var(--accent)',
            animation: 'spin 0.8s linear infinite',
          }}
        />
        <style>{'@keyframes spin{to{transform:rotate(360deg)}}'}</style>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <Outlet />;
}
