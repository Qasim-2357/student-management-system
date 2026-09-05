'use client';

import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AttendanceForm } from '@/components/attendance/AttendanceForm';
import { useCreateAttendance } from '@/lib/hooks/use-attendance';

export default function NewAttendancePage() {
  const router = useRouter();
  const mutation = useCreateAttendance();

  return (
    <div className="mx-auto max-w-3xl">
      <Card>
        <CardHeader>
          <CardTitle>Add attendance record</CardTitle>
        </CardHeader>
        <CardContent>
          <AttendanceForm
            busy={mutation.isPending}
            error={mutation.error}
            submitLabel="Create record"
            onSubmit={(values) =>
              mutation.mutate(values, {
                onSuccess: (attendance) => router.push(`/attendance/${attendance.id}`),
              })
            }
          />
        </CardContent>
      </Card>
    </div>
  );
}
