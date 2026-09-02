'use client';

import { Menu, LogOut } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { useQueryClient } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { queryKeys } from '@/lib/query-keys';
import { useAuth, useLogoutMutation } from '@/lib/hooks/use-auth';

export interface AppHeaderProps {
  onMenuClick: () => void;
  isMenuOpen: boolean;
}

export function AppHeader({ onMenuClick, isMenuOpen }: AppHeaderProps) {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const logoutMutation = useLogoutMutation();

  const handleLogout = () => {
    queryClient.setQueryData(queryKeys.auth.me, null);
    router.replace('/login');
    logoutMutation.mutate(undefined, {
      onSettled: () => router.replace('/login'),
    });
  };

  return (
    <header className="flex h-14 items-center justify-between gap-4 border-b border-border bg-background px-4 sm:px-6">
      <div className="flex items-center gap-2">
        <Button
          variant="ghost"
          size="icon"
          className="lg:hidden"
          aria-label="Open navigation menu"
          aria-haspopup="true"
          aria-expanded={isMenuOpen}
          onClick={onMenuClick}
        >
          <Menu className="size-5" aria-hidden="true" />
        </Button>
        <h1 className="text-sm font-semibold sm:text-base">Student Management System</h1>
      </div>

      <div className="flex items-center gap-3">
        {user ? (
          <span className="hidden text-sm text-muted-foreground sm:inline">
            {user.name} <span className="text-xs uppercase">({user.role})</span>
          </span>
        ) : null}
        <Button variant="outline" size="sm" onClick={handleLogout} disabled={logoutMutation.isPending}>
          <LogOut className="size-4" aria-hidden="true" />
          {logoutMutation.isPending ? 'Signing out…' : 'Sign out'}
        </Button>
      </div>
    </header>
  );
}
