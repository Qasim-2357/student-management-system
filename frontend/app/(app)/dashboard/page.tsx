'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { EmptyState } from '@/components/states/EmptyState';
import { ErrorState } from '@/components/states/ErrorState';
import { LoadingState } from '@/components/states/LoadingState';
import { useAuth } from '@/lib/hooks/use-auth';
import { useAdminDashboard, useStudentDashboard, useTeacherDashboard } from '@/lib/hooks/use-dashboard';

function MetricCard({ label, value }: { label: string; value: string | number }) {
  return (
    <Card>
      <CardHeader className="pb-2"><CardTitle className="text-sm font-medium text-muted-foreground">{label}</CardTitle></CardHeader>
      <CardContent><p className="text-2xl font-bold">{value}</p></CardContent>
    </Card>
  );
}

export default function DashboardPage() {
  const { user, isLoading: authLoading } = useAuth();
  const admin = useAdminDashboard(user?.role === 'admin');
  const teacher = useTeacherDashboard(user?.role === 'teacher');
  const student = useStudentDashboard(user?.role === 'student');
  const query = user?.role === 'admin' ? admin : user?.role === 'teacher' ? teacher : student;

  if (authLoading || query.isLoading) return <LoadingState label="Loading dashboard" rows={6} />;
  if (query.isError) return <ErrorState title="Dashboard unavailable" message="The dashboard could not be loaded." onRetry={() => query.refetch()} />;
  if (!query.data) return <EmptyState title="No dashboard data" description="There is no dashboard information available for this account." />;

  if (user?.role === 'admin' && admin.data) {
    const data = admin.data;
    return (
      <div className="space-y-6">
        <div><h1 className="font-serif text-2xl font-bold">Institutional dashboard</h1><p className="text-sm text-muted-foreground">A current overview of academic operations.</p></div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard label="Students" value={data.total_students} /><MetricCard label="Teachers" value={data.total_teachers} />
          <MetricCard label="Classes" value={data.total_classes} /><MetricCard label="Subjects" value={data.total_subjects} />
          <MetricCard label="Exams" value={data.total_exams} /><MetricCard label="Attendance" value={`${data.overall_attendance_percentage}%`} />
        </div>
      </div>
    );
  }

  if (user?.role === 'teacher' && teacher.data) {
    const data = teacher.data;
    return (
      <div className="space-y-6">
        <div><h1 className="font-serif text-2xl font-bold">Faculty dashboard</h1><p className="text-sm text-muted-foreground">Your authorized academic workload and activity.</p></div>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard label="Assigned classes" value={data.total_assigned_classes} /><MetricCard label="Assigned subjects" value={data.total_assigned_subjects} />
          <MetricCard label="Students" value={data.total_students} /><MetricCard label="Attendance" value={`${data.overall_attendance_percentage}%`} />
        </div>
        <Card><CardHeader><CardTitle>Assigned classes</CardTitle></CardHeader><CardContent><div className="space-y-2">{data.assigned_classes.length ? data.assigned_classes.map((item) => <div key={item.id} className="flex justify-between border-b py-2 text-sm"><span>{item.name} ({item.code})</span><span>{item.student_count} students</span></div>) : <EmptyState title="No assigned classes" />}</div></CardContent></Card>
      </div>
    );
  }

  if (!student.data) return <EmptyState title="No dashboard data" description="There is no dashboard information available for this account." />;
  const data = student.data;
  return (
    <div className="space-y-6">
      <div><h1 className="font-serif text-2xl font-bold">Student dashboard</h1><p className="text-sm text-muted-foreground">Your academic progress and current activity.</p></div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <MetricCard label="Percentage" value={`${data.percentage}%`} /><MetricCard label="Grade" value={data.overall_grade} />
        <MetricCard label="Attendance" value={`${data.attendance_percentage}%`} /><MetricCard label="Upcoming exams" value={data.upcoming_exams.length} />
      </div>
      <Card><CardHeader><CardTitle>Recent marks</CardTitle></CardHeader><CardContent>{data.recent_marks.length ? <div className="space-y-2">{data.recent_marks.map((mark) => <div key={mark.mark_id} className="flex justify-between border-b py-2 text-sm"><span>{mark.subject_name}</span><span>{mark.marks} · {mark.grade}</span></div>)}</div> : <EmptyState title="No marks recorded" description="Your recent marks will appear here when they are published." />}</CardContent></Card>
    </div>
  );
}
