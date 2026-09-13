import React from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { Role } from '@/types/auth';

interface RoleGuardProps {
  allowedRoles: Role[];
  redirectTo?: string;
}

/** Use nested inside a <ProtectedRoute> tree to further restrict a subtree
 * by role, e.g. the admin dashboard. This is a UX convenience only — the
 * real enforcement is server-side via app.auth.dependencies.require_role. */
export function RoleGuard({ allowedRoles, redirectTo = '/dashboard' }: RoleGuardProps) {
  const { user } = useAuth();

  if (!user || !allowedRoles.includes(user.role)) {
    return <Navigate to={redirectTo} replace />;
  }

  return <Outlet />;
}
