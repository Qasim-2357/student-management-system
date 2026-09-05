'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createExam, deleteExam, getExam, listExams, updateExam } from '@/lib/api/exams';
import { queryKeys } from '@/lib/query-keys';
import type { ExamCreate, ExamListParams, ExamUpdate } from '@/lib/types/exams';

export function useExams(params: ExamListParams) {
  return useQuery({
    queryKey: queryKeys.exams.list(params),
    queryFn: () => listExams(params),
  });
}

export function useExam(id: number) {
  return useQuery({
    queryKey: queryKeys.exams.detail(id),
    queryFn: () => getExam(id),
    enabled: Number.isInteger(id) && id > 0,
  });
}

export function useCreateExam() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: ExamCreate) => createExam(body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.exams.all }),
  });
}

export function useUpdateExam(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: ExamUpdate) => updateExam(id, body),
    onSuccess: (exam) => {
      queryClient.setQueryData(queryKeys.exams.detail(id), exam);
      return queryClient.invalidateQueries({ queryKey: queryKeys.exams.all });
    },
  });
}

export function useDeleteExam() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteExam(id),
    onSuccess: (_, id) => {
      queryClient.removeQueries({ queryKey: queryKeys.exams.detail(id) });
      return queryClient.invalidateQueries({ queryKey: queryKeys.exams.all });
    },
  });
}
