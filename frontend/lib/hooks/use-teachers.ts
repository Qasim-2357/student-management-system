'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createTeacher, deleteTeacher, getTeacher, listTeachers, updateTeacher } from '@/lib/api/teachers';
import { queryKeys } from '@/lib/query-keys';
import type { TeacherCreate, TeacherListParams, TeacherUpdate } from '@/lib/types/teachers';

export function useTeachers(params: TeacherListParams) {
  return useQuery({
    queryKey: queryKeys.teachers.list(params),
    queryFn: () => listTeachers(params),
  });
}

export function useTeacher(id: number) {
  return useQuery({
    queryKey: queryKeys.teachers.detail(id),
    queryFn: () => getTeacher(id),
    enabled: Number.isInteger(id) && id > 0,
  });
}

export function useCreateTeacher() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: TeacherCreate) => createTeacher(body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.teachers.all }),
  });
}

export function useUpdateTeacher(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: TeacherUpdate) => updateTeacher(id, body),
    onSuccess: (teacher) => {
      queryClient.setQueryData(queryKeys.teachers.detail(id), teacher);
      return queryClient.invalidateQueries({ queryKey: queryKeys.teachers.all });
    },
  });
}

export function useDeleteTeacher() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteTeacher(id),
    onSuccess: (_, id) => {
      queryClient.removeQueries({ queryKey: queryKeys.teachers.detail(id) });
      return queryClient.invalidateQueries({ queryKey: queryKeys.teachers.all });
    },
  });
}
