export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface Subject {
  id: number;
  name: string;
  code: string;
}

export interface SubjectCreate {
  name: string;
  code: string;
}

export type SubjectUpdate = Partial<SubjectCreate>;

export interface SubjectListParams {
  search?: string;
  page?: number;
  page_size?: number;
}
