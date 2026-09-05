'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createMark, deleteMark, getMark, listMarks, updateMark } from '@/lib/api/marks';
import { queryKeys } from '@/lib/query-keys';
import type { MarkCreate, MarkListParams, MarkUpdate } from '@/lib/types/marks';

export function useMarks(params: MarkListParams) {
  return useQuery({
    queryKey: queryKeys.marks.list(params),
    queryFn: () => listMarks(params),
  });
}

export function useMark(id: number) {
  return useQuery({
    queryKey: queryKeys.marks.detail(id),
    queryFn: () => getMark(id),
    enabled: Number.isInteger(id) && id > 0,
  });
}

export function useCreateMark() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: MarkCreate) => createMark(body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.marks.all }),
  });
}

export function useUpdateMark(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: MarkUpdate) => updateMark(id, body),
    onSuccess: (mark) => {
      queryClient.setQueryData(queryKeys.marks.detail(id), mark);
      return queryClient.invalidateQueries({ queryKey: queryKeys.marks.all });
    },
  });
}

export function useDeleteMark() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteMark(id),
    onSuccess: (_, id) => {
      queryClient.removeQueries({ queryKey: queryKeys.marks.detail(id) });
      return queryClient.invalidateQueries({ queryKey: queryKeys.marks.all });
    },
  });
}
