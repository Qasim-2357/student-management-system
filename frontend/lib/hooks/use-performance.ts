import { useQuery } from "@tanstack/react-query"
import { queryKeys } from "../query-keys"
import { getStudentPerformance } from "../api/performance"

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