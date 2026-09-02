'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

/**
 * Real session state (and the /login redirect for unauthenticated users) is
 * decided by the (app) route group's layout via GET /auth/me - this page
 * just points people at the protected area and lets that layout take over.
 */
export default function Home() {
  const router = useRouter();

  useEffect(() => {
    router.replace('/dashboard');
  }, [router]);

  return (
    <main className="flex min-h-dvh items-center justify-center bg-background p-6 text-muted-foreground">
      Redirecting…
    </main>
  );
}
