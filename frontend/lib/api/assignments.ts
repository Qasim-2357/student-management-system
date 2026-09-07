import { apiFetch } from '@/lib/api/client';
import type { Assignment, AssignmentCreate, AssignmentListResponse, AssignmentUpdate, SubmissionListResponse } from '@/lib/types/assignments';

export function listAssignments(params: { page?: number; page_size?: number; search?: string; subject_id?: number; academic_class_id?: number; due_date?: string } = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => { if (value !== undefined && value !== '') query.set(key, String(value)); });
  return apiFetch<AssignmentListResponse>(`/assignments?${query}`);
}
export const getAssignment = (id: number) => apiFetch<Assignment>(`/assignments/${id}`);
export const createAssignment = (body: AssignmentCreate) => apiFetch<Assignment>('/assignments', { method: 'POST', body });
export const updateAssignment = (id: number, body: AssignmentUpdate) => apiFetch<Assignment>(`/assignments/${id}`, { method: 'PATCH', body });
export const deleteAssignment = (id: number) => apiFetch<void>(`/assignments/${id}`, { method: 'DELETE' });
export const listSubmissions = (id: number, page = 1) => apiFetch<SubmissionListResponse>(`/assignments/${id}/submissions?page=${page}&page_size=20`);
