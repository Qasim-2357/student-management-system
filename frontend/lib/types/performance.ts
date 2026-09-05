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