'use client';

import type { ReactNode } from 'react';
import { useAuth } from '@/lib/hooks/use-auth';
import type { UserRole } from '@/lib/types/auth';

export interface RoleGateProps {
  roles: UserRole[];
  children: ReactNode;
  /** Rendered instead when the current user's role is not allowed. Omit to render nothing. */
  fallback?: ReactNode;
}

/**
 * Conditionally renders children based on the current user's role.
 *
 * IMPORTANT: this is a UI convenience only, to avoid showing actions a
 * role can't use. It is NOT an authorization boundary - the backend
 * independently enforces every role check server-side (see
 * app/security.py's require_role and app/services/student_authorization.py).
 * Hiding a button here never substitutes for that.
 */
export function RoleGate({ roles, children, fallback = null }: RoleGateProps) {
  const { user } = useAuth();

  if (!user || !roles.includes(user.role)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
