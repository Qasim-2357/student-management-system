export interface MarksChartResponse {
  student_id: number;
  data: Array<{ subject_id: number; subject_name: string; average_marks: number }>;
}

export interface ExamChartResponse {
  student_id: number;
  data: Array<{ exam_id: number; exam_name: string; average_marks: number }>;
}

export interface AttendanceChartResponse {
  student_id: number;
  present: number;
  absent: number;
  total: number;
  percentage: number;
}
