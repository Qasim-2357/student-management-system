'use client';

import { FormEvent, useState } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';

const VALID_CREDENTIALS = {
  email: 'admin@example.com',
  password: 'password123',
};

export default function LoginPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (email !== VALID_CREDENTIALS.email || password !== VALID_CREDENTIALS.password) {
      setError('Invalid email or password.');
      return;
    }

    const nextUrl = searchParams.get('redirect') || '/dashboard';
    localStorage.setItem(
      'session',
      JSON.stringify({ user: { email, role: 'admin' } }),
    );
    router.push(nextUrl);
  };

  return (
    <main className="min-h-screen bg-slate-100 p-6">
      <div className="mx-auto max-w-md rounded-lg border border-slate-200 bg-white p-8 shadow-sm">
        <h1 className="mb-6 text-2xl font-semibold text-slate-900">Sign in</h1>
        {searchParams.get('redirect') ? (
          <p className="mb-4 text-sm text-slate-600">Please sign in to continue.</p>
        ) : null}
        {error ? (
          <div className="mb-4 rounded border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </div>
        ) : null}
        <form className="space-y-4" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="email" className="mb-1 block text-sm font-medium text-slate-700">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              className="w-full rounded border border-slate-300 px-3 py-2 outline-none ring-0 focus:border-slate-500"
              autoComplete="email"
              required
            />
          </div>
          <div>
            <label htmlFor="password" className="mb-1 block text-sm font-medium text-slate-700">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              className="w-full rounded border border-slate-300 px-3 py-2 outline-none ring-0 focus:border-slate-500"
              autoComplete="current-password"
              required
            />
          </div>
          <button
            type="submit"
            className="w-full rounded bg-slate-900 px-4 py-2 font-medium text-white transition hover:bg-slate-700"
          >
            Sign in
          </button>
        </form>
      </div>
    </main>
  );
}
