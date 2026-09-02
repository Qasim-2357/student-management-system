'use client';

import Link from 'next/link';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { useMemo } from 'react';
import { Button, buttonVariants } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { RoleGate } from '@/components/role/RoleGate';
import { LoadingState } from '@/components/states/LoadingState';
import { ErrorState } from '@/components/states/ErrorState';
import { EmptyState } from '@/components/states/EmptyState';
import { ApiError } from '@/lib/api/client';
import { useDeleteTeacher, useTeachers } from '@/lib/hooks/use-teachers';

const PAGE_SIZE = 20;

export default function TeachersPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const params = useMemo(() => ({
    search: searchParams.get('search') || undefined,
    page: Math.max(1, Number(searchParams.get('page')) || 1),
    page_size: PAGE_SIZE,
  }), [searchParams]);
  const teachers = useTeachers(params);
  const deleteMutation = useDeleteTeacher();
  const updateUrl = (changes: Record<string, string | undefined>) => {
    const next = new URLSearchParams(searchParams.toString());
    Object.entries(changes).forEach(([key, value]) => value ? next.set(key, value) : next.delete(key));
    router.push(`${pathname}${next.toString() ? `?${next}` : ''}`);
  };
  const handleDelete = (id: number, name: string) => {
    if (window.confirm(`Delete ${name}? This action cannot be undone.`)) deleteMutation.mutate(id);
  };
  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div><p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Directory</p><h1 className="mt-1 text-3xl font-semibold tracking-tight">Teachers</h1><p className="mt-1 text-muted-foreground">Search and manage teacher records.</p></div>
        <RoleGate roles={['admin']}><Link className={buttonVariants()} href="/teachers/new">Add teacher</Link></RoleGate>
      </div>
      <Card>
        <CardHeader><CardTitle className="text-lg">Teacher records</CardTitle><div className="pt-2"><Input aria-label="Search teachers" placeholder="Search name, email, or phone" defaultValue={params.search ?? ''} onChange={(event) => updateUrl({ search: event.target.value.trim() || undefined, page: undefined })} /></div></CardHeader>
        <CardContent>
          {teachers.isLoading ? <LoadingState rows={5} label="Loading teachers" /> : null}
          {teachers.isError ? <ErrorState message={teachers.error instanceof ApiError ? teachers.error.message : 'Unable to load teachers.'} onRetry={() => teachers.refetch()} /> : null}
          {deleteMutation.isError ? <ErrorState title="Teacher could not be deleted" message={deleteMutation.error instanceof ApiError ? deleteMutation.error.message : 'Please try again.'} /> : null}
          {teachers.isSuccess && teachers.data.items.length === 0 ? <EmptyState title={params.search ? 'No matching teachers' : 'No teachers yet'} description={params.search ? 'Try adjusting your search.' : 'Teacher records will appear here when they are added.'} action={params.search ? <Button variant="outline" size="sm" onClick={() => updateUrl({ search: undefined, page: undefined })}>Clear search</Button> : <RoleGate roles={['admin']}><Link className={buttonVariants({ size: 'sm' })} href="/teachers/new">Add teacher</Link></RoleGate>} /> : null}
          {teachers.isSuccess && teachers.data.items.length > 0 ? <><div className="overflow-x-auto"><table className="w-full min-w-[680px] text-left text-sm"><caption className="sr-only">Teacher records</caption><thead className="border-b text-muted-foreground"><tr><th scope="col" className="px-3 py-3">Name</th><th scope="col" className="px-3 py-3">Email</th><th scope="col" className="px-3 py-3">Phone</th><th scope="col" className="px-3 py-3">User ID</th><th scope="col" className="px-3 py-3 text-right">Actions</th></tr></thead><tbody className="divide-y">{teachers.data.items.map((teacher) => <tr key={teacher.id}><td className="px-3 py-3 font-medium">{teacher.name}</td><td className="px-3 py-3">{teacher.email}</td><td className="px-3 py-3">{teacher.phone}</td><td className="px-3 py-3">{teacher.user_id}</td><td className="px-3 py-3"><div className="flex justify-end gap-2"><Link className={buttonVariants({ variant: 'outline', size: 'sm' })} href={`/teachers/${teacher.id}`}>View</Link><RoleGate roles={['admin']}><Link className={buttonVariants({ variant: 'outline', size: 'sm' })} href={`/teachers/${teacher.id}/edit`}>Edit</Link><Button variant="destructive" size="sm" disabled={deleteMutation.isPending} onClick={() => handleDelete(teacher.id, teacher.name)}>Delete</Button></RoleGate></div></td></tr>)}</tbody></table></div><div className="mt-4 flex items-center justify-between gap-3 text-sm text-muted-foreground"><span>{teachers.data.total} teacher{teachers.data.total === 1 ? '' : 's'}</span><div className="flex items-center gap-2"><Button variant="outline" size="sm" disabled={params.page <= 1} onClick={() => updateUrl({ page: String(params.page - 1) })}>Previous</Button><span>Page {teachers.data.page} of {Math.max(1, teachers.data.total_pages)}</span><Button variant="outline" size="sm" disabled={teachers.data.page >= teachers.data.total_pages} onClick={() => updateUrl({ page: String(params.page + 1) })}>Next</Button></div></div></> : null}
        </CardContent>
      </Card>
    </div>
  );
}
