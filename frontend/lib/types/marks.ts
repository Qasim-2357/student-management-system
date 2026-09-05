export interface Mark {
  id: number;
  exam_id: number;
  student_id: number;
  subject_id: number;
  marks: number;
}

export interface MarkCreate {
  exam_id: number;
  student_id: number;
  subject_id: number;
  marks: number;
}

export type MarkUpdate = Partial<MarkCreate>;

export interface MarkListParams {
  search?: string;
  exam_id?: number;
  student_id?: number;
  subject_id?: number;
  page?: number;
  page_size?: number;
}

export interface MarkListResponse {
  items: Mark[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
