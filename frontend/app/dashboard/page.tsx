'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';

type SessionUser = {
  email: string;
  role: string;
};

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<SessionUser | null>(null);

  useEffect(() => {
    const rawSession = localStorage.getItem('session');

    if (!rawSession) {
      router.replace('/login?redirect=/dashboard');
      return;
    }

    try {
      const parsed = JSON.parse(rawSession) as { user?: SessionUser };
      if (!parsed.user) {
        localStorage.removeItem('session');
        router.replace('/login?redirect=/dashboard');
        return;
      }
      setUser(parsed.user);
    } catch {
      localStorage.removeItem('session');
      router.replace('/login?redirect=/dashboard');
    }
  }, [router]);

  const handleLogout = () => {
    localStorage.removeItem('session');
    router.push('/login');
  };

  if (!user) {
    return <main className="p-6 text-slate-700">Checking your session...</main>;
  }

  return (
    <main className="min-h-screen bg-slate-50 p-6">
      <div className="mx-auto max-w-3xl rounded-lg border border-slate-200 bg-white p-8 shadow-sm">
        <div className="mb-6 flex items-center justify-between gap-4">
          <div>
            <p className="text-sm uppercase tracking-[0.2em] text-slate-500">Dashboard</p>
            <h1 className="mt-2 text-3xl font-semibold text-slate-900">Welcome back, {user.email}</h1>
          </div>
          <button
            type="button"
            onClick={handleLogout}
            className="rounded bg-slate-900 px-4 py-2 text-sm font-medium text-white transition hover:bg-slate-700"
          >
            Log out
          </button>
        </div>
        <p className="text-slate-600">You are authenticated as {user.role}.</p>
      </div>
    </main>
  );
}
