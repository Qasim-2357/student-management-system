'use client';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FeeForm } from '@/components/fees/FeeForm';
import { useCreateFee } from '@/lib/hooks/use-fees';
import { useStudents } from '@/lib/hooks/use-students';
export default function NewFeePage() { const router = useRouter(); const create = useCreateFee(); const students = useStudents({ page: 1, page_size: 100 }); return <Card className="mx-auto max-w-3xl"><CardHeader><CardTitle>Create fee record</CardTitle></CardHeader><CardContent><FeeForm students={students.data?.items ?? []} busy={create.isPending} error={create.error} onSubmit={(data) => create.mutate(data, { onSuccess: (item) => router.push(`/fees/${item.id}`) })} /></CardContent></Card>; }
