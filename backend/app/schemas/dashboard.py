from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RecentStudentItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    created_at: datetime


class UpcomingExamItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    exam_date: date
    academic_class_name: str | None = None


class AdminDashboardResponse(BaseModel):
    total_students: int
    total_teachers: int
    total_classes: int
    total_subjects: int
    total_exams: int
    total_assignments: int
    total_submissions: int
    total_fee_records: int
    paid_fee_records: int
    pending_fee_records: int
    total_attendance_records: int
    overall_attendance_percentage: float
    recent_students: list[RecentStudentItem] = Field(default_factory=list)
    upcoming_exams: list[UpcomingExamItem] = Field(default_factory=list)
