/**
 * Small, resource-agnostic fetch wrapper for the FastAPI backend.
 *
 * - Backend base URL comes from NEXT_PUBLIC_API_BASE_URL (never hardcoded).
 * - `credentials: 'include'` on every request, since auth is an httpOnly
 *   `access_token` cookie set by POST /auth/login - there is no token for
 *   the frontend to read or store.
 * - Does NOT know about students/teachers/etc. Resource-specific functions
 *   belong in their own files (e.g. lib/api/students.ts), added on later days.
 */

// Defaults to a same-origin relative path. In dev this is proxied to the
// real backend via the rewrite in next.config.ts, which avoids needing
// CORS support on the backend (it currently has none configured) while the
// browser still only ever talks to its own origin. Override with an
// absolute URL if the backend already has CORS + credentialed cookies set
// up for a different origin.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? '/api';

export type ApiErrorKind = 'unauthorized' | 'forbidden' | 'not_found' | 'validation' | 'network' | 'unknown';

export class ApiError extends Error {
  readonly status: number | null;
  readonly kind: ApiErrorKind;
  readonly detail: unknown;

  constructor(message: string, status: number | null, kind: ApiErrorKind, detail?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.kind = kind;
    this.detail = detail;
  }
}

function kindForStatus(status: number): ApiErrorKind {
  switch (status) {
    case 401:
      return 'unauthorized';
    case 403:
      return 'forbidden';
    case 404:
      return 'not_found';
    case 422:
      return 'validation';
    default:
      return 'unknown';
  }
}

/** Extracts FastAPI's conventional `{"detail": "..."}` or validation error shape, if present. */
function extractMessage(body: unknown, fallback: string): string {
  if (body && typeof body === 'object' && 'detail' in body) {
    const detail = (body as { detail: unknown }).detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail)) {
      const first = detail[0] as { msg?: string } | undefined;
      if (first?.msg) return first.msg;
    }
  }
  return fallback;
}

export interface ApiRequestOptions extends Omit<RequestInit, 'body'> {
  body?: unknown;
}

export async function apiFetch<T>(path: string, options: ApiRequestOptions = {}): Promise<T> {
  const { body, headers, ...rest } = options;

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...rest,
      credentials: 'include',
      headers: {
        ...(body !== undefined ? { 'Content-Type': 'application/json' } : {}),
        ...headers,
      },
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch (cause) {
    throw new ApiError('Unable to reach the server. Check your connection and try again.', null, 'network', cause);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const isJson = response.headers.get('content-type')?.includes('application/json');
  const payload = isJson ? await response.json().catch(() => null) : null;

  if (!response.ok) {
    const kind = kindForStatus(response.status);
    const message = extractMessage(payload, `Request failed with status ${response.status}`);
    throw new ApiError(message, response.status, kind, payload);
  }

  return payload as T;
}
