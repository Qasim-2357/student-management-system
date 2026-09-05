'use client';

import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AttendanceForm } from '@/components/attendance/AttendanceForm';
import { ErrorState } from '@/components/states/ErrorState';
import { LoadingState } from '@/components/states/LoadingState';
import { ApiError } from '@/lib/api/client';
import { useAttendanceRecord, useUpdateAttendance } from '@/lib/hooks/use-attendance';

export default function EditAttendancePage() {
  const { id } = useParams<{ id: string }>();
  const attendanceId = Number(id);
  const router = useRouter();
  const attendance = useAttendanceRecord(attendanceId);
  const mutation = useUpdateAttendance(attendanceId);

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

  return (
    <div className="mx-auto max-w-3xl">
      <Card>
        <CardHeader>
          <CardTitle>Edit attendance</CardTitle>
        </CardHeader>
        <CardContent>
          <AttendanceForm
            attendance={attendance.data}
            busy={mutation.isPending}
            error={mutation.error}
            submitLabel="Save changes"
            onSubmit={(values) =>
              mutation.mutate(values, {
                onSuccess: () => router.push(`/attendance/${attendanceId}`),
              })
            }
          />
        </CardContent>
      </Card>
    </div>
  );
}
