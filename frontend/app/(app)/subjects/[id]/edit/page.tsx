'use client';

import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { SubjectForm } from '@/components/subjects/SubjectForm';
import { ErrorState } from '@/components/states/ErrorState';
import { LoadingState } from '@/components/states/LoadingState';
import { ApiError } from '@/lib/api/client';
import { useSubject, useUpdateSubject } from '@/lib/hooks/use-subjects';

export default function EditSubjectPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const subjectId = Number(id);
  const subject = useSubject(subjectId);
  const mutation = useUpdateSubject(subjectId);

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

  return (
    <div className="mx-auto max-w-3xl">
      <Card>
        <CardHeader>
          <CardTitle>Edit subject</CardTitle>
        </CardHeader>
        <CardContent>
          <SubjectForm
            subject={subject.data}
            busy={mutation.isPending}
            error={mutation.error}
            submitLabel="Save changes"
            onSubmit={(values) =>
              mutation.mutate(values, {
                onSuccess: () => router.push(`/subjects/${subjectId}`),
              })
            }
          />
        </CardContent>
      </Card>
    </div>
  );
}
