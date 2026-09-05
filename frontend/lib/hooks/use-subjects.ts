'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createSubject, deleteSubject, getSubject, listSubjects, updateSubject } from '@/lib/api/subjects';
import { queryKeys } from '@/lib/query-keys';
import type { SubjectCreate, SubjectListParams, SubjectUpdate } from '@/lib/types/subjects';

export function useSubjects(params: SubjectListParams) {
  return useQuery({
    queryKey: queryKeys.subjects.list(params),
    queryFn: () => listSubjects(params),
  });
}

export function useSubject(id: number) {
  return useQuery({
    queryKey: queryKeys.subjects.detail(id),
    queryFn: () => getSubject(id),
    enabled: Number.isInteger(id) && id > 0,
  });
}

export function useCreateSubject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: SubjectCreate) => createSubject(body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.subjects.all }),
  });
}

export function useUpdateSubject(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: SubjectUpdate) => updateSubject(id, body),
    onSuccess: (subject) => {
      queryClient.setQueryData(queryKeys.subjects.detail(id), subject);
      return queryClient.invalidateQueries({ queryKey: queryKeys.subjects.all });
    },
  });
}

export function useDeleteSubject() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteSubject(id),
    onSuccess: (_, id) => {
      queryClient.removeQueries({ queryKey: queryKeys.subjects.detail(id) });
      return queryClient.invalidateQueries({ queryKey: queryKeys.subjects.all });
    },
  });
}
