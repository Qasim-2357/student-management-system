'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ApiError } from '@/lib/api/client';
import type { Teacher, TeacherCreate } from '@/lib/types/teachers';

const teacherSchema = z.object({
  user_id: z.string().regex(/^[1-9]\d*$/, 'User ID must be at least 1'),
  name: z.string().trim().min(1, 'Name is required').max(100),
  email: z.string().trim().email('Enter a valid email address'),
  phone: z.string().trim().min(1, 'Phone is required').max(20),
});

type TeacherFormValues = z.infer<typeof teacherSchema>;

function errorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  return 'Something went wrong. Please try again.';
}

export interface TeacherFormProps {
  teacher?: Teacher;
  busy: boolean;
  error?: unknown;
  onSubmit: (values: TeacherCreate) => void;
  submitLabel: string;
}

export function TeacherForm({ teacher, busy, error, onSubmit, submitLabel }: TeacherFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<TeacherFormValues>({
    resolver: zodResolver(teacherSchema),
    defaultValues: {
      user_id: teacher ? String(teacher.user_id) : '',
      name: teacher?.name ?? '',
      email: teacher?.email ?? '',
      phone: teacher?.phone ?? '',
    },
  });

  const submit = handleSubmit((values) => {
    onSubmit({ ...values, user_id: Number(values.user_id) });
  });

  return (
    <form onSubmit={submit} className="space-y-6" noValidate>
      {error ? (
        <Alert variant="destructive" role="alert">
          <AlertDescription>{errorMessage(error)}</AlertDescription>
        </Alert>
      ) : null}
      <div className="grid gap-4 sm:grid-cols-2">
        <FormField label="User ID" name="user_id" type="number" error={errors.user_id?.message} register={register} />
        <FormField label="Name" name="name" error={errors.name?.message} register={register} />
        <FormField label="Email" name="email" type="email" error={errors.email?.message} register={register} />
        <FormField label="Phone" name="phone" error={errors.phone?.message} register={register} />
      </div>
      <Button type="submit" disabled={busy}>{busy ? 'Saving…' : submitLabel}</Button>
    </form>
  );
}

function FormField({ label, name, type = 'text', error, register }: {
  label: string;
  name: keyof TeacherFormValues;
  type?: string;
  error?: string;
  register: ReturnType<typeof useForm<TeacherFormValues>>['register'];
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
