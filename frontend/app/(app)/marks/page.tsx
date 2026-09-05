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
import { useDeleteMark, useMarks } from '@/lib/hooks/use-marks';

const PAGE_SIZE = 20;

export default function MarksPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const params = useMemo(
    () => ({
      search: searchParams.get('search') || undefined,
      exam_id: Number(searchParams.get('exam_id')) || undefined,
      student_id: Number(searchParams.get('student_id')) || undefined,
      subject_id: Number(searchParams.get('subject_id')) || undefined,
      page: Math.max(1, Number(searchParams.get('page')) || 1),
      page_size: PAGE_SIZE,
    }),
    [searchParams],
  );

  const marks = useMarks(params);
  const deleteMutation = useDeleteMark();

  const updateUrl = (changes: Record<string, string | undefined>) => {
    const next = new URLSearchParams(searchParams.toString());
    Object.entries(changes).forEach(([key, value]) => {
      if (value) next.set(key, value);
      else next.delete(key);
    });
    router.push(`${pathname}${next.toString() ? `?${next}` : ''}`);
  };

  const handleDelete = (id: number, studentId: number) => {
    if (window.confirm(`Delete mark record for student ${studentId}?`)) {
      deleteMutation.mutate(id);
    }
  };

  const error = marks.error instanceof ApiError ? marks.error.message : 'Unable to load marks.';

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Assessment records</p>
          <h1 className="mt-1 text-3xl font-semibold tracking-tight">Marks</h1>
          <p className="mt-1 text-muted-foreground">Review and manage student performance entries.</p>
        </div>
        <RoleGate roles={['admin']}>
          <Link className={buttonVariants()} href="/marks/new">Add mark</Link>
        </RoleGate>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Markbook</CardTitle>
          <div className="grid gap-3 pt-2 sm:grid-cols-4">
            <Input
              aria-label="Search marks"
              placeholder="Search"
              defaultValue={params.search ?? ''}
              onChange={(event) =>
                updateUrl({
                  search: event.target.value.trim() || undefined,
                  page: undefined,
                })
              }
            />
            <Input
              aria-label="Exam filter"
              placeholder="Exam ID"
              defaultValue={params.exam_id ?? ''}
              onChange={(event) =>
                updateUrl({
                  exam_id: event.target.value.trim() || undefined,
                  page: undefined,
                })
              }
            />
            <Input
              aria-label="Student filter"
              placeholder="Student ID"
              defaultValue={params.student_id ?? ''}
              onChange={(event) =>
                updateUrl({
                  student_id: event.target.value.trim() || undefined,
                  page: undefined,
                })
              }
            />
            <Input
              aria-label="Subject filter"
              placeholder="Subject ID"
              defaultValue={params.subject_id ?? ''}
              onChange={(event) =>
                updateUrl({
                  subject_id: event.target.value.trim() || undefined,
                  page: undefined,
                })
              }
            />
          </div>
        </CardHeader>
        <CardContent>
          {marks.isLoading ? <LoadingState rows={5} label="Loading marks" /> : null}
          {marks.isError ? <ErrorState message={error} onRetry={() => marks.refetch()} /> : null}
          {deleteMutation.isError ? (
            <ErrorState
              title="Mark could not be deleted"
              message={deleteMutation.error instanceof ApiError ? deleteMutation.error.message : 'Please try again.'}
            />
          ) : null}

          {marks.isSuccess && marks.data.items.length === 0 ? (
            <EmptyState
              title="No marks found"
              description="Try changing the filters or add a new marks entry."
              action={
                <RoleGate roles={['admin']}>
                  <Link className={buttonVariants({ size: 'sm' })} href="/marks/new">Add mark</Link>
                </RoleGate>
              }
            />
          ) : null}

          {marks.isSuccess && marks.data.items.length > 0 ? (
            <>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[760px] text-left text-sm">
                  <caption className="sr-only">Marks</caption>
                  <thead className="border-b text-muted-foreground">
                    <tr>
                      <th className="px-3 py-3">Exam</th>
                      <th className="px-3 py-3">Student</th>
                      <th className="px-3 py-3">Subject</th>
                      <th className="px-3 py-3">Marks</th>
                      <th className="px-3 py-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {marks.data.items.map((mark) => (
                      <tr key={mark.id}>
                        <td className="px-3 py-3 font-medium">{mark.exam_id}</td>
                        <td className="px-3 py-3">{mark.student_id}</td>
                        <td className="px-3 py-3">{mark.subject_id}</td>
                        <td className="px-3 py-3">{mark.marks}</td>
                        <td className="px-3 py-3">
                          <div className="flex justify-end gap-2">
                            <Link className={buttonVariants({ variant: 'outline', size: 'sm' })} href={`/marks/${mark.id}`}>View</Link>
                            <RoleGate roles={['admin']}>
                              <Link className={buttonVariants({ variant: 'outline', size: 'sm' })} href={`/marks/${mark.id}/edit`}>Edit</Link>
                              <Button variant="destructive" size="sm" onClick={() => handleDelete(mark.id, mark.student_id)} disabled={deleteMutation.isPending}>Delete</Button>
                            </RoleGate>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="mt-4 flex items-center justify-between gap-3 text-sm text-muted-foreground">
                <span>{marks.data.total} mark{marks.data.total === 1 ? '' : 's'}</span>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" disabled={params.page <= 1} onClick={() => updateUrl({ page: String(params.page - 1) })}>Previous</Button>
                  <span className="px-2 py-2">Page {marks.data.page} of {Math.max(1, marks.data.total_pages)}</span>
                  <Button variant="outline" size="sm" disabled={marks.data.page >= marks.data.total_pages} onClick={() => updateUrl({ page: String(params.page + 1) })}>Next</Button>
                </div>
              </div>
            </>
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
}
