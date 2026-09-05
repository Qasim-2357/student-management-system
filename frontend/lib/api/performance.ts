import { apiFetch } from "./client"
import type { PerformanceResponse } from "../types/performance"

export async function getStudentPerformance(studentId: number): Promise<PerformanceResponse> {
  return apiFetch<PerformanceResponse>(`/students/${studentId}/performance`)
}