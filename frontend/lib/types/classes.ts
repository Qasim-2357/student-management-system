import type { PaginatedResponse } from '@/lib/types/students';

export interface AcademicClass {
  id: number;
  name: string;
  code: string;
  course: string;
  semester: number;
}

export interface ClassCreate {
  name: string;
  code: string;
  course: string;
  semester: number;
}

export type ClassUpdate = Partial<ClassCreate>;

export interface ClassListParams {
  search?: string;
  page?: number;
  page_size?: number;
}

export type ClassListResponse = PaginatedResponse<AcademicClass>;
