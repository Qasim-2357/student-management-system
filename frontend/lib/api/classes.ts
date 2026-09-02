import { apiFetch } from '@/lib/api/client';
import type { AcademicClass, ClassCreate, ClassListParams, ClassListResponse, ClassUpdate } from '@/lib/types/classes';

function queryString(params: ClassListParams): string {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== '') searchParams.set(key, String(value));
  });
  const query = searchParams.toString();
  return query ? `?${query}` : '';
}

export function listClasses(params: ClassListParams = {}) {
  return apiFetch<ClassListResponse>(`/classes${queryString(params)}`);
}

export function getClass(id: number) {
  return apiFetch<AcademicClass>(`/classes/${id}`);
}

export function createClass(body: ClassCreate) {
  return apiFetch<AcademicClass>('/classes', { method: 'POST', body });
}

export function updateClass(id: number, body: ClassUpdate) {
  return apiFetch<AcademicClass>(`/classes/${id}`, { method: 'PATCH', body });
}

export function deleteClass(id: number) {
  return apiFetch<void>(`/classes/${id}`, { method: 'DELETE' });
}
