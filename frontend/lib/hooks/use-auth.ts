import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { getCurrentUser, login as loginApi, logout as logoutApi } from "@/lib/api/auth";
import type { AuthUser, LoginRequest } from "@/lib/types/auth";

export const queryKeys = {
  auth: {
    me: ["auth", "me"] as const,
  },
};

export function useAuth() {
  const {
    data: user,
    isLoading,
    error,
    refetch,
  } = useQuery<AuthUser>({
    queryKey: queryKeys.auth.me,
    queryFn: getCurrentUser,
    retry: false,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  return {
    user: user ?? null,
    isLoading,
    isAuthenticated: Boolean(user),
    isUnauthenticated: !isLoading && !user,
    error: error as Error | null,
    refetch,
  };
}

export function useLogin() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation<AuthUser, Error, LoginRequest>({
    mutationFn: (credentials: LoginRequest) => loginApi(credentials),
    onSuccess: (user: AuthUser) => {
      queryClient.setQueryData(queryKeys.auth.me, user);
      router.push("/dashboard");
    },
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  const router = useRouter();

  return useMutation<void, Error, void>({
    mutationFn: logoutApi,
    onSuccess: () => {
      queryClient.setQueryData(queryKeys.auth.me, null);
      queryClient.clear();
      router.push("/login");
    },
  });
}