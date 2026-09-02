import type { PaginatedResponse } from '@/lib/types/students';

export interface Teacher {
  id: number;
  user_id: number;
  name: string;
  email: string;
  phone: string;
}

export interface TeacherCreate {
  user_id: number;
  name: string;
  email: string;
  phone: string;
}

export type TeacherUpdate = Partial<TeacherCreate>;

export interface TeacherListParams {
  search?: string;
  page?: number;
  page_size?: number;
}

export type TeacherListResponse = PaginatedResponse<Teacher>;
