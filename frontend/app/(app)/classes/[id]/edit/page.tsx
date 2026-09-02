'use client';

import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ClassForm } from '@/components/classes/ClassForm';
import { LoadingState } from '@/components/states/LoadingState';
import { ErrorState } from '@/components/states/ErrorState';
import { ApiError } from '@/lib/api/client';
import { useAcademicClass, useUpdateClass } from '@/lib/hooks/use-classes';

export default function EditClassPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const classId = Number(id);
  const academicClass = useAcademicClass(classId);
  const mutation = useUpdateClass(classId);
  if (academicClass.isLoading) return <LoadingState label="Loading class" rows={4} />;
  if (academicClass.isError || !academicClass.data) return <ErrorState title="Class unavailable" message={academicClass.error instanceof ApiError ? academicClass.error.message : 'The class could not be loaded.'} onRetry={() => academicClass.refetch()} />;
  return <div className="mx-auto max-w-3xl"><Card><CardHeader><CardTitle>Edit class</CardTitle></CardHeader><CardContent><ClassForm academicClass={academicClass.data} busy={mutation.isPending} error={mutation.error} submitLabel="Save changes" onSubmit={(values) => mutation.mutate(values, { onSuccess: () => router.push(`/classes/${classId}`) })} /></CardContent></Card></div>;
}
