'use client';

import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TeacherForm } from '@/components/teachers/TeacherForm';
import { useCreateTeacher } from '@/lib/hooks/use-teachers';

export default function NewTeacherPage() {
  const router = useRouter();
  const mutation = useCreateTeacher();
  return <div className="mx-auto max-w-3xl"><Card><CardHeader><CardTitle>Add teacher</CardTitle></CardHeader><CardContent><TeacherForm busy={mutation.isPending} error={mutation.error} submitLabel="Create teacher" onSubmit={(values) => mutation.mutate(values, { onSuccess: (teacher) => router.push(`/teachers/${teacher.id}`) })} /></CardContent></Card></div>;
}
