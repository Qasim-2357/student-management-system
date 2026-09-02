'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { getMe, login as loginRequest, logout as logoutRequest } from '@/lib/api/auth';
import { ApiError } from '@/lib/api/client';
import { queryKeys } from '@/lib/query-keys';
import type { LoginRequest } from '@/lib/types/auth';

/**
 * Session state, backed entirely by the backend's httpOnly cookie via
 * GET /auth/me. There is no client-stored token to read - a 401 here
 * just means "not logged in", which is a normal, expected state, not
 * a query failure to retry.
 */
export function useAuth() {
  const query = useQuery({
    queryKey: queryKeys.auth.me,
    queryFn: getMe,
    retry: false,
    staleTime: 5 * 60 * 1000,
  });

  const isUnauthenticated = query.isError && query.error instanceof ApiError && query.error.status === 401;

  return {
    user: query.data ?? null,
    isLoading: query.isLoading,
    isAuthenticated: Boolean(query.data),
    isUnauthenticated,
    error: query.error,
    refetch: query.refetch,
  };
}

export function useLoginMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (credentials: LoginRequest) => loginRequest(credentials),
    onSuccess: (data) => {
      // Seed the session query directly - avoids an extra round trip to /auth/me.
      queryClient.setQueryData(queryKeys.auth.me, data.user);
    },
  });
}

export function useLogoutMutation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => logoutRequest(),
    onSuccess: () => {
      queryClient.setQueryData(queryKeys.auth.me, null);
      queryClient.clear();
    },
  });
}
