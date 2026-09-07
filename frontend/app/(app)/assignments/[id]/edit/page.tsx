'use client';
import { useParams, useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { AssignmentForm } from '@/components/assignments/AssignmentForm';
import { useAssignment, useUpdateAssignment } from '@/lib/hooks/use-assignments';
import { useSubjects } from '@/lib/hooks/use-subjects';
import { useClasses } from '@/lib/hooks/use-classes';
import { LoadingState } from '@/components/states/LoadingState';
import { ErrorState } from '@/components/states/ErrorState';
export default function EditAssignmentPage() { const { id } = useParams<{ id: string }>(); const assignment = useAssignment(Number(id)); const update = useUpdateAssignment(Number(id)); const subjects = useSubjects({ page: 1, page_size: 100 }); const classes = useClasses({ page: 1, page_size: 100 }); const router = useRouter(); if (assignment.isLoading) return <LoadingState />; if (assignment.isError || !assignment.data) return <ErrorState title="Assignment unavailable" onRetry={() => assignment.refetch()} />; return <Card className="mx-auto max-w-3xl"><CardHeader><CardTitle>Edit assignment</CardTitle></CardHeader><CardContent><AssignmentForm initialData={assignment.data} subjects={subjects.data?.items ?? []} classes={classes.data?.items ?? []} busy={update.isPending} onSubmit={(data) => update.mutate(data, { onSuccess: () => router.push(`/assignments/${id}`) })} /></CardContent></Card>; }
