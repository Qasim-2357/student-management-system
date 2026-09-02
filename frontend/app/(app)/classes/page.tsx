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
import { useClasses, useDeleteClass } from '@/lib/hooks/use-classes';

const PAGE_SIZE = 20;

export default function ClassesPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const params = useMemo(() => ({
    search: searchParams.get('search') || undefined,
    page: Math.max(1, Number(searchParams.get('page')) || 1),
    page_size: PAGE_SIZE,
  }), [searchParams]);
  const classes = useClasses(params);
  const deleteMutation = useDeleteClass();
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
        <div><p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Directory</p><h1 className="mt-1 text-3xl font-semibold tracking-tight">Classes</h1><p className="mt-1 text-muted-foreground">Search and manage academic classes.</p></div>
        <RoleGate roles={['admin']}><Link className={buttonVariants()} href="/classes/new">Add class</Link></RoleGate>
      </div>
      <Card>
        <CardHeader><CardTitle className="text-lg">Academic classes</CardTitle><div className="pt-2"><Input aria-label="Search classes" placeholder="Search name, code, or course" defaultValue={params.search ?? ''} onChange={(event) => updateUrl({ search: event.target.value.trim() || undefined, page: undefined })} /></div></CardHeader>
        <CardContent>
          {classes.isLoading ? <LoadingState rows={5} label="Loading classes" /> : null}
          {classes.isError ? <ErrorState message={classes.error instanceof ApiError ? classes.error.message : 'Unable to load classes.'} onRetry={() => classes.refetch()} /> : null}
          {classes.isSuccess && classes.data.items.length === 0 ? <EmptyState title="No classes found" description="Try adjusting your search." /> : null}
          {classes.isSuccess && classes.data.items.length > 0 ? <><div className="overflow-x-auto"><table className="w-full min-w-[680px] text-left text-sm"><caption className="sr-only">Academic classes</caption><thead className="border-b text-muted-foreground"><tr><th scope="col" className="px-3 py-3">Name</th><th scope="col" className="px-3 py-3">Code</th><th scope="col" className="px-3 py-3">Course</th><th scope="col" className="px-3 py-3">Semester</th><th scope="col" className="px-3 py-3 text-right">Actions</th></tr></thead><tbody className="divide-y">{classes.data.items.map((academicClass) => <tr key={academicClass.id}><td className="px-3 py-3 font-medium">{academicClass.name}</td><td className="px-3 py-3">{academicClass.code}</td><td className="px-3 py-3">{academicClass.course}</td><td className="px-3 py-3">{academicClass.semester}</td><td className="px-3 py-3"><div className="flex justify-end gap-2"><Link className={buttonVariants({ variant: 'outline', size: 'sm' })} href={`/classes/${academicClass.id}`}>View</Link><RoleGate roles={['admin']}><Link className={buttonVariants({ variant: 'outline', size: 'sm' })} href={`/classes/${academicClass.id}/edit`}>Edit</Link><Button variant="destructive" size="sm" disabled={deleteMutation.isPending} onClick={() => handleDelete(academicClass.id, academicClass.name)}>Delete</Button></RoleGate></div></td></tr>)}</tbody></table></div><div className="mt-4 flex items-center justify-between gap-3 text-sm text-muted-foreground"><span>{classes.data.total} class{classes.data.total === 1 ? '' : 'es'}</span><div className="flex items-center gap-2"><Button variant="outline" size="sm" disabled={params.page <= 1} onClick={() => updateUrl({ page: String(params.page - 1) })}>Previous</Button><span>Page {classes.data.page} of {Math.max(1, classes.data.total_pages)}</span><Button variant="outline" size="sm" disabled={classes.data.page >= classes.data.total_pages} onClick={() => updateUrl({ page: String(params.page + 1) })}>Next</Button></div></div></> : null}
        </CardContent>
      </Card>
    </div>
  );
}
