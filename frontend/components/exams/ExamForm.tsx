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
import { useClasses } from '@/lib/hooks/use-classes';
import type { Exam, ExamCreate } from '@/lib/types/exams';

const examSchema = z.object({
  name: z.string().trim().min(1, 'Exam name is required').max(100),
  exam_type: z.string().trim().min(1, 'Exam type is required').max(50),
  exam_date: z.string().min(1, 'Exam date is required'),
  academic_class_id: z.coerce.number().int().positive('Class is required'),
});

export type ExamFormValues = z.infer<typeof examSchema>;

function errorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  return 'Something went wrong. Please try again.';
}

export interface ExamFormProps {
  exam?: Exam;
  busy: boolean;
  error?: unknown;
  onSubmit: (values: ExamCreate) => void;
  submitLabel: string;
}

export function ExamForm({ exam, busy, error, onSubmit, submitLabel }: ExamFormProps) {
  const classes = useClasses({ page: 1, page_size: 100 });
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<z.input<typeof examSchema>, undefined, ExamFormValues>({
    resolver: zodResolver(examSchema),
    defaultValues: {
      name: exam?.name ?? '',
      exam_type: exam?.exam_type ?? '',
      exam_date: exam?.exam_date ?? '',
      academic_class_id: exam?.academic_class_id ?? 0,
    },
  });

  const submit = handleSubmit((values) => onSubmit({
    name: values.name,
    exam_type: values.exam_type,
    exam_date: values.exam_date,
    academic_class_id: values.academic_class_id,
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
          <Label htmlFor="name">Exam name</Label>
          <Input id="name" aria-invalid={Boolean(errors.name)} {...register('name')} />
          {errors.name ? <p className="text-sm text-destructive">{errors.name.message}</p> : null}
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="exam_type">Exam type</Label>
          <Input id="exam_type" aria-invalid={Boolean(errors.exam_type)} {...register('exam_type')} />
          {errors.exam_type ? <p className="text-sm text-destructive">{errors.exam_type.message}</p> : null}
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="exam_date">Exam date</Label>
          <Input id="exam_date" type="date" aria-invalid={Boolean(errors.exam_date)} {...register('exam_date')} />
          {errors.exam_date ? <p className="text-sm text-destructive">{errors.exam_date.message}</p> : null}
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="academic_class_id">Academic class</Label>
          <Select
            id="academic_class_id"
            aria-invalid={Boolean(errors.academic_class_id)}
            disabled={classes.isLoading || classes.isError || classes.data?.items.length === 0}
            {...register('academic_class_id')}
          >
            <option value="">{classes.isLoading ? 'Loading classes…' : classes.isError ? 'Unable to load classes' : classes.data?.items.length ? 'Select a class' : 'No classes available'}</option>
            {classes.data?.items.map((academicClass) => (
              <option key={academicClass.id} value={academicClass.id}>
                {academicClass.name} — Code: {academicClass.code} — {academicClass.course} — Semester {academicClass.semester}
              </option>
            ))}
          </Select>
          {errors.academic_class_id ? <p className="text-sm text-destructive">{errors.academic_class_id.message}</p> : null}
        </div>
      </div>

      <Button type="submit" disabled={busy}>{busy ? 'Saving…' : submitLabel}</Button>
    </form>
  );
}
