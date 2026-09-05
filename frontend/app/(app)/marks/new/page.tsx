'use client';

import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { MarkForm } from '@/components/marks/MarkForm';
import { useCreateMark } from '@/lib/hooks/use-marks';

export default function NewMarkPage() {
  const router = useRouter();
  const mutation = useCreateMark();

  return (
    <div className="mx-auto max-w-3xl">
      <Card>
        <CardHeader>
          <CardTitle>Add mark entry</CardTitle>
        </CardHeader>
        <CardContent>
          <MarkForm
            busy={mutation.isPending}
            error={mutation.error}
            submitLabel="Create mark"
            onSubmit={(values) =>
              mutation.mutate(values, {
                onSuccess: (mark) => router.push(`/marks/${mark.id}`),
              })
            }
          />
        </CardContent>
      </Card>
    </div>
  );
}
