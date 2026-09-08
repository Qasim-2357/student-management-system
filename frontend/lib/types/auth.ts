export type UserRole = "admin" | "teacher" | "student";

export interface AuthUser {
  id: number;
  name: string;
  email: string;
  role: UserRole;
}

export interface LoginRequest {
  identifier: string;
  password: string;
}

export interface LoginResponse {
  message: string;
  user: AuthUser;
}