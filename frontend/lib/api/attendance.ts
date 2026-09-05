import { apiFetch } from '@/lib/api/client';
import type { Attendance, AttendanceCreate, AttendanceListParams, AttendanceListResponse, AttendanceUpdate } from '@/lib/types/attendance';

function queryString(params: AttendanceListParams): string {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== '') searchParams.set(key, String(value));
  });

  const query = searchParams.toString();
  return query ? `?${query}` : '';
}

export function listAttendance(params: AttendanceListParams = {}) {
  return apiFetch<AttendanceListResponse>(`/attendance${queryString(params)}`);
}

export function getAttendance(id: number) {
  return apiFetch<Attendance>(`/attendance/${id}`);
}

export function createAttendance(body: AttendanceCreate) {
  return apiFetch<Attendance>('/attendance', { method: 'POST', body });
}

export function updateAttendance(id: number, body: AttendanceUpdate) {
  return apiFetch<Attendance>(`/attendance/${id}`, { method: 'PATCH', body });
}

export function deleteAttendance(id: number) {
  return apiFetch<void>(`/attendance/${id}`, { method: 'DELETE' });
}
