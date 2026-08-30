from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.academic_class import ClassResponse
from app.schemas.fee import FeeResponse


class StudentReportStudent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    roll_number: str
    email: EmailStr
    phone: str
    course: str
    semester: int


class StudentReportMark(BaseModel):
    mark_id: int
    exam_id: int
    exam_name: str
    exam_type: str
    exam_date: date
    subject_id: int
    subject_name: str
    subject_code: str
    marks_obtained: float
    grade: str


class StudentReportMarksSummary(BaseModel):
    total_marks_obtained: float
    total_possible_marks: int
    percentage: float
    overall_grade: str


class StudentReportAttendanceRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    attendance_date: date
    status: str


class StudentReportAttendanceSummary(BaseModel):
    total_records: int
    present_records: int
    absent_records: int
    attendance_percentage: float


class StudentReportAttendance(BaseModel):
    summary: StudentReportAttendanceSummary
    records: list[StudentReportAttendanceRecord]


class StudentReportSubmission(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    submitted_at: datetime | None
    status: str


class StudentReportAssignment(BaseModel):
    id: int
    title: str
    description: str | None
    subject_id: int
    academic_class_id: int
    due_date: date
    submission: StudentReportSubmission | None


class StudentReportFeesSummary(BaseModel):
    total_amount: float
    total_paid_amount: float
    total_due_amount: float
    records: list[FeeResponse]


class StudentReportResponse(BaseModel):
    student: StudentReportStudent
    academic_class: ClassResponse | None
    marks: list[StudentReportMark]
    marks_summary: StudentReportMarksSummary
    attendance: StudentReportAttendance
    assignments: list[StudentReportAssignment]
    fees: StudentReportFeesSummary
