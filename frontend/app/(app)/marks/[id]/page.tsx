'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { buttonVariants } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { RoleGate } from '@/components/role/RoleGate';
import { ErrorState } from '@/components/states/ErrorState';
import { LoadingState } from '@/components/states/LoadingState';
import { ApiError } from '@/lib/api/client';
import { useMark } from '@/lib/hooks/use-marks';

export default function MarkDetailPage() {
  const { id } = useParams<{ id: string }>();
  const mark = useMark(Number(id));

  if (mark.isLoading) return <LoadingState label="Loading mark" rows={4} />;
  if (mark.isError || !mark.data) {
    return (
      <ErrorState
        title="Mark record unavailable"
        message={mark.error instanceof ApiError ? mark.error.message : 'The mark record could not be loaded.'}
        onRetry={() => mark.refetch()}
      />
    );
  }

  const value = mark.data;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Mark record</p>
          <h1 className="mt-1 text-3xl font-semibold">Student {value.student_id}</h1>
        </div>
        <div className="flex gap-2">
          <Link className={buttonVariants({ variant: 'outline' })} href="/marks">Back</Link>
          <RoleGate roles={['admin']}>
            <Link className={buttonVariants()} href={`/marks/${value.id}/edit`}>Edit</Link>
          </RoleGate>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Mark details</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid gap-4 sm:grid-cols-2">
            <div>
              <dt className="text-sm text-muted-foreground">Exam ID</dt>
              <dd className="mt-1 font-medium">{value.exam_id}</dd>
            </div>
            <div>
              <dt className="text-sm text-muted-foreground">Student ID</dt>
              <dd className="mt-1 font-medium">{value.student_id}</dd>
            </div>
            <div>
              <dt className="text-sm text-muted-foreground">Subject ID</dt>
              <dd className="mt-1 font-medium">{value.subject_id}</dd>
            </div>
            <div>
              <dt className="text-sm text-muted-foreground">Marks</dt>
              <dd className="mt-1 font-medium">{value.marks}</dd>
            </div>
          </dl>
        </CardContent>
      </Card>
    </div>
  );
}
