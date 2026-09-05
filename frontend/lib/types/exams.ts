export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface Exam {
  id: number;
  name: string;
  exam_type: string;
  exam_date: string;
  academic_class_id: number;
}

export interface ExamCreate {
  name: string;
  exam_type: string;
  exam_date: string;
  academic_class_id: number;
}

export type ExamUpdate = Partial<ExamCreate>;

export interface ExamListParams {
  search?: string;
  academic_class_id?: number;
  exam_type?: string;
  page?: number;
  page_size?: number;
}
