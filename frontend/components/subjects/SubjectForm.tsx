'use client';

import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { ApiError } from '@/lib/api/client';
import type { Subject, SubjectCreate } from '@/lib/types/subjects';

const subjectSchema = z.object({
  name: z.string().trim().min(1, 'Subject name is required').max(100),
  code: z.string().trim().min(1, 'Subject code is required').max(50),
});

export type SubjectFormValues = z.infer<typeof subjectSchema>;

function errorMessage(error: unknown): string {
  if (error instanceof ApiError) return error.message;
  return 'Something went wrong. Please try again.';
}

export interface SubjectFormProps {
  subject?: Subject;
  busy: boolean;
  error?: unknown;
  onSubmit: (values: SubjectCreate) => void;
  submitLabel: string;
}

export function SubjectForm({ subject, busy, error, onSubmit, submitLabel }: SubjectFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SubjectFormValues>({
    resolver: zodResolver(subjectSchema),
    defaultValues: {
      name: subject?.name ?? '',
      code: subject?.code ?? '',
    },
  });

  const submit = handleSubmit((values) => onSubmit({
    name: values.name,
    code: values.code,
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
          <Label htmlFor="name">Subject name</Label>
          <Input
            id="name"
            aria-invalid={Boolean(errors.name)}
            aria-describedby={errors.name ? 'name-error' : undefined}
            {...register('name')}
          />
          {errors.name ? <p id="name-error" className="text-sm text-destructive">{errors.name.message}</p> : null}
        </div>

        <div className="space-y-1.5">
          <Label htmlFor="code">Subject code</Label>
          <Input
            id="code"
            aria-invalid={Boolean(errors.code)}
            aria-describedby={errors.code ? 'code-error' : undefined}
            {...register('code')}
          />
          {errors.code ? <p id="code-error" className="text-sm text-destructive">{errors.code.message}</p> : null}
        </div>
      </div>

      <Button type="submit" disabled={busy}>
        {busy ? 'Saving…' : submitLabel}
      </Button>
    </form>
  );
}
