'use client';

import { useEffect } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { AppShell } from '@/components/layout/AppShell';
import { LoadingState } from '@/components/states/LoadingState';
import { useAuth } from '@/lib/hooks/use-auth';

/**
 * Gate for every route under (app). Auth state comes from GET /auth/me
 * (an httpOnly cookie the browser sends automatically) - there is no
 * client-side token to check, so this is a real session check, not a
 * localStorage flag.
 */
export default function ProtectedLayout({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const { user, isLoading, isUnauthenticated } = useAuth();

  useEffect(() => {
    if (isUnauthenticated) {
      const query = window.location.search;
      const destination = query ? `${pathname}${query}` : pathname;
      router.replace(`/login?redirect=${encodeURIComponent(destination)}`);
    }
  }, [isUnauthenticated, pathname, router]);

  if (isLoading) {
    return (
      <div className="flex h-dvh items-center justify-center p-6">
        <LoadingState label="Checking your session" rows={2} className="max-w-sm" />
      </div>
    );
  }

  if (!user) {
    // Redirecting - render nothing rather than a flash of protected content.
    return null;
  }

  return <AppShell>{children}</AppShell>;
}
