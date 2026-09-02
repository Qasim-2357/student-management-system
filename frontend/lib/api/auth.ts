import { apiFetch } from '@/lib/api/client';
import type { AuthUser, LoginRequest, LoginResponse } from '@/lib/types/auth';

/** POST /auth/login - sets the httpOnly access_token cookie; never returns a token. */
export function login(credentials: LoginRequest): Promise<LoginResponse> {
  return apiFetch<LoginResponse>('/auth/login', {
    method: 'POST',
    body: credentials,
  });
}

/** POST /auth/logout - clears the httpOnly access_token cookie server-side. */
export function logout(): Promise<{ message: string }> {
  return apiFetch<{ message: string }>('/auth/logout', { method: 'POST' });
}

/**
 * GET /auth/me - the source of truth for "is there a valid session right now".
 * Rejects with ApiError(status 401) when there is no valid cookie.
 */
export function getMe(): Promise<AuthUser> {
  return apiFetch<AuthUser>('/auth/me', { method: 'GET' });
}
