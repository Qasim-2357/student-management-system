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
import { useAttendance, useDeleteAttendance } from '@/lib/hooks/use-attendance';

const PAGE_SIZE = 20;

export default function AttendancePage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  const params = useMemo(
    () => ({
      student_id: Number(searchParams.get('student_id')) || undefined,
      attendance_date: searchParams.get('attendance_date') || undefined,
      status: (searchParams.get('status') as 'present' | 'absent') || undefined,
      page: Math.max(1, Number(searchParams.get('page')) || 1),
      page_size: PAGE_SIZE,
    }),
    [searchParams],
  );

  const attendance = useAttendance(params);
  const deleteMutation = useDeleteAttendance();

  const updateUrl = (changes: Record<string, string | undefined>) => {
    const next = new URLSearchParams(searchParams.toString());
    Object.entries(changes).forEach(([key, value]) => {
      if (value) next.set(key, value);
      else next.delete(key);
    });
    router.push(`${pathname}${next.toString() ? `?${next}` : ''}`);
  };

  const handleDelete = (id: number, studentId: number) => {
    if (window.confirm(`Delete attendance record for student ${studentId}?`)) {
      deleteMutation.mutate(id);
    }
  };

  const error = attendance.error instanceof ApiError ? attendance.error.message : 'Unable to load attendance.';

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Daily records</p>
          <h1 className="mt-1 text-3xl font-semibold tracking-tight">Attendance</h1>
          <p className="mt-1 text-muted-foreground">Track present and absent records by student.</p>
        </div>
        <RoleGate roles={['admin']}>
          <Link className={buttonVariants()} href="/attendance/new">Add record</Link>
        </RoleGate>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Attendance log</CardTitle>
          <div className="grid gap-3 pt-2 sm:grid-cols-3">
            <Input
              aria-label="Student ID filter"
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
              aria-label="Attendance date filter"
              type="date"
              value={params.attendance_date ?? ''}
              onChange={(event) =>
                updateUrl({
                  attendance_date: event.target.value || undefined,
                  page: undefined,
                })
              }
            />
            <select
              aria-label="Status filter"
              className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
              value={params.status ?? ''}
              onChange={(event) =>
                updateUrl({
                  status: event.target.value || undefined,
                  page: undefined,
                })
              }
            >
              <option value="">All statuses</option>
              <option value="present">Present</option>
              <option value="absent">Absent</option>
            </select>
          </div>
        </CardHeader>
        <CardContent>
          {attendance.isLoading ? <LoadingState rows={5} label="Loading attendance" /> : null}
          {attendance.isError ? <ErrorState message={error} onRetry={() => attendance.refetch()} /> : null}
          {deleteMutation.isError ? (
            <ErrorState
              title="Attendance could not be deleted"
              message={deleteMutation.error instanceof ApiError ? deleteMutation.error.message : 'Please try again.'}
            />
          ) : null}

          {attendance.isSuccess && attendance.data.items.length === 0 ? (
            <EmptyState
              title="No attendance records found"
              description="Try adjusting the filter or add a new attendance entry."
              action={
                <RoleGate roles={['admin']}>
                  <Link className={buttonVariants({ size: 'sm' })} href="/attendance/new">Add record</Link>
                </RoleGate>
              }
            />
          ) : null}

          {attendance.isSuccess && attendance.data.items.length > 0 ? (
            <>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[640px] text-left text-sm">
                  <caption className="sr-only">Attendance</caption>
                  <thead className="border-b text-muted-foreground">
                    <tr>
                      <th className="px-3 py-3">Student</th>
                      <th className="px-3 py-3">Date</th>
                      <th className="px-3 py-3">Status</th>
                      <th className="px-3 py-3 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y">
                    {attendance.data.items.map((record) => (
                      <tr key={record.id}>
                        <td className="px-3 py-3 font-medium">{record.student_id}</td>
                        <td className="px-3 py-3">{record.attendance_date}</td>
                        <td className="px-3 py-3">
                          <span className={`inline-flex rounded-full px-2 py-1 text-xs font-medium ${record.status === 'present' ? 'bg-emerald-100 text-emerald-800' : 'bg-rose-100 text-rose-800'}`}>
                            {record.status}
                          </span>
                        </td>
                        <td className="px-3 py-3">
                          <div className="flex justify-end gap-2">
                            <Link className={buttonVariants({ variant: 'outline', size: 'sm' })} href={`/attendance/${record.id}`}>View</Link>
                            <RoleGate roles={['admin']}>
                              <Link className={buttonVariants({ variant: 'outline', size: 'sm' })} href={`/attendance/${record.id}/edit`}>Edit</Link>
                              <Button variant="destructive" size="sm" onClick={() => handleDelete(record.id, record.student_id)} disabled={deleteMutation.isPending}>Delete</Button>
                            </RoleGate>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              <div className="mt-4 flex items-center justify-between gap-3 text-sm text-muted-foreground">
                <span>{attendance.data.total} record{attendance.data.total === 1 ? '' : 's'}</span>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm" disabled={params.page <= 1} onClick={() => updateUrl({ page: String(params.page - 1) })}>Previous</Button>
                  <span className="px-2 py-2">Page {attendance.data.page} of {Math.max(1, attendance.data.total_pages)}</span>
                  <Button variant="outline" size="sm" disabled={attendance.data.page >= attendance.data.total_pages} onClick={() => updateUrl({ page: String(params.page + 1) })}>Next</Button>
                </div>
              </div>
            </>
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
}
