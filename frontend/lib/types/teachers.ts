import type { PaginatedResponse } from '@/lib/types/students';

export interface Teacher {
  id: number;
  teacher_code: string;
  name: string;
  email: string;
  phone: string;
}

export interface TeacherCreate {
  name: string;
  email: string;
  phone: string;
  password?: string;
}

export type TeacherUpdate = Partial<TeacherCreate>;

export interface TeacherListParams {
  search?: string;
  page?: number;
  page_size?: number;
}

export type TeacherListResponse = PaginatedResponse<Teacher>;
