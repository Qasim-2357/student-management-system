'use client';

import { useQuery } from '@tanstack/react-query';
import { getAttendanceChart, getExamChart, getMarksChart } from '@/lib/api/charts';

export function useStudentCharts(studentId: number | undefined) {
  const enabled = Number.isInteger(studentId) && (studentId ?? 0) > 0;
  const requireStudentId = () => {
    if (!enabled || studentId === undefined) {
      throw new Error('A valid student is required for chart data');
    }
    return studentId;
  };
  return {
    marks: useQuery({ queryKey: ['charts', 'marks', studentId], queryFn: () => getMarksChart(requireStudentId()), enabled }),
    exams: useQuery({ queryKey: ['charts', 'exams', studentId], queryFn: () => getExamChart(requireStudentId()), enabled }),
    attendance: useQuery({ queryKey: ['charts', 'attendance', studentId], queryFn: () => getAttendanceChart(requireStudentId()), enabled }),
  };
}
