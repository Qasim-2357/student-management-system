'use client';

import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ApiError } from '@/lib/api/client';

function shouldRetry(failureCount: number, error: unknown): boolean {
  // Don't retry auth/permission/not-found errors - retrying won't change the outcome.
  if (error instanceof ApiError && (error.kind === 'unauthorized' || error.kind === 'forbidden' || error.kind === 'not_found')) {
    return false;
  }
  return failureCount < 2;
}

export function QueryProvider({ children }: { children: React.ReactNode }) {
  // Created once per browser session, not per render.
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            retry: shouldRetry,
            staleTime: 30 * 1000,
            refetchOnWindowFocus: false,
          },
          mutations: {
            retry: false,
          },
        },
      }),
  );

  return <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>;
}
