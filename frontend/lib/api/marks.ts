import { apiFetch } from '@/lib/api/client';
import type { Mark, MarkCreate, MarkListParams, MarkListResponse, MarkUpdate } from '@/lib/types/marks';

function queryString(params: MarkListParams): string {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== '') searchParams.set(key, String(value));
  });

  const query = searchParams.toString();
  return query ? `?${query}` : '';
}

export function listMarks(params: MarkListParams = {}) {
  return apiFetch<MarkListResponse>(`/marks${queryString(params)}`);
}

export function getMark(id: number) {
  return apiFetch<Mark>(`/marks/${id}`);
}

export function createMark(body: MarkCreate) {
  return apiFetch<Mark>('/marks', { method: 'POST', body });
}

export function updateMark(id: number, body: MarkUpdate) {
  return apiFetch<Mark>(`/marks/${id}`, { method: 'PATCH', body });
}

export function deleteMark(id: number) {
  return apiFetch<void>(`/marks/${id}`, { method: 'DELETE' });
}
