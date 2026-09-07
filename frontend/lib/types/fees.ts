export type FeeStatus = 'pending' | 'partial' | 'paid';

export interface Fee {
  id: number;
  student_id: number;
  amount: number;
  paid_amount: number;
  due_amount: number;
  due_date: string;
  status: FeeStatus;
  created_at: string;
}

export interface FeeListResponse {
  items: Fee[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface FeeCreate {
  student_id: number;
  amount: number;
  paid_amount?: number;
  due_date: string;
}

export type FeeUpdate = Partial<FeeCreate>;

export interface FeeReceipt {
  fee: Fee;
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
}
