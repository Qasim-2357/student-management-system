'use client';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import type { Assignment, AssignmentCreate } from '@/lib/types/assignments';
import type { AcademicClass } from '@/lib/types/classes';
import type { Subject } from '@/lib/types/subjects';
const schema = z.object({ title: z.string().trim().min(1), description: z.string().optional(), subject_id: z.coerce.number().int().positive(), academic_class_id: z.coerce.number().int().positive(), due_date: z.string().min(1) });
type AssignmentFormInput = z.input<typeof schema>;
type AssignmentFormOutput = z.output<typeof schema>;
export function AssignmentForm({ initialData, subjects, classes, busy, error, onSubmit }: { initialData?: Assignment; subjects: Subject[]; classes: AcademicClass[]; busy: boolean; error?: unknown; onSubmit: (data: AssignmentCreate) => void }) {
  const { register, handleSubmit, formState: { errors } } = useForm<AssignmentFormInput, unknown, AssignmentFormOutput>({ resolver: zodResolver(schema), defaultValues: { title: initialData?.title ?? '', description: initialData?.description ?? '', subject_id: initialData?.subject_id, academic_class_id: initialData?.academic_class_id, due_date: initialData?.due_date ?? '' } });
  return <form onSubmit={handleSubmit((data) => onSubmit({ ...data, description: data.description || null }))} className="space-y-4">{error ? <p className="text-sm text-destructive">{error instanceof Error ? error.message : 'Unable to save assignment.'}</p> : null}
    <Input placeholder="Assignment title" {...register('title')} />{errors.title && <p className="text-sm text-destructive">{errors.title.message}</p>}
    <textarea className="min-h-24 w-full rounded-md border bg-background px-3 py-2 text-sm" placeholder="Description (optional)" {...register('description')} />
    <div className="grid gap-4 sm:grid-cols-2"><select className="h-10 rounded-md border bg-background px-3 text-sm" {...register('subject_id')}><option value="">Select subject</option>{subjects.map((s) => <option key={s.id} value={s.id}>{s.name} ({s.code})</option>)}</select><select className="h-10 rounded-md border bg-background px-3 text-sm" {...register('academic_class_id')}><option value="">Select class</option>{classes.map((c) => <option key={c.id} value={c.id}>{c.name} ({c.code})</option>)}</select></div>
    <Input type="date" {...register('due_date')} />{errors.due_date && <p className="text-sm text-destructive">{errors.due_date.message}</p>}
    <Button type="submit" disabled={busy}>
      {busy ? 'Saving...' : 'Save assignment'}
    </Button>
  </form>;
}
