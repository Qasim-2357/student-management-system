'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { buttonVariants } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { RoleGate } from '@/components/role/RoleGate';
import { ErrorState } from '@/components/states/ErrorState';
import { LoadingState } from '@/components/states/LoadingState';
import { ApiError } from '@/lib/api/client';
import { useExam } from '@/lib/hooks/use-exams';

export default function ExamDetailPage() {
  const { id } = useParams<{ id: string }>();
  const exam = useExam(Number(id));

  if (exam.isLoading) return <LoadingState label="Loading exam" rows={4} />;
  if (exam.isError || !exam.data) {
    return (
      <ErrorState
        title="Exam unavailable"
        message={exam.error instanceof ApiError ? exam.error.message : 'The exam could not be loaded.'}
        onRetry={() => exam.refetch()}
      />
    );
  }

  const value = exam.data;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Exam</p>
          <h1 className="mt-1 text-3xl font-semibold">{value.name}</h1>
        </div>
        <div className="flex gap-2">
          <Link className={buttonVariants({ variant: 'outline' })} href="/exams">Back</Link>
          <RoleGate roles={['admin']}>
            <Link className={buttonVariants()} href={`/exams/${value.id}/edit`}>Edit</Link>
          </RoleGate>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Exam details</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid gap-4 sm:grid-cols-2">
            <div>
              <dt className="text-sm text-muted-foreground">Name</dt>
              <dd className="mt-1 font-medium">{value.name}</dd>
            </div>
            <div>
              <dt className="text-sm text-muted-foreground">Exam type</dt>
              <dd className="mt-1 font-medium">{value.exam_type}</dd>
            </div>
            <div>
              <dt className="text-sm text-muted-foreground">Date</dt>
              <dd className="mt-1 font-medium">{value.exam_date}</dd>
            </div>
            <div>
              <dt className="text-sm text-muted-foreground">Academic class</dt>
              <dd className="mt-1 font-medium">{value.academic_class_id}</dd>
            </div>
          </dl>
        </CardContent>
      </Card>
    </div>
  );
}
