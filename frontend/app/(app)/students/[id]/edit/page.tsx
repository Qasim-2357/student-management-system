'use client';

import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { StudentForm } from '@/components/students/StudentForm';
import { LoadingState } from '@/components/states/LoadingState';
import { ErrorState } from '@/components/states/ErrorState';
import { useStudent, useUpdateStudent } from '@/lib/hooks/use-students';
import { ApiError } from '@/lib/api/client';

export default function EditStudentPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const studentId = Number(id);
  const student = useStudent(studentId);
  const mutation = useUpdateStudent(studentId);
  if (student.isLoading) return <LoadingState label="Loading student" rows={6} />;
  if (student.isError || !student.data) return <ErrorState title="Student unavailable" message={student.error instanceof ApiError ? student.error.message : 'The student could not be loaded.'} onRetry={() => student.refetch()} />;
  return <div className="mx-auto max-w-3xl"><Card><CardHeader><CardTitle>Edit student</CardTitle></CardHeader><CardContent><StudentForm student={student.data} busy={mutation.isPending} error={mutation.error} submitLabel="Save changes" onSubmit={(values) => mutation.mutate(values, { onSuccess: () => router.push(`/students/${studentId}`) })} /></CardContent></Card></div>;
}
