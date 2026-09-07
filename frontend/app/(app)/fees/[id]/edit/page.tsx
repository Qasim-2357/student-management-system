'use client';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { FeeForm } from '@/components/fees/FeeForm';
import { useFee, useUpdateFee } from '@/lib/hooks/use-fees';
import { useStudents } from '@/lib/hooks/use-students';
import { LoadingState } from '@/components/states/LoadingState';
import { ErrorState } from '@/components/states/ErrorState';
export default function EditFeePage() { const { id } = useParams<{ id: string }>(); const fee = useFee(Number(id)); const update = useUpdateFee(Number(id)); const students = useStudents({ page: 1, page_size: 100 }); const router = useRouter(); if (fee.isLoading) return <LoadingState />; if (fee.isError || !fee.data) return <ErrorState title="Fee record unavailable" onRetry={() => fee.refetch()} />; return <Card className="mx-auto max-w-3xl"><CardHeader><CardTitle>Edit fee record</CardTitle></CardHeader><CardContent><FeeForm initialData={fee.data} students={students.data?.items ?? []} busy={update.isPending} onSubmit={(data) => update.mutate(data, { onSuccess: () => router.push(`/fees/${id}`) })} /></CardContent></Card>; }
