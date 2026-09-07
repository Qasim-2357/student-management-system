export interface Assignment {
  id: number;
  title: string;
  description: string | null;
  subject_id: number;
  academic_class_id: number;
  due_date: string;
  created_at: string;
}

export interface AssignmentListResponse {
  items: Assignment[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export type AssignmentCreate = Omit<Assignment, 'id' | 'created_at'>;
export type AssignmentUpdate = Partial<AssignmentCreate>;

export interface Submission {
  id: number;
  assignment_id: number;
  student_id: number;
  submitted_at: string | null;
  status: 'pending' | 'submitted' | 'late';
}

export interface SubmissionListResponse {
  items: Submission[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
