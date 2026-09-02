import { apiFetch } from '@/lib/api/client';
import type { Teacher, TeacherCreate, TeacherListParams, TeacherListResponse, TeacherUpdate } from '@/lib/types/teachers';

function queryString(params: TeacherListParams): string {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== '') searchParams.set(key, String(value));
  });
  const query = searchParams.toString();
  return query ? `?${query}` : '';
}

export function listTeachers(params: TeacherListParams = {}) {
  return apiFetch<TeacherListResponse>(`/teachers${queryString(params)}`);
}

export function getTeacher(id: number) {
  return apiFetch<Teacher>(`/teachers/${id}`);
}

export function createTeacher(body: TeacherCreate) {
  return apiFetch<Teacher>('/teachers', { method: 'POST', body });
}

export function updateTeacher(id: number, body: TeacherUpdate) {
  return apiFetch<Teacher>(`/teachers/${id}`, { method: 'PATCH', body });
}

export function deleteTeacher(id: number) {
  return apiFetch<void>(`/teachers/${id}`, { method: 'DELETE' });
}
