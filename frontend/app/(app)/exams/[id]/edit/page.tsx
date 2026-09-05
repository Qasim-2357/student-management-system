'use client';

import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ExamForm } from '@/components/exams/ExamForm';
import { ErrorState } from '@/components/states/ErrorState';
import { LoadingState } from '@/components/states/LoadingState';
import { ApiError } from '@/lib/api/client';
import { useExam, useUpdateExam } from '@/lib/hooks/use-exams';

export default function EditExamPage() {
  const { id } = useParams<{ id: string }>();
  const examId = Number(id);
  const router = useRouter();
  const exam = useExam(examId);
  const mutation = useUpdateExam(examId);

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

  return (
    <div className="mx-auto max-w-3xl">
      <Card>
        <CardHeader>
          <CardTitle>Edit exam</CardTitle>
        </CardHeader>
        <CardContent>
          <ExamForm
            exam={exam.data}
            busy={mutation.isPending}
            error={mutation.error}
            submitLabel="Save changes"
            onSubmit={(values) =>
              mutation.mutate(values, {
                onSuccess: () => router.push(`/exams/${examId}`),
              })
            }
          />
        </CardContent>
      </Card>
    </div>
  );
}
