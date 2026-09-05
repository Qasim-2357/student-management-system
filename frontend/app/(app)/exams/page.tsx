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
import { useDeleteExam, useExams } from '@/lib/hooks/use-exams';

const PAGE_SIZE = 20;

export default function ExamsPage() {
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

  const exams = useExams(params);
  const deleteMutation = useDeleteExam();

  const updateUrl = (changes: Record<string, string | undefined>) => {
    const next = new URLSearchParams(searchParams.toString());
    Object.entries(changes).forEach(([key, value]) => {
      if (value) next.set(key, value);
      else next.delete(key);
    });
    router.push(`${pathname}${next.toString() ? `?${next}` : ''}`);
  };

  const handleDelete = (id: number, name: string) => {
    if (window.confirm(`Delete ${name}? This action cannot be undone.`)) {
      deleteMutation.mutate(id);
    }
  };

  const error = exams.error instanceof ApiError ? exams.error.message : 'Unable to load exams.';

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Assessment calendar</p>
          <h1 className="mt-1 text-3xl font-semibold tracking-tight">Exams</h1>
          <p className="mt-1 text-muted-foreground">Manage scheduled assessments and class-level exam records.</p>
        </div>
        <RoleGate roles={['admin']}>
          <Link className={buttonVariants()} href="/exams/new">Add exam</Link>
        </RoleGate>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Exam schedule</CardTitle>
          <div className="pt-2">
            <Input
              aria-label="Search exams"
              placeholder="Search by name or type"
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
          {exams.isLoading ? <LoadingState rows={5} label="Loading exams" /> : null}
          {exams.isError ? <ErrorState message={error} onRetry={() => exams.refetch()} /> : null}
          {deleteMutation.isError ? (
            <ErrorState
              title="Exam could not be deleted"
              message={deleteMutation.error instanceof ApiError ? deleteMutation.error.message : 'Please try again.'}
            />
          ) : null}

          {exams.isSuccess && exams.data.items.length === 0 ? (
            <EmptyState
              title={params.search ? 'No matching exams' : 'No exams yet'}
              description={params.search ? 'Try another search term.' : 'Scheduled exams will appear here once created.'}
              action={
                params.search ? (
                  <Button variant="outline" size="sm" onClick={() => updateUrl({ search: undefined, page: undefined })}>Clear search</Button>
                ) : (
                  <RoleGate roles={['admin']}>
                    <Link className={buttonVariants({ size: 'sm' })} href="/exams/new">Add exam</Link>
                  </RoleGate>
                )
              }
            />
          ) : null}

          {exams.isSuccess && exams.data.items.length > 0 ? (
            <>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[720px] text-left text-sm">
                  <caption className="sr-only">Exams</caption>
                  <thead className="border-b text-muted-foreground">
                    <tr>
                      <th className="px-3 py-3">Name</th>
                      <th className="px-3 py-3">Type</th>
                      <th className="px-3 py-3">Date</th>
                      <th className="px-3 py-3">Class</th>
                      <th className="px-3 py-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {exams.data.items.map((exam) => (
                      <tr key={exam.id}>
                        <td className="px-3 py-3 font-medium">{exam.name}</td>
                        <td className="px-3 py-3">{exam.exam_type}</td>
                        <td className="px-3 py-3">{exam.exam_date}</td>
                        <td className="px-3 py-3">{exam.academic_class_id}</td>
                        <td className="px-3 py-3">
                          <div className="flex justify-end gap-2">
                            <Link className={buttonVariants({ variant: 'outline', size: 'sm' })} href={`/exams/${exam.id}`}>View</Link>
                            <RoleGate roles={['admin']}>
                              <Link className={buttonVariants({ variant: 'outline', size: 'sm' })} href={`/exams/${exam.id}/edit`}>Edit</Link>
                              <Button variant="destructive" size="sm" onClick={() => handleDelete(exam.id, exam.name)} disabled={deleteMutation.isPending}>Delete</Button>
                            </RoleGate>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="mt-4 flex items-center justify-between gap-3 text-sm text-muted-foreground">
                <span>{exams.data.total} exam{exams.data.total === 1 ? '' : 's'}</span>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" disabled={params.page <= 1} onClick={() => updateUrl({ page: String(params.page - 1) })}>Previous</Button>
                  <span className="px-2 py-2">Page {exams.data.page} of {Math.max(1, exams.data.total_pages)}</span>
                  <Button variant="outline" size="sm" disabled={exams.data.page >= exams.data.total_pages} onClick={() => updateUrl({ page: String(params.page + 1) })}>Next</Button>
                </div>
              </div>
            </>
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
}
