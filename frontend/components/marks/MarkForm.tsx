'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select } from '@/components/ui/select';
import { ApiError } from '@/lib/api/client';
import { useExams } from '@/lib/hooks/use-exams';
import { useStudents } from '@/lib/hooks/use-students';
import { useSubjects } from '@/lib/hooks/use-subjects';
import type { Mark, MarkCreate } from '@/lib/types/marks';

const markSchema = z.object({
  exam_id: z.coerce.number().int().positive('Exam is required'),
  student_id: z.coerce.number().int().positive('Student is required'),
  subject_id: z.coerce.number().int().positive('Subject is required'),
  marks: z.coerce.number().min(0, 'Marks cannot be negative').max(100, 'Marks cannot exceed 100'),
});

export type MarkFormValues = z.infer<typeof markSchema>;

function errorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  return 'Something went wrong. Please try again.';
}

export interface MarkFormProps {
  mark?: Mark;
  busy: boolean;
  error?: unknown;
  onSubmit: (values: MarkCreate) => void;
  submitLabel: string;
}

export function MarkForm({ mark, busy, error, onSubmit, submitLabel }: MarkFormProps) {
  const exams = useExams({ page: 1, page_size: 100 });
  const students = useStudents({ page: 1, page_size: 100 });
  const subjects = useSubjects({ page: 1, page_size: 100 });
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<z.input<typeof markSchema>, undefined, MarkFormValues>({
    resolver: zodResolver(markSchema),
    defaultValues: {
      exam_id: mark?.exam_id ?? 0,
      student_id: mark?.student_id ?? 0,
      subject_id: mark?.subject_id ?? 0,
      marks: mark?.marks ?? 0,
    },
  });

  const submit = handleSubmit((values) => onSubmit({
    exam_id: values.exam_id,
    student_id: values.student_id,
    subject_id: values.subject_id,
    marks: values.marks,
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
          <Label htmlFor="exam_id">Exam</Label>
          <Select
            id="exam_id"
            aria-invalid={Boolean(errors.exam_id)}
            disabled={exams.isLoading || exams.isError || exams.data?.items.length === 0}
            {...register('exam_id')}
          >
            <option value="">{exams.isLoading ? 'Loading exams…' : exams.isError ? 'Unable to load exams' : exams.data?.items.length ? 'Select an exam' : 'No exams available'}</option>
            {exams.data?.items.map((exam) => (
              <option key={exam.id} value={exam.id}>
                {exam.name} — {new Date(`${exam.exam_date}T00:00:00`).toLocaleDateString(undefined, { day: '2-digit', month: 'short', year: 'numeric' })}
              </option>
            ))}
          </Select>
          {errors.exam_id ? <p className="text-sm text-destructive">{errors.exam_id.message}</p> : null}
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="student_id">Student</Label>
          <Select
            id="student_id"
            aria-invalid={Boolean(errors.student_id)}
            disabled={students.isLoading || students.isError || students.data?.items.length === 0}
            {...register('student_id')}
          >
            <option value="">{students.isLoading ? 'Loading students…' : students.isError ? 'Unable to load students' : students.data?.items.length ? 'Select a student' : 'No students available'}</option>
            {students.data?.items.map((student) => (
              <option key={student.id} value={student.id}>
                {student.name} — {student.roll_number}
              </option>
            ))}
          </Select>
          {errors.student_id ? <p className="text-sm text-destructive">{errors.student_id.message}</p> : null}
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="subject_id">Subject</Label>
          <Select
            id="subject_id"
            aria-invalid={Boolean(errors.subject_id)}
            disabled={subjects.isLoading || subjects.isError || subjects.data?.items.length === 0}
            {...register('subject_id')}
          >
            <option value="">{subjects.isLoading ? 'Loading subjects…' : subjects.isError ? 'Unable to load subjects' : subjects.data?.items.length ? 'Select a subject' : 'No subjects available'}</option>
            {subjects.data?.items.map((subject) => (
              <option key={subject.id} value={subject.id}>
                {subject.name} — {subject.code}
              </option>
            ))}
          </Select>
          {errors.subject_id ? <p className="text-sm text-destructive">{errors.subject_id.message}</p> : null}
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="marks">Marks</Label>
          <Input id="marks" type="number" min={0} max={100} step="0.1" aria-invalid={Boolean(errors.marks)} {...register('marks')} />
          {errors.marks ? <p className="text-sm text-destructive">{errors.marks.message}</p> : null}
        </div>
      </div>

      <Button type="submit" disabled={busy}>{busy ? 'Saving…' : submitLabel}</Button>
    </form>
  );
}
