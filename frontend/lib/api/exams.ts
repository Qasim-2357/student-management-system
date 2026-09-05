import { apiFetch } from '@/lib/api/client';
import type { Exam, ExamCreate, ExamListParams, ExamUpdate, PaginatedResponse } from '@/lib/types/exams';

function queryString(params: ExamListParams): string {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== '') searchParams.set(key, String(value));
  });

  const query = searchParams.toString();
  return query ? `?${query}` : '';
}

export function listExams(params: ExamListParams = {}) {
  return apiFetch<PaginatedResponse<Exam>>(`/exams${queryString(params)}`);
}

export function getExam(id: number) {
  return apiFetch<Exam>(`/exams/${id}`);
}

export function createExam(body: ExamCreate) {
  return apiFetch<Exam>('/exams', { method: 'POST', body });
}

export function updateExam(id: number, body: ExamUpdate) {
  return apiFetch<Exam>(`/exams/${id}`, { method: 'PATCH', body });
}

export function deleteExam(id: number) {
  return apiFetch<void>(`/exams/${id}`, { method: 'DELETE' });
}
