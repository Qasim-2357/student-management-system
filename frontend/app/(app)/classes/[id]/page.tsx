'use client';

import Link from 'next/link';
import { useParams, useRouter } from 'next/navigation';
import { Button, buttonVariants } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { RoleGate } from '@/components/role/RoleGate';
import { LoadingState } from '@/components/states/LoadingState';
import { ErrorState } from '@/components/states/ErrorState';
import { ApiError } from '@/lib/api/client';
import { useAcademicClass, useDeleteClass } from '@/lib/hooks/use-classes';

export default function ClassDetailPage() {
  const { id } = useParams<{ id: string }>();
  const router = useRouter();
  const classId = Number(id);
  const academicClass = useAcademicClass(classId);
  const deleteMutation = useDeleteClass();
  if (academicClass.isLoading) return <LoadingState label="Loading class" rows={4} />;
  if (academicClass.isError || !academicClass.data) return <ErrorState title="Class unavailable" message={academicClass.error instanceof ApiError ? academicClass.error.message : 'The class could not be loaded.'} onRetry={() => academicClass.refetch()} />;
  const value = academicClass.data;
  const handleDelete = () => {
    if (window.confirm(`Delete ${value.name}? This action cannot be undone.`)) deleteMutation.mutate(value.id, { onSuccess: () => router.push('/classes') });
  };
  return <div className="mx-auto max-w-3xl space-y-6"><div className="flex flex-wrap items-center justify-between gap-3"><div><p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Class</p><h1 className="mt-1 text-3xl font-semibold">{value.name}</h1></div><div className="flex flex-wrap gap-2"><Link className={buttonVariants({ variant: 'outline' })} href="/classes">Back</Link><RoleGate roles={['admin']}><Link className={buttonVariants()} href={`/classes/${value.id}/edit`}>Edit</Link><Button variant="destructive" onClick={handleDelete} disabled={deleteMutation.isPending}>Delete</Button></RoleGate></div></div><Card><CardHeader><CardTitle>Class details</CardTitle></CardHeader><CardContent><dl className="grid gap-4 sm:grid-cols-2"><div><dt className="text-sm text-muted-foreground">Code</dt><dd className="mt-1 font-medium">{value.code}</dd></div><div><dt className="text-sm text-muted-foreground">Course</dt><dd className="mt-1 font-medium">{value.course}</dd></div><div><dt className="text-sm text-muted-foreground">Semester</dt><dd className="mt-1 font-medium">{value.semester}</dd></div></dl></CardContent></Card></div>;
}
