export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface Student {
  id: number;
  user_id: number | null;
  academic_class_id: number | null;
  name: string;
  roll_number: string;
  email: string;
  phone: string;
  date_of_birth: string | null;
  course: string;
  semester: number;
  created_at: string;
}

export interface StudentCreate {
  name: string;
  roll_number: string;
  email: string;
  phone: string;
  date_of_birth?: string | null;
  course: string;
  semester: number;
  user_id?: number | null;
  academic_class_id?: number | null;
}

export type StudentUpdate = Partial<StudentCreate>;

export interface StudentListParams {
  search?: string;
  course?: string;
  semester?: number;
  academic_class_id?: number;
  page?: number;
  page_size?: number;
}
