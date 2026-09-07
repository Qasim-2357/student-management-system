import { apiFetch } from '@/lib/api/client';
import type { ClassSubjects, TeacherRelationships } from '@/lib/types/relationships';

export function getTeacherRelationships(teacherId: number) {
  return apiFetch<TeacherRelationships>(`/relationships/teachers/${teacherId}`);
}

export function updateTeacherRelationships(teacherId: number, body: TeacherRelationships) {
  return apiFetch<TeacherRelationships>(`/relationships/teachers/${teacherId}`, { method: 'PUT', body });
}

export function getClassSubjects(classId: number) {
  return apiFetch<ClassSubjects>(`/relationships/classes/${classId}/subjects`);
}

export function updateClassSubjects(classId: number, subjectIds: number[]) {
  return apiFetch<ClassSubjects>(`/relationships/classes/${classId}/subjects`, {
    method: 'PUT',
    body: { ids: subjectIds },
  });
}
