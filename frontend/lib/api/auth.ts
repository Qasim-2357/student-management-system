import { apiFetch } from "./client";
import type { AuthUser, LoginRequest, LoginResponse } from "@/lib/types/auth";

export async function login(credentials: LoginRequest): Promise<AuthUser> {
  const response = await apiFetch<LoginResponse>("/auth/login", {
    method: "POST",
    body: {
      email: credentials.email,
      password: credentials.password,
    },
  });

  return response.user;
}

export async function logout(): Promise<void> {
  return apiFetch<void>("/auth/logout", {
    method: "POST",
  });
}

export async function getCurrentUser(): Promise<AuthUser> {
  return apiFetch<AuthUser>("/auth/me", {
    method: "GET",
  });
}