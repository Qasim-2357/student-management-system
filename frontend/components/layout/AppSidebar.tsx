'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Users,
  GraduationCap,
  Layers,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuth } from '@/lib/hooks/use-auth';
import type { UserRole } from '@/lib/types/auth';

interface NavItem {
  label: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  roles: UserRole[];
}

const NAV_ITEMS: NavItem[] = [
  { label: 'Dashboard', href: '/dashboard', icon: LayoutDashboard, roles: ['admin', 'teacher', 'student'] },
  { label: 'Students', href: '/students', icon: Users, roles: ['admin', 'teacher'] },
  { label: 'Teachers', href: '/teachers', icon: GraduationCap, roles: ['admin'] },
  { label: 'Classes', href: '/classes', icon: Layers, roles: ['admin', 'teacher'] },
];

export interface AppSidebarProps {
  className?: string;
  onNavigate?: () => void;
}

export function AppSidebar({ className, onNavigate }: AppSidebarProps) {
  const pathname = usePathname();
  const { user } = useAuth();
  const items = NAV_ITEMS.filter((item) => !user || item.roles.includes(user.role));

  return (
    <nav aria-label="Primary" className={cn('flex h-full flex-col gap-1 overflow-y-auto p-4', className)}>
      <div className="mb-4 px-2">
        <span className="text-lg font-semibold tracking-tight">SMS</span>
      </div>
      <ul className="flex flex-col gap-1">
        {items.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
          const Icon = item.icon;
          return (
            <li key={item.href}>
              <Link
                href={item.href}
                onClick={onNavigate}
                aria-current={isActive ? 'page' : undefined}
                className={cn(
                  'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                  'hover:bg-muted',
                  isActive ? 'bg-muted text-foreground' : 'text-muted-foreground',
                )}
              >
                <Icon className="size-4 shrink-0" aria-hidden="true" />
                {item.label}
              </Link>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}
