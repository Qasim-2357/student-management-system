from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.attendance import AttendanceStatus


class AttendanceReportStudent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    roll_number: str
    email: EmailStr
    phone: str
    course: str
    semester: int


class AttendanceReportSummary(BaseModel):
    total_records: int
    present_records: int
    absent_records: int
    attendance_percentage: float


class AttendanceReportRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    attendance_date: date
    status: AttendanceStatus


class AttendanceReportResponse(BaseModel):
    student: AttendanceReportStudent
    summary: AttendanceReportSummary
    attendance_records: list[AttendanceReportRecord]
