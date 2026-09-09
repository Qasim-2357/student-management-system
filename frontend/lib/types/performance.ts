export interface PerformanceResultItem {
  mark_id: number
  exam_id: number
  subject_id: number
  marks: number
  grade: string
}

export interface PerformanceResponse {
  student_id: number
  total_marks: number
  marks_obtained: number
  percentage: number
  average_marks: number
  grade: string
  total_subjects: number
  results: PerformanceResultItem[]
}

/**
 * AI-generated interpretation of a student's already-calculated
 * performance data. Mirrors backend `AIPerformanceAnalysisResponse`
 * (app/schemas/ai_analysis.py) - the AI only interprets figures the
 * backend already computed, it never derives them itself.
 */
export interface AIPerformanceAnalysis {
  summary: string
  strengths: string[]
  areas_for_improvement: string[]
  recommendations: string[]
}