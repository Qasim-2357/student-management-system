'use client';

import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { StudentForm } from '@/components/students/StudentForm';
import { useCreateStudent } from '@/lib/hooks/use-students';

export default function NewStudentPage() {
  const router = useRouter();
  const mutation = useCreateStudent();
  return <div className="mx-auto max-w-3xl"><Card><CardHeader><CardTitle>Add student</CardTitle></CardHeader><CardContent><StudentForm busy={mutation.isPending} error={mutation.error} submitLabel="Create student" onSubmit={(values) => mutation.mutate(values, { onSuccess: (student) => router.push(`/students/${student.id}`) })} /></CardContent></Card></div>;
}
