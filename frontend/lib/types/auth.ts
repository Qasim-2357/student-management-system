/**
 * Mirrors app/schemas/auth.py and app.models.models.User.role on the backend.
 * Kept intentionally minimal for Day 15 - only what /auth/me actually returns.
 */
export type UserRole = 'admin' | 'teacher' | 'student';

export interface AuthUser {
  id: number;
  name: string;
  email: string;
  role: UserRole;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  message: string;
  user: AuthUser;
}
