'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ApiError } from '@/lib/api/client';
import type { Attendance, AttendanceCreate, AttendanceStatus } from '@/lib/types/attendance';

const attendanceSchema = z.object({
  student_id: z.coerce.number().int().positive('Student is required'),
  attendance_date: z.string().min(1, 'Attendance date is required'),
  status: z.enum(['present', 'absent']),
});

export type AttendanceFormValues = z.infer<typeof attendanceSchema>;

function errorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  return 'Something went wrong. Please try again.';
}

export interface AttendanceFormProps {
  attendance?: Attendance;
  busy: boolean;
  error?: unknown;
  onSubmit: (values: AttendanceCreate) => void;
  submitLabel: string;
}

const STATUS_OPTIONS: Array<{ value: AttendanceStatus; label: string }> = [
  { value: 'present', label: 'Present' },
  { value: 'absent', label: 'Absent' },
];

export function AttendanceForm({ attendance, busy, error, onSubmit, submitLabel }: AttendanceFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<z.input<typeof attendanceSchema>, undefined, AttendanceFormValues>({
    resolver: zodResolver(attendanceSchema),
    defaultValues: {
      student_id: attendance?.student_id ?? 0,
      attendance_date: attendance?.attendance_date ?? '',
      status: attendance?.status ?? 'present',
    },
  });

  const submit = handleSubmit((values) => onSubmit({
    student_id: values.student_id,
    attendance_date: values.attendance_date,
    status: values.status,
  }));

  return (
    <form onSubmit={submit} className="space-y-6" noValidate>
      {error ? (
        <Alert variant="destructive" role="alert">
          <AlertDescription>{errorMessage(error)}</AlertDescription>
        </Alert>
      ) : null}

      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-1.5">
          <Label htmlFor="student_id">Student ID</Label>
          <Input id="student_id" type="number" min={1} aria-invalid={Boolean(errors.student_id)} {...register('student_id')} />
          {errors.student_id ? <p className="text-sm text-destructive">{errors.student_id.message}</p> : null}
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="attendance_date">Attendance date</Label>
          <Input id="attendance_date" type="date" aria-invalid={Boolean(errors.attendance_date)} {...register('attendance_date')} />
          {errors.attendance_date ? <p className="text-sm text-destructive">{errors.attendance_date.message}</p> : null}
        </div>

        <div className="space-y-1.5 sm:col-span-2">
          <Label htmlFor="status">Status</Label>
          <select
            id="status"
            className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
            aria-invalid={Boolean(errors.status)}
            {...register('status')}
          >
            {STATUS_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>{option.label}</option>
            ))}
          </select>
          {errors.status ? <p className="text-sm text-destructive">{errors.status.message}</p> : null}
        </div>
      </div>

      <Button type="submit" disabled={busy}>{busy ? 'Saving…' : submitLabel}</Button>
    </form>
  );
}
