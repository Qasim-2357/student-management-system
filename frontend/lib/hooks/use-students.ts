'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createStudent, deleteStudent, getStudent, listStudents, updateStudent } from '@/lib/api/students';
import { queryKeys } from '@/lib/query-keys';
import type { StudentCreate, StudentListParams, StudentUpdate } from '@/lib/types/students';

export function useStudents(params: StudentListParams) {
  return useQuery({
    queryKey: queryKeys.students.list(params),
    queryFn: () => listStudents(params),
  });
}

export function useStudent(id: number) {
  return useQuery({
    queryKey: queryKeys.students.detail(id),
    queryFn: () => getStudent(id),
    enabled: Number.isInteger(id) && id > 0,
  });
}

export function useCreateStudent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: StudentCreate) => createStudent(body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.students.all }),
  });
}

export function useUpdateStudent(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: StudentUpdate) => updateStudent(id, body),
    onSuccess: (student) => {
      queryClient.setQueryData(queryKeys.students.detail(id), student);
      return queryClient.invalidateQueries({ queryKey: queryKeys.students.all });
    },
  });
}

export function useDeleteStudent() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteStudent(id),
    onSuccess: (_, id) => {
      queryClient.removeQueries({ queryKey: queryKeys.students.detail(id) });
      return queryClient.invalidateQueries({ queryKey: queryKeys.students.all });
    },
  });
}
