'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { getClassSubjects, getTeacherRelationships, updateClassSubjects, updateTeacherRelationships } from '@/lib/api/relationships';
import type { TeacherRelationships } from '@/lib/types/relationships';

export function useTeacherRelationships(teacherId: number) {
  return useQuery({
    queryKey: ['relationships', 'teacher', teacherId],
    queryFn: () => getTeacherRelationships(teacherId),
    enabled: Number.isInteger(teacherId) && teacherId > 0,
  });
}

export function useUpdateTeacherRelationships(teacherId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: TeacherRelationships) => updateTeacherRelationships(teacherId, body),
    onSuccess: (data) => queryClient.setQueryData(['relationships', 'teacher', teacherId], data),
  });
}

export function useClassSubjects(classId: number) {
  return useQuery({
    queryKey: ['relationships', 'class-subjects', classId],
    queryFn: () => getClassSubjects(classId),
    enabled: Number.isInteger(classId) && classId > 0,
  });
}

export function useUpdateClassSubjects(classId: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (subjectIds: number[]) => updateClassSubjects(classId, subjectIds),
    onSuccess: (data) => queryClient.setQueryData(['relationships', 'class-subjects', classId], data),
  });
}
