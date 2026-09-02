'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createClass, deleteClass, getClass, listClasses, updateClass } from '@/lib/api/classes';
import { queryKeys } from '@/lib/query-keys';
import type { ClassCreate, ClassListParams, ClassUpdate } from '@/lib/types/classes';

export function useClasses(params: ClassListParams) {
  return useQuery({
    queryKey: queryKeys.classes.list(params),
    queryFn: () => listClasses(params),
  });
}

export function useAcademicClass(id: number) {
  return useQuery({
    queryKey: queryKeys.classes.detail(id),
    queryFn: () => getClass(id),
    enabled: Number.isInteger(id) && id > 0,
  });
}

export function useCreateClass() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: ClassCreate) => createClass(body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.classes.all }),
  });
}

export function useUpdateClass(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: ClassUpdate) => updateClass(id, body),
    onSuccess: (academicClass) => {
      queryClient.setQueryData(queryKeys.classes.detail(id), academicClass);
      return queryClient.invalidateQueries({ queryKey: queryKeys.classes.all });
    },
  });
}

export function useDeleteClass() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteClass(id),
    onSuccess: (_, id) => {
      queryClient.removeQueries({ queryKey: queryKeys.classes.detail(id) });
      return queryClient.invalidateQueries({ queryKey: queryKeys.classes.all });
    },
  });
}
