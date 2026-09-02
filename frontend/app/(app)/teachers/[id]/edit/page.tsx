'use client';

import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TeacherForm } from '@/components/teachers/TeacherForm';
import { LoadingState } from '@/components/states/LoadingState';
import { ErrorState } from '@/components/states/ErrorState';
import { ApiError } from '@/lib/api/client';
import { useTeacher, useUpdateTeacher } from '@/lib/hooks/use-teachers';

export default function EditTeacherPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const teacherId = Number(id);
  const teacher = useTeacher(teacherId);
  const mutation = useUpdateTeacher(teacherId);
  if (teacher.isLoading) return <LoadingState label="Loading teacher" rows={4} />;
  if (teacher.isError || !teacher.data) return <ErrorState title="Teacher unavailable" message={teacher.error instanceof ApiError ? teacher.error.message : 'The teacher could not be loaded.'} onRetry={() => teacher.refetch()} />;
  return <div className="mx-auto max-w-3xl"><Card><CardHeader><CardTitle>Edit teacher</CardTitle></CardHeader><CardContent><TeacherForm teacher={teacher.data} busy={mutation.isPending} error={mutation.error} submitLabel="Save changes" onSubmit={(values) => mutation.mutate(values, { onSuccess: () => router.push(`/teachers/${teacherId}`) })} /></CardContent></Card></div>;
}
