'use client';

import { useQuery } from '@tanstack/react-query';
import { getAdminDashboard, getStudentDashboard, getTeacherDashboard } from '@/lib/api/dashboard';

export function useAdminDashboard(enabled: boolean) {
  return useQuery({
    queryKey: ['dashboard', 'admin'],
    queryFn: getAdminDashboard,
    enabled,
  });
}

export function useTeacherDashboard(enabled: boolean) {
  return useQuery({
    queryKey: ['dashboard', 'teacher'],
    queryFn: getTeacherDashboard,
    enabled,
  });
}

export function useStudentDashboard(enabled: boolean) {
  return useQuery({
    queryKey: ['dashboard', 'student'],
    queryFn: getStudentDashboard,
    enabled,
  });
}
