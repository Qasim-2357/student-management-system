'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ApiError } from '@/lib/api/client';
import type { Student, StudentCreate } from '@/lib/types/students';

const studentSchema = z.object({
  name: z.string().trim().min(1, 'Name is required').max(100),
  roll_number: z.string().trim().min(1, 'Roll number is required').max(50),
  email: z.string().trim().email('Enter a valid email address'),
  phone: z.string().trim().min(1, 'Phone is required').max(20),
  date_of_birth: z.string(),
  course: z.string().trim().min(1, 'Course is required').max(100),
  semester: z.string().regex(/^[1-9]\d*$/, 'Semester must be at least 1'),
  academic_class_id: z.string().refine((value) => value === '' || /^[1-9]\d*$/.test(value), 'Class ID must be at least 1'),
});

type StudentFormValues = z.infer<typeof studentSchema>;

function errorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  return 'Something went wrong. Please try again.';
}

export interface StudentFormProps {
  student?: Student;
  busy: boolean;
  error?: unknown;
  onSubmit: (values: StudentCreate) => void;
  submitLabel: string;
}

export function StudentForm({ student, busy, error, onSubmit, submitLabel }: StudentFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<StudentFormValues>({
    resolver: zodResolver(studentSchema),
    defaultValues: {
      name: student?.name ?? '',
      roll_number: student?.roll_number ?? '',
      email: student?.email ?? '',
      phone: student?.phone ?? '',
      date_of_birth: student?.date_of_birth ?? '',
      course: student?.course ?? '',
      semester: String(student?.semester ?? 1),
      academic_class_id: student?.academic_class_id ? String(student.academic_class_id) : '',
    },
  });

  const submit = handleSubmit((values) => {
    onSubmit({
      ...values,
      date_of_birth: values.date_of_birth || null,
      semester: Number(values.semester),
      academic_class_id: values.academic_class_id ? Number(values.academic_class_id) : null,
    });
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
        <FormField label="Roll number" name="roll_number" error={errors.roll_number?.message} register={register} />
        <FormField label="Email" name="email" type="email" error={errors.email?.message} register={register} />
        <FormField label="Phone" name="phone" error={errors.phone?.message} register={register} />
        <FormField label="Date of birth" name="date_of_birth" type="date" error={errors.date_of_birth?.message} register={register} />
        <FormField label="Course" name="course" error={errors.course?.message} register={register} />
        <FormField label="Semester" name="semester" type="number" error={errors.semester?.message} register={register} />
        <FormField label="Academic class ID (optional)" name="academic_class_id" type="number" error={errors.academic_class_id?.message} register={register} />
      </div>
      <Button type="submit" disabled={busy}>{busy ? 'Saving…' : submitLabel}</Button>
    </form>
  );
}

function FormField({ label, name, type = 'text', error, register }: {
  label: string;
  name: keyof StudentFormValues;
  type?: string;
  error?: string;
  register: ReturnType<typeof useForm<StudentFormValues>>['register'];
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
