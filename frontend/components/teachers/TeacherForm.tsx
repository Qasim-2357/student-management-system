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
  name: z.string().trim().min(1, 'Name is required').max(100),
  email: z.string().trim().email('Enter a valid email address'),
  phone: z.string().trim().min(1, 'Phone is required').max(20),
  password: z.string().max(128).optional(),
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
    setError,
    formState: { errors },
  } = useForm<TeacherFormValues>({
    resolver: zodResolver(teacherSchema),
    defaultValues: {
      name: teacher?.name ?? '',
      email: teacher?.email ?? '',
      phone: teacher?.phone ?? '',
      password: '',
    },
  });

  const submit = handleSubmit((values) => {
    if (!teacher && !values.password) {
      setError('password', { message: 'Password is required for a teacher login' });
      return;
    }
    const { password, ...profile } = values;
    onSubmit(password ? { ...profile, password } : profile);
  });

  return (
    <form onSubmit={submit} className="space-y-6" noValidate>
      {error ? (
        <Alert variant="destructive" role="alert">
          <AlertDescription>{errorMessage(error)}</AlertDescription>
        </Alert>
      ) : null}
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-1.5">
          <Label>Teacher ID</Label>
          <Input value={teacher?.teacher_code ?? 'Generated after creation'} readOnly />
        </div>
        <FormField label="Name" name="name" error={errors.name?.message} register={register} />
        <FormField label="Email" name="email" type="email" error={errors.email?.message} register={register} />
        <FormField label="Phone" name="phone" error={errors.phone?.message} register={register} />
        {!teacher ? <FormField label="Password" name="password" type="password" error={errors.password?.message} register={register} /> : null}
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
