'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { buttonVariants } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { RoleGate } from '@/components/role/RoleGate';
import { LoadingState } from '@/components/states/LoadingState';
import { ErrorState } from '@/components/states/ErrorState';
import { ApiError } from '@/lib/api/client';
import { useTeacher } from '@/lib/hooks/use-teachers';

export default function TeacherDetailPage() {
  const { id } = useParams<{ id: string }>();
  const teacher = useTeacher(Number(id));
  if (teacher.isLoading) return <LoadingState label="Loading teacher" rows={4} />;
  if (teacher.isError || !teacher.data) return <ErrorState title="Teacher unavailable" message={teacher.error instanceof ApiError ? teacher.error.message : 'The teacher could not be loaded.'} onRetry={() => teacher.refetch()} />;
  const value = teacher.data;
  return <div className="mx-auto max-w-3xl space-y-6"><div className="flex flex-wrap items-center justify-between gap-3"><div><p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Teacher</p><h1 className="mt-1 text-3xl font-semibold">{value.name}</h1></div><div className="flex gap-2"><Link className={buttonVariants({ variant: 'outline' })} href="/teachers">Back</Link><RoleGate roles={['admin']}><Link className={buttonVariants()} href={`/teachers/${value.id}/edit`}>Edit</Link></RoleGate></div></div><Card><CardHeader><CardTitle>Teacher details</CardTitle></CardHeader><CardContent><dl className="grid gap-4 sm:grid-cols-2"><div><dt className="text-sm text-muted-foreground">User ID</dt><dd className="mt-1 font-medium">{value.user_id}</dd></div><div><dt className="text-sm text-muted-foreground">Email</dt><dd className="mt-1 font-medium">{value.email}</dd></div><div><dt className="text-sm text-muted-foreground">Phone</dt><dd className="mt-1 font-medium">{value.phone}</dd></div></dl></CardContent></Card></div>;
}
