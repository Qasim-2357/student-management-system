'use client';

import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { SubjectForm } from '@/components/subjects/SubjectForm';
import { useCreateSubject } from '@/lib/hooks/use-subjects';

export default function NewSubjectPage() {
  const router = useRouter();
  const mutation = useCreateSubject();

  return (
    <div className="mx-auto max-w-3xl">
      <Card>
        <CardHeader>
          <CardTitle>Add subject</CardTitle>
        </CardHeader>
        <CardContent>
          <SubjectForm
            busy={mutation.isPending}
            error={mutation.error}
            submitLabel="Create subject"
            onSubmit={(values) =>
              mutation.mutate(values, {
                onSuccess: (subject) => router.push(`/subjects/${subject.id}`),
              })
            }
          />
        </CardContent>
      </Card>
    </div>
  );
}
