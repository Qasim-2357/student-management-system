'use client';

import Link from 'next/link';
import { usePathname, useRouter, useSearchParams } from 'next/navigation';
import { useMemo } from 'react';
import { Button, buttonVariants } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { RoleGate } from '@/components/role/RoleGate';
import { LoadingState } from '@/components/states/LoadingState';
import { ErrorState } from '@/components/states/ErrorState';
import { EmptyState } from '@/components/states/EmptyState';
import { useDeleteStudent, useStudents } from '@/lib/hooks/use-students';
import { ApiError } from '@/lib/api/client';

const PAGE_SIZE = 20;

export default function StudentsPage() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const params = useMemo(() => ({
    search: searchParams.get('search') || undefined,
    course: searchParams.get('course') || undefined,
    semester: Number(searchParams.get('semester')) || undefined,
    academic_class_id: Number(searchParams.get('class')) || undefined,
    page: Math.max(1, Number(searchParams.get('page')) || 1),
    page_size: PAGE_SIZE,
  }), [searchParams]);
  const students = useStudents(params);
  const deleteMutation = useDeleteStudent();

  const updateUrl = (changes: Record<string, string | undefined>) => {
    const next = new URLSearchParams(searchParams.toString());
    Object.entries(changes).forEach(([key, value]) => value ? next.set(key, value) : next.delete(key));
    router.push(`${pathname}${next.toString() ? `?${next}` : ''}`);
  };

  const error = students.error instanceof ApiError ? students.error.message : 'Unable to load students.';

  const handleDelete = (id: number, name: string) => {
    if (window.confirm(`Delete ${name}? This action cannot be undone.`)) deleteMutation.mutate(id);
  };

  return (
    <div className="mx-auto max-w-7xl space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <p className="text-sm uppercase tracking-[0.2em] text-muted-foreground">Directory</p>
          <h1 className="mt-1 text-3xl font-semibold tracking-tight">Students</h1>
          <p className="mt-1 text-muted-foreground">Search and manage student records.</p>
        </div>
        <RoleGate roles={['admin']}>
          <Link className={buttonVariants()} href="/students/new">Add student</Link>
        </RoleGate>
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">Student records</CardTitle>
          <div className="grid gap-3 pt-2 sm:grid-cols-3">
            <Input aria-label="Search students" placeholder="Search name, roll number, or email" defaultValue={params.search ?? ''} onChange={(event) => updateUrl({ search: event.target.value.trim() || undefined, page: undefined })} />
            <Input aria-label="Filter by course" placeholder="Course" defaultValue={params.course ?? ''} onChange={(event) => updateUrl({ course: event.target.value.trim() || undefined, page: undefined })} />
            <Input aria-label="Filter by semester" placeholder="Semester" type="number" min={1} defaultValue={params.semester ?? ''} onChange={(event) => updateUrl({ semester: event.target.value || undefined, page: undefined })} />
          </div>
        </CardHeader>
        <CardContent>
          {students.isLoading ? <LoadingState rows={5} label="Loading students" /> : null}
          {students.isError ? <ErrorState message={error} onRetry={() => students.refetch()} /> : null}
          {students.isSuccess && students.data.items.length === 0 ? <EmptyState title="No students found" description="Try adjusting your search or filters." /> : null}
          {students.isSuccess && students.data.items.length > 0 ? (
            <>
              <div className="overflow-x-auto">
                <table className="w-full min-w-[760px] text-left text-sm">
                  <caption className="sr-only">Student records</caption>
                  <thead className="border-b text-muted-foreground"><tr><th scope="col" className="px-3 py-3">Name</th><th scope="col" className="px-3 py-3">Roll number</th><th scope="col" className="px-3 py-3">Email</th><th scope="col" className="px-3 py-3">Course</th><th scope="col" className="px-3 py-3">Semester</th><th scope="col" className="px-3 py-3 text-right">Actions</th></tr></thead>
                  <tbody className="divide-y">
                    {students.data.items.map((student) => <tr key={student.id}><td className="px-3 py-3 font-medium">{student.name}</td><td className="px-3 py-3">{student.roll_number}</td><td className="px-3 py-3">{student.email}</td><td className="px-3 py-3">{student.course}</td><td className="px-3 py-3">{student.semester}</td><td className="px-3 py-3"><div className="flex justify-end gap-2"><Link className={buttonVariants({ variant: 'outline', size: 'sm' })} href={`/students/${student.id}`}>View</Link><RoleGate roles={['admin']}><Link className={buttonVariants({ variant: 'outline', size: 'sm' })} href={`/students/${student.id}/edit`}>Edit</Link><Button variant="destructive" size="sm" onClick={() => handleDelete(student.id, student.name)} disabled={deleteMutation.isPending}>Delete</Button></RoleGate></div></td></tr>)}
                  </tbody>
                </table>
              </div>
              <div className="mt-4 flex items-center justify-between gap-3 text-sm text-muted-foreground">
                <span>{students.data.total} student{students.data.total === 1 ? '' : 's'}</span>
                <div className="flex gap-2"><Button variant="outline" size="sm" disabled={params.page <= 1} onClick={() => updateUrl({ page: String(params.page - 1) })}>Previous</Button><span className="px-2 py-2">Page {students.data.page} of {Math.max(1, students.data.total_pages)}</span><Button variant="outline" size="sm" disabled={students.data.page >= students.data.total_pages} onClick={() => updateUrl({ page: String(params.page + 1) })}>Next</Button></div>
              </div>
            </>
          ) : null}
        </CardContent>
      </Card>
    </div>
  );
}
