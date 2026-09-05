import { apiFetch } from '@/lib/api/client';
import type { PaginatedResponse, Subject, SubjectCreate, SubjectListParams, SubjectUpdate } from '@/lib/types/subjects';

function queryString(params: SubjectListParams): string {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== '') searchParams.set(key, String(value));
  });

  const query = searchParams.toString();
  return query ? `?${query}` : '';
}

export function listSubjects(params: SubjectListParams = {}) {
  return apiFetch<PaginatedResponse<Subject>>(`/subjects${queryString(params)}`);
}

export function getSubject(id: number) {
  return apiFetch<Subject>(`/subjects/${id}`);
}

export function createSubject(body: SubjectCreate) {
  return apiFetch<Subject>('/subjects', { method: 'POST', body });
}

export function updateSubject(id: number, body: SubjectUpdate) {
  return apiFetch<Subject>(`/subjects/${id}`, { method: 'PATCH', body });
}

export function deleteSubject(id: number) {
  return apiFetch<void>(`/subjects/${id}`, { method: 'DELETE' });
}
