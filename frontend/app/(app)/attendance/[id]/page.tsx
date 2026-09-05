'use client';

import Link from 'next/link';
import { useParams } from 'next/navigation';
import { buttonVariants } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { RoleGate } from '@/components/role/RoleGate';
import { ErrorState } from '@/components/states/ErrorState';
import { LoadingState } from '@/components/states/LoadingState';
import { ApiError } from '@/lib/api/client';
import { useAttendanceRecord } from '@/lib/hooks/use-attendance';

export default function AttendanceDetailPage() {
  const { id } = useParams<{ id: string }>();
  const attendance = useAttendanceRecord(Number(id));

  if (attendance.isLoading) return <LoadingState label="Loading attendance" rows={4} />;
  if (attendance.isError || !attendance.data) {
    return (
      <ErrorState
        title="Attendance record unavailable"
        message={attendance.error instanceof ApiError ? attendance.error.message : 'The record could not be loaded.'}
        onRetry={() => attendance.refetch()}
      />
    );
  }

  const value = attendance.data;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Attendance</p>
          <h1 className="mt-1 text-3xl font-semibold">Student {value.student_id}</h1>
        </div>
        <div className="flex gap-2">
          <Link className={buttonVariants({ variant: 'outline' })} href="/attendance">Back</Link>
          <RoleGate roles={['admin']}>
            <Link className={buttonVariants()} href={`/attendance/${value.id}/edit`}>Edit</Link>
          </RoleGate>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Attendance details</CardTitle>
        </CardHeader>
        <CardContent>
          <dl className="grid gap-4 sm:grid-cols-2">
            <div>
              <dt className="text-sm text-muted-foreground">Student ID</dt>
              <dd className="mt-1 font-medium">{value.student_id}</dd>
            </div>
            <div>
              <dt className="text-sm text-muted-foreground">Status</dt>
              <dd className="mt-1 font-medium">{value.status}</dd>
            </div>
            <div className="sm:col-span-2">
              <dt className="text-sm text-muted-foreground">Date</dt>
              <dd className="mt-1 font-medium">{value.attendance_date}</dd>
            </div>
          </dl>
        </CardContent>
      </Card>
    </div>
  );
}
