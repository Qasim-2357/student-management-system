'use client';

import Link from 'next/link';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { useMemo } from 'react';
import { Button, buttonVariants } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { RoleGate } from '@/components/role/RoleGate';
import { EmptyState } from '@/components/states/EmptyState';
import { ErrorState } from '@/components/states/ErrorState';
import { LoadingState } from '@/components/states/LoadingState';
import { ApiError } from '@/lib/api/client';
import { useDeleteSubject, useSubjects } from '@/lib/hooks/use-subjects';

const PAGE_SIZE = 20;

export default function SubjectsPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const params = useMemo(
    () => ({
      search: searchParams.get('search') || undefined,
      page: Math.max(1, Number(searchParams.get('page')) || 1),
      page_size: PAGE_SIZE,
    }),
    [searchParams],
  );

  const subjects = useSubjects(params);
  const deleteMutation = useDeleteSubject();

  const updateUrl = (changes: Record<string, string | undefined>) => {
    const next = new URLSearchParams(searchParams.toString());
    Object.entries(changes).forEach(([key, value]) => {
      if (value) next.set(key, value);
      else next.delete(key);
    });
    router.push(`${pathname}${next.toString() ? `?${next}` : ''}`);
  };

  const error = subjects.error instanceof ApiError ? subjects.error.message : 'Unable to load subjects.';

  const handleDelete = (id: number, name: string) => {
    if (window.confirm(`Delete ${name}? This action cannot be undone.`)) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Academic catalog</p>
          <h1 className="mt-1 text-3xl font-semibold tracking-tight">Subjects</h1>
          <p className="mt-1 text-muted-foreground">Manage and review the subject catalog.</p>
        </div>
        <RoleGate roles={['admin']}>
          <Link className={buttonVariants()} href="/subjects/new">
            Add subject
          </Link>
        </RoleGate>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Subject directory</CardTitle>
          <div className="pt-2">
            <Input
              aria-label="Search subjects"
              placeholder="Search by name or code"
              defaultValue={params.search ?? ''}
              onChange={(event) =>
                updateUrl({
                  search: event.target.value.trim() || undefined,
                  page: undefined,
                })
              }
            />
          </div>
        </CardHeader>
        <CardContent>
          {subjects.isLoading ? <LoadingState rows={5} label="Loading subjects" /> : null}
          {subjects.isError ? <ErrorState message={error} onRetry={() => subjects.refetch()} /> : null}
          {deleteMutation.isError ? (
            <ErrorState
              title="Subject could not be deleted"
              message={deleteMutation.error instanceof ApiError ? deleteMutation.error.message : 'Please try again.'}
            />
          ) : null}

          {subjects.isSuccess && subjects.data.items.length === 0 ? (
            <EmptyState
              title={params.search ? 'No matching subjects' : 'No subjects yet'}
              description={params.search ? 'Try another search phrase.' : 'Subject records will appear here when they are added.'}
              action={
                params.search ? (
                  <Button variant="outline" size="sm" onClick={() => updateUrl({ search: undefined, page: undefined })}>
                    Clear search
                  </Button>
                ) : (
                  <RoleGate roles={['admin']}>
                    <Link className={buttonVariants({ size: 'sm' })} href="/subjects/new">
                      Add subject
                    </Link>
                  </RoleGate>
                )
              }
            />
          ) : null}

          {subjects.isSuccess && subjects.data.items.length > 0 ? (
            <>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[600px] text-left text-sm">
                  <caption className="sr-only">Subjects</caption>
                  <thead className="border-b text-muted-foreground">
                    <tr>
                      <th scope="col" className="px-3 py-3">Name</th>
                      <th scope="col" className="px-3 py-3">Code</th>
                      <th scope="col" className="px-3 py-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {subjects.data.items.map((subject) => (
                      <tr key={subject.id}>
                        <td className="px-3 py-3 font-medium">{subject.name}</td>
                        <td className="px-3 py-3">{subject.code}</td>
                        <td className="px-3 py-3">
                          <div className="flex justify-end gap-2">
                            <Link className={buttonVariants({ variant: 'outline', size: 'sm' })} href={`/subjects/${subject.id}`}>
                              View
                            </Link>
                            <RoleGate roles={['admin']}>
                              <Link className={buttonVariants({ variant: 'outline', size: 'sm' })} href={`/subjects/${subject.id}/edit`}>
                                Edit
                              </Link>
                              <Button variant="destructive" size="sm" onClick={() => handleDelete(subject.id, subject.name)} disabled={deleteMutation.isPending}>
                                Delete
                              </Button>
                            </RoleGate>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="mt-4 flex items-center justify-between gap-3 text-sm text-muted-foreground">
                <span>{subjects.data.total} subject{subjects.data.total === 1 ? '' : 's'}</span>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" disabled={params.page <= 1} onClick={() => updateUrl({ page: String(params.page - 1) })}>
                    Previous
                  </Button>
                  <span className="px-2 py-2">Page {subjects.data.page} of {Math.max(1, subjects.data.total_pages)}</span>
                  <Button variant="outline" size="sm" disabled={subjects.data.page >= subjects.data.total_pages} onClick={() => updateUrl({ page: String(params.page + 1) })}>
                    Next
                  </Button>
                </div>
              </div>
            </>
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
}
