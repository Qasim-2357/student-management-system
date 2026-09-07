import { apiFetch } from '@/lib/api/client';
import type { AdminDashboard, StudentDashboard, TeacherDashboard } from '@/lib/types/dashboard';

export function getAdminDashboard() {
  return apiFetch<AdminDashboard>('/dashboard/admin');
}

export function getTeacherDashboard() {
  return apiFetch<TeacherDashboard>('/dashboard/teacher');
}

export function getStudentDashboard() {
  return apiFetch<StudentDashboard>('/dashboard/student');
}
