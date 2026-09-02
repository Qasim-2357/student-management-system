'use client';

import { Suspense, useEffect } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ApiError } from '@/lib/api/client';
import { useAuth, useLoginMutation } from '@/lib/hooks/use-auth';

const loginSchema = z.object({
  email: z.string().min(1, 'Email is required').email('Enter a valid email address'),
  password: z.string().min(1, 'Password is required'),
});

type LoginFormValues = z.infer<typeof loginSchema>;

function LoginForm() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const redirectTo = searchParams.get('redirect') || '/dashboard';
  const { isAuthenticated } = useAuth();
  const loginMutation = useLoginMutation();

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
    defaultValues: { email: '', password: '' },
  });

  // Already have a valid session (e.g. back-navigated here) - skip the form.
  useEffect(() => {
    if (isAuthenticated) {
      router.replace(redirectTo);
    }

  }, [isAuthenticated, redirectTo, router]);

  const onSubmit = handleSubmit(async (values) => {
    try {
      await loginMutation.mutateAsync(values);
      router.push(redirectTo);
    } catch {
      // Surfaced below via loginMutation.error - nothing else to do here.
    }
  });

  const errorMessage =
    loginMutation.error instanceof ApiError
      ? loginMutation.error.kind === 'unauthorized'
        ? 'Invalid email or password.'
        : loginMutation.error.message
      : loginMutation.error
        ? 'Something went wrong. Please try again.'
        : null;

  const busy = isSubmitting || loginMutation.isPending;

  return (
    <main className="flex min-h-dvh items-center justify-center bg-muted/40 p-4 sm:p-6">
      <div className="w-full max-w-sm rounded-lg border border-border bg-card p-6 shadow-sm sm:max-w-md sm:p-8">
        <h1 className="mb-1 text-2xl font-semibold text-foreground">Sign in</h1>
        <p className="mb-6 text-sm text-muted-foreground">Student Management System</p>

        {searchParams.get('redirect') ? (
          <p className="mb-4 text-sm text-muted-foreground">Please sign in to continue.</p>
        ) : null}

        {errorMessage ? (
          <Alert role="alert" aria-live="assertive" variant="destructive" className="mb-4">
            <AlertDescription>{errorMessage}</AlertDescription>
          </Alert>
        ) : null}

        <form className="space-y-4" onSubmit={onSubmit} noValidate>
          <div className="space-y-1.5">
            <Label htmlFor="email">Email</Label>
            <Input
              id="email"
              type="email"
              autoComplete="email"
              disabled={busy}
              aria-invalid={Boolean(errors.email)}
              aria-describedby={errors.email ? 'email-error' : undefined}
              {...register('email')}
            />
            {errors.email ? (
              <p id="email-error" className="text-sm text-destructive">
                {errors.email.message}
              </p>
            ) : null}
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              type="password"
              autoComplete="current-password"
              disabled={busy}
              aria-invalid={Boolean(errors.password)}
              aria-describedby={errors.password ? 'password-error' : undefined}
              {...register('password')}
            />
            {errors.password ? (
              <p id="password-error" className="text-sm text-destructive">
                {errors.password.message}
              </p>
            ) : null}
          </div>

          <Button type="submit" className="w-full" disabled={busy}>
            {busy ? 'Signing in…' : 'Sign in'}
          </Button>
        </form>
      </div>
    </main>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <main className="flex min-h-dvh items-center justify-center bg-muted/40 p-4">
          <p className="text-sm text-muted-foreground">Loading sign-in…</p>
        </main>
      }
    >
      <LoginForm />
    </Suspense>
  );
}
