'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  useEffect(() => {
    const rawSession = localStorage.getItem('session');
    router.replace(rawSession ? '/dashboard' : '/login');
  }, [router]);

  return (
    <main className="flex min-h-screen items-center justify-center bg-slate-100 text-slate-700">
      Redirecting...
    </main>
  );
}
