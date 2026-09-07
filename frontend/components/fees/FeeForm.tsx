'use client';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import type { Student } from '@/lib/types/students';
import type { Fee, FeeCreate } from '@/lib/types/fees';
const schema = z.object({ student_id: z.coerce.number().int().positive(), amount: z.coerce.number().min(0), paid_amount: z.coerce.number().min(0), due_date: z.string().min(1) }).refine((v) => v.paid_amount <= v.amount, { message: 'Paid amount cannot exceed total amount', path: ['paid_amount'] });
type FeeFormInput = z.input<typeof schema>;
type FeeFormOutput = z.output<typeof schema>;
export function FeeForm({ initialData, students, busy, error, onSubmit }: { initialData?: Fee; students: Student[]; busy: boolean; error?: unknown; onSubmit: (data: FeeCreate) => void }) {
  const { register, handleSubmit, formState: { errors } } = useForm<FeeFormInput, unknown, FeeFormOutput>({ resolver: zodResolver(schema), defaultValues: { student_id: initialData?.student_id, amount: initialData?.amount ?? 0, paid_amount: initialData?.paid_amount ?? 0, due_date: initialData?.due_date ?? '' } });
  return <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">{error ? <p className="text-sm text-destructive">{error instanceof Error ? error.message : 'Unable to save fee record.'}</p> : null}<select className="h-10 w-full rounded-md border bg-background px-3 text-sm" {...register('student_id')}><option value="">Select student</option>{students.map((s) => <option key={s.id} value={s.id}>{s.name} ({s.roll_number})</option>)}</select><div className="grid gap-4 sm:grid-cols-2"><Input type="number" min="0" step="0.01" placeholder="Amount" {...register('amount')} /><Input type="number" min="0" step="0.01" placeholder="Paid amount" {...register('paid_amount')} /></div>{errors.paid_amount && <p className="text-sm text-destructive">{errors.paid_amount.message}</p>}<Input type="date" {...register('due_date')} /><Button type="submit" disabled={busy}>{busy ? 'Saving...' : 'Save fee record'}</Button></form>;
}
