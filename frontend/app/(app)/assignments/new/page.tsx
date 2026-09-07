'use client';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AssignmentForm } from '@/components/assignments/AssignmentForm';
import { useCreateAssignment } from '@/lib/hooks/use-assignments';
import { useSubjects } from '@/lib/hooks/use-subjects';
import { useClasses } from '@/lib/hooks/use-classes';
export default function NewAssignmentPage() { const router = useRouter(); const create = useCreateAssignment(); const subjects = useSubjects({ page: 1, page_size: 100 }); const classes = useClasses({ page: 1, page_size: 100 }); return <Card className="mx-auto max-w-3xl"><CardHeader><CardTitle>Create assignment</CardTitle></CardHeader><CardContent><AssignmentForm subjects={subjects.data?.items ?? []} classes={classes.data?.items ?? []} busy={create.isPending} error={create.error} onSubmit={(data) => create.mutate(data, { onSuccess: (item) => router.push(`/assignments/${item.id}`) })} /></CardContent></Card>; }
