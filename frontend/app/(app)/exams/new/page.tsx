'use client';

import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ExamForm } from '@/components/exams/ExamForm';
import { useCreateExam } from '@/lib/hooks/use-exams';

export default function NewExamPage() {
  const router = useRouter();
  const mutation = useCreateExam();

  return (
    <div className="mx-auto max-w-3xl">
      <Card>
        <CardHeader>
          <CardTitle>Add exam</CardTitle>
        </CardHeader>
        <CardContent>
          <ExamForm
            busy={mutation.isPending}
            error={mutation.error}
            submitLabel="Create exam"
            onSubmit={(values) =>
              mutation.mutate(values, {
                onSuccess: (exam) => router.push(`/exams/${exam.id}`),
              })
            }
          />
        </CardContent>
      </Card>
    </div>
  );
}
