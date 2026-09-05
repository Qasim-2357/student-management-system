'use client';

import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { createAttendance, deleteAttendance, getAttendance, listAttendance, updateAttendance } from '@/lib/api/attendance';
import { queryKeys } from '@/lib/query-keys';
import type { AttendanceCreate, AttendanceListParams, AttendanceUpdate } from '@/lib/types/attendance';

export function useAttendance(params: AttendanceListParams) {
  return useQuery({
    queryKey: queryKeys.attendance.list(params),
    queryFn: () => listAttendance(params),
  });
}

export function useAttendanceRecord(id: number) {
  return useQuery({
    queryKey: queryKeys.attendance.detail(id),
    queryFn: () => getAttendance(id),
    enabled: Number.isInteger(id) && id > 0,
  });
}

export function useCreateAttendance() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: AttendanceCreate) => createAttendance(body),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: queryKeys.attendance.all }),
  });
}

export function useUpdateAttendance(id: number) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (body: AttendanceUpdate) => updateAttendance(id, body),
    onSuccess: (attendance) => {
      queryClient.setQueryData(queryKeys.attendance.detail(id), attendance);
      return queryClient.invalidateQueries({ queryKey: queryKeys.attendance.all });
    },
  });
}

export function useDeleteAttendance() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => deleteAttendance(id),
    onSuccess: (_, id) => {
      queryClient.removeQueries({ queryKey: queryKeys.attendance.detail(id) });
      return queryClient.invalidateQueries({ queryKey: queryKeys.attendance.all });
    },
  });
}
