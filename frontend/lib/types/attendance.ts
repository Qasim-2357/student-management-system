export type AttendanceStatus = 'present' | 'absent';

export interface Attendance {
  id: number;
  student_id: number;
  attendance_date: string;
  status: AttendanceStatus;
}

export interface AttendanceCreate {
  student_id: number;
  attendance_date: string;
  status: AttendanceStatus;
}

export type AttendanceUpdate = Partial<AttendanceCreate>;

export interface AttendanceListParams {
  student_id?: number;
  attendance_date?: string;
  status?: AttendanceStatus;
  page?: number;
  page_size?: number;
}

export interface AttendanceListResponse {
  items: Attendance[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}
