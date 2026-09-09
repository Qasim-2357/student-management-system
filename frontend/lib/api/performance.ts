import { apiFetch } from "./client"
import type { AIPerformanceAnalysis, PerformanceResponse } from "../types/performance"

export async function getStudentPerformance(studentId: number): Promise<PerformanceResponse> {
  return apiFetch<PerformanceResponse>(`/students/${studentId}/performance`)
}

/**
 * Requests an AI-generated interpretation of a student's already-calculated
 * performance. Same-origin, cookie-authenticated request via apiFetch - no
 * AI provider credentials ever touch the browser. Authorization (student
 * can only see their own analysis; teacher/admin scoping) is enforced by
 * the backend's existing `authorize_student_access`, not here.
 */
export async function getStudentAIPerformanceAnalysis(studentId: number): Promise<AIPerformanceAnalysis> {
  return apiFetch<AIPerformanceAnalysis>(`/students/${studentId}/performance/analysis`)
}