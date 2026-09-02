'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ApiError } from '@/lib/api/client';
import type { AcademicClass, ClassCreate } from '@/lib/types/classes';

const classSchema = z.object({
  name: z.string().trim().min(1, 'Name is required').max(100),
  code: z.string().trim().min(1, 'Code is required').max(50),
  course: z.string().trim().min(1, 'Course is required').max(100),
  semester: z.string().regex(/^[1-9]\d*$/, 'Semester must be at least 1'),
});

type ClassFormValues = z.infer<typeof classSchema>;

function errorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  return 'Something went wrong. Please try again.';
}

export interface ClassFormProps {
  academicClass?: AcademicClass;
  busy: boolean;
  error?: unknown;
  onSubmit: (values: ClassCreate) => void;
  submitLabel: string;
}

export function ClassForm({ academicClass, busy, error, onSubmit, submitLabel }: ClassFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ClassFormValues>({
    resolver: zodResolver(classSchema),
    defaultValues: {
      name: academicClass?.name ?? '',
      code: academicClass?.code ?? '',
      course: academicClass?.course ?? '',
      semester: String(academicClass?.semester ?? 1),
    },
  });

  const submit = handleSubmit((values) => {
    onSubmit({ ...values, semester: Number(values.semester) });
  });

  return (
    <form onSubmit={submit} className="space-y-6" noValidate>
      {error ? (
        <Alert variant="destructive" role="alert">
          <AlertDescription>{errorMessage(error)}</AlertDescription>
        </Alert>
      ) : null}
      <div className="grid gap-4 sm:grid-cols-2">
        <FormField label="Name" name="name" error={errors.name?.message} register={register} />
        <FormField label="Code" name="code" error={errors.code?.message} register={register} />
        <FormField label="Course" name="course" error={errors.course?.message} register={register} />
        <FormField label="Semester" name="semester" type="number" error={errors.semester?.message} register={register} />
      </div>
      <Button type="submit" disabled={busy}>{busy ? 'Saving…' : submitLabel}</Button>
    </form>
  );
}

function FormField({ label, name, type = 'text', error, register }: {
  label: string;
  name: keyof ClassFormValues;
  type?: string;
  error?: string;
  register: ReturnType<typeof useForm<ClassFormValues>>['register'];
}) {
  const errorId = `${name}-error`;
  return (
    <div className="space-y-1.5">
      <Label htmlFor={name}>{label}</Label>
      <Input id={name} type={type} aria-invalid={Boolean(error)} aria-describedby={error ? errorId : undefined} {...register(name)} />
      {error ? <p id={errorId} className="text-sm text-destructive">{error}</p> : null}
    </div>
  );
}
