'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { buttonVariants } from '@/components/ui/button';
import { RoleGate } from '@/components/role/RoleGate';
import { LoadingState } from '@/components/states/LoadingState';
import { ErrorState } from '@/components/states/ErrorState';
import { useStudent } from '@/lib/hooks/use-students';
import { ApiError } from '@/lib/api/client';

export default function StudentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const student = useStudent(Number(id));
  if (student.isLoading) return <LoadingState label="Loading student" rows={6} />;
  if (student.isError || !student.data) return <ErrorState title="Student unavailable" message={student.error instanceof ApiError ? student.error.message : 'The student could not be loaded.'} onRetry={() => student.refetch()} />;
  const value = student.data;
  return <div className="mx-auto max-w-3xl space-y-6"><div className="flex flex-wrap items-center justify-between gap-3"><div><p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Student</p><h1 className="mt-1 text-3xl font-semibold">{value.name}</h1></div><div className="flex gap-2"><Link className={buttonVariants({ variant: 'outline' })} href="/students">Back</Link><RoleGate roles={['admin']}><Link className={buttonVariants()} href={`/students/${value.id}/edit`}>Edit</Link></RoleGate></div></div><Card><CardHeader><CardTitle>Student details</CardTitle></CardHeader><CardContent><dl className="grid gap-4 sm:grid-cols-2">{[['Roll number', value.roll_number], ['Email', value.email], ['Phone', value.phone], ['Course', value.course], ['Semester', value.semester], ['Date of birth', value.date_of_birth || 'Not provided'], ['Academic class ID', value.academic_class_id ?? 'Not assigned']].map(([label, text]) => <div key={label as string}><dt className="text-sm text-muted-foreground">{label}</dt><dd className="mt-1 font-medium">{text}</dd></div>)}</dl></CardContent></Card></div>;
}
