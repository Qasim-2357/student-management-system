import { useMutation, useQuery } from "@tanstack/react-query"
import { queryKeys } from "../query-keys"
import { getStudentAIPerformanceAnalysis, getStudentPerformance } from "../api/performance"
import type { ApiError } from "../api/client"
import type { AIPerformanceAnalysis } from "../types/performance"

export function useStudentPerformance(studentId?: number) {
  const hasValidStudentId =
    typeof studentId === "number" && Number.isInteger(studentId) && studentId > 0

  return useQuery({
    queryKey: queryKeys.performance.student(studentId ?? 0),
    queryFn: () => {
      if (typeof studentId !== "number" || !Number.isInteger(studentId) || studentId <= 0) {
        throw new Error("Student ID required")
      }
      return getStudentPerformance(studentId)
    },
    enabled: hasValidStudentId,
  })
}

/**
 * Explicitly triggered ("Analyze Performance" button) AI interpretation of
 * a student's performance. Modeled as a mutation rather than a query since
 * it must never run automatically on mount/navigation and must never be
 * retried automatically - both of which useMutation gives us by default,
 * unlike useQuery.
 */
export function useAnalyzeStudentPerformance() {
  return useMutation<AIPerformanceAnalysis, ApiError, number>({
    mutationFn: (studentId: number) => getStudentAIPerformanceAnalysis(studentId),
    retry: false,
  })
}