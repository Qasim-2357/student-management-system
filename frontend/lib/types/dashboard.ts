export interface UpcomingExam {
  id: number;
  name: string;
  exam_date: string;
  academic_class_name: string | null;
}

export interface AdminDashboard {
  total_students: number;
  total_teachers: number;
  total_classes: number;
  total_subjects: number;
  total_exams: number;
  total_assignments: number;
  total_submissions: number;
  total_fee_records: number;
  paid_fee_records: number;
  pending_fee_records: number;
  total_attendance_records: number;
  overall_attendance_percentage: number;
  recent_students: Array<{ id: number; name: string; email: string; created_at: string }>;
  upcoming_exams: UpcomingExam[];
}

export interface TeacherDashboard {
  teacher: { id: number; name: string; email: string; phone: string };
  total_assigned_classes: number;
  total_assigned_subjects: number;
  total_students: number;
  total_relevant_exams: number;
  upcoming_exams: UpcomingExam[];
  total_assignments: number;
  total_submissions: number;
  submitted_submissions: number;
  pending_submissions: number;
  total_attendance_records: number;
  present_attendance_records: number;
  overall_attendance_percentage: number;
  assigned_classes: Array<{ id: number; name: string; code: string; student_count: number }>;
  assigned_subjects: Array<{ id: number; name: string; code: string }>;
}

export interface StudentDashboard {
  student: {
    id: number;
    name: string;
    roll_number: string;
    email: string;
    phone: string;
    course: string;
    semester: number;
  };
  academic_class: { id: number; name: string; code: string; course: string; semester: number } | null;
  total_results: number;
  total_possible_marks: number;
  marks_obtained: number;
  percentage: number;
  average_marks: number;
  overall_grade: string;
  recent_marks: Array<{
    mark_id: number;
    exam_id: number;
    subject_id: number;
    subject_name: string;
    marks: number;
    grade: string;
  }>;
  total_attendance_records: number;
  present_attendance_records: number;
  absent_attendance_records: number;
  attendance_percentage: number;
  total_exams: number;
  upcoming_exams: UpcomingExam[];
  past_exams_count: number;
  total_assignments: number;
  submitted_assignments: number;
  pending_assignments: number;
  total_fee_records: number;
  paid_fee_records: number;
  pending_fee_records: number;
  total_fee_amount: number;
  paid_fee_amount: number;
  due_fee_amount: number;
}
