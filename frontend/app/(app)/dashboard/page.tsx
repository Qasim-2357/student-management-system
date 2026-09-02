'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useAuth } from '@/lib/hooks/use-auth';

/**
 * Placeholder landing page for the authenticated shell. The real
 * role-specific dashboards (admin/teacher/student KPIs, charts, etc.) are
 * built on a later day against /dashboard/admin, /dashboard/teacher, and
 * /dashboard/student - this page intentionally does not call those yet.
 */
export default function DashboardPage() {
  const { user } = useAuth();

  return (
    <Card className="mx-auto max-w-xl">
      <CardHeader>
        <CardTitle>Welcome{user ? `, ${user.name}` : ''}</CardTitle>
        <CardDescription>You&apos;re signed in as {user?.role}.</CardDescription>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-muted-foreground">
          The role-specific dashboard content for this account will be built on a later day.
        </p>
      </CardContent>
    </Card>
  );
}
