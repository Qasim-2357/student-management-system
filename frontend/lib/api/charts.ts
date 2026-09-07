import { apiFetch } from '@/lib/api/client';
import type { AttendanceChartResponse, ExamChartResponse, MarksChartResponse } from '@/lib/types/charts';

export function getMarksChart(studentId: number) {
  return apiFetch<MarksChartResponse>(`/students/${studentId}/charts/marks`);
}

export function getExamChart(studentId: number) {
  return apiFetch<ExamChartResponse>(`/students/${studentId}/charts/exams`);
}

export function getAttendanceChart(studentId: number) {
  return apiFetch<AttendanceChartResponse>(`/students/${studentId}/charts/attendance`);
}
