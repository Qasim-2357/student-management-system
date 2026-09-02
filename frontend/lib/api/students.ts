import { apiFetch } from '@/lib/api/client';
import type { PaginatedResponse, Student, StudentCreate, StudentListParams, StudentUpdate } from '@/lib/types/students';

function queryString(params: StudentListParams): string {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== '') searchParams.set(key, String(value));
  });
  const query = searchParams.toString();
  return query ? `?${query}` : '';
}

export function listStudents(params: StudentListParams = {}) {
  return apiFetch<PaginatedResponse<Student>>(`/students${queryString(params)}`);
}

export function getStudent(id: number) {
  return apiFetch<Student>(`/students/${id}`);
}

export function createStudent(body: StudentCreate) {
  return apiFetch<Student>('/students', { method: 'POST', body });
}

export function updateStudent(id: number, body: StudentUpdate) {
  return apiFetch<Student>(`/students/${id}`, { method: 'PATCH', body });
}

export function deleteStudent(id: number) {
  return apiFetch<void>(`/students/${id}`, { method: 'DELETE' });
}
