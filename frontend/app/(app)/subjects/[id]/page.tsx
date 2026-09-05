'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { buttonVariants } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { RoleGate } from '@/components/role/RoleGate';
import { ErrorState } from '@/components/states/ErrorState';
import { LoadingState } from '@/components/states/LoadingState';
import { ApiError } from '@/lib/api/client';
import { useSubject } from '@/lib/hooks/use-subjects';

export default function SubjectDetailPage() {
  const { id } = useParams<{ id: string }>();
  const subject = useSubject(Number(id));

  if (subject.isLoading) return <LoadingState label="Loading subject" rows={4} />;
  if (subject.isError || !subject.data) {
    return (
      <ErrorState
        title="Subject unavailable"
        message={subject.error instanceof ApiError ? subject.error.message : 'The subject could not be loaded.'}
        onRetry={() => subject.refetch()}
      />
    );
  }

  const value = subject.data;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Subject</p>
          <h1 className="mt-1 text-3xl font-semibold">{value.name}</h1>
        </div>
        <div className="flex gap-2">
          <Link className={buttonVariants({ variant: 'outline' })} href="/subjects">
            Back
          </Link>
          <RoleGate roles={['admin']}>
            <Link className={buttonVariants()} href={`/subjects/${value.id}/edit`}>
              Edit
            </Link>
          </RoleGate>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Subject details</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid gap-4 sm:grid-cols-2">
            <div>
              <dt className="text-sm text-muted-foreground">Name</dt>
              <dd className="mt-1 font-medium">{value.name}</dd>
            </div>
            <div>
              <dt className="text-sm text-muted-foreground">Code</dt>
              <dd className="mt-1 font-medium">{value.code}</dd>
            </div>
          </dl>
        </CardContent>
      </Card>
    </div>
  );
}
