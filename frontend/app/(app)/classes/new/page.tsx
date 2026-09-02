'use client';

import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ClassForm } from '@/components/classes/ClassForm';
import { useCreateClass } from '@/lib/hooks/use-classes';

export default function NewClassPage() {
  const router = useRouter();
  const mutation = useCreateClass();
  return <div className="mx-auto max-w-3xl"><Card><CardHeader><CardTitle>Add class</CardTitle></CardHeader><CardContent><ClassForm busy={mutation.isPending} error={mutation.error} submitLabel="Create class" onSubmit={(values) => mutation.mutate(values, { onSuccess: (academicClass) => router.push(`/classes/${academicClass.id}`) })} /></CardContent></Card></div>;
}
