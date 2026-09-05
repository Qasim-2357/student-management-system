'use client';

import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { MarkForm } from '@/components/marks/MarkForm';
import { ErrorState } from '@/components/states/ErrorState';
import { LoadingState } from '@/components/states/LoadingState';
import { ApiError } from '@/lib/api/client';
import { useMark, useUpdateMark } from '@/lib/hooks/use-marks';

export default function EditMarkPage() {
  const { id } = useParams<{ id: string }>();
  const markId = Number(id);
  const router = useRouter();
  const mark = useMark(markId);
  const mutation = useUpdateMark(markId);

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

  return (
    <div className="mx-auto max-w-3xl">
      <Card>
        <CardHeader>
          <CardTitle>Edit mark</CardTitle>
        </CardHeader>
        <CardContent>
          <MarkForm
            mark={mark.data}
            busy={mutation.isPending}
            error={mutation.error}
            submitLabel="Save changes"
            onSubmit={(values) =>
              mutation.mutate(values, {
                onSuccess: () => router.push(`/marks/${markId}`),
              })
            }
          />
        </CardContent>
      </Card>
    </div>
  );
}
