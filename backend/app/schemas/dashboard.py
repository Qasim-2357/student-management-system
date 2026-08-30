from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.academic_class import ClassResponse


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


class TeacherInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    phone: str


class AssignedClassItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    student_count: int


class AssignedSubjectItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str


class TeacherDashboardResponse(BaseModel):
    teacher: TeacherInfo

    total_assigned_classes: int
    total_assigned_subjects: int
    total_students: int

    total_relevant_exams: int
    upcoming_exams: list[UpcomingExamItem] = Field(default_factory=list)

    total_assignments: int
    total_submissions: int
    submitted_submissions: int
    pending_submissions: int

    total_attendance_records: int
    present_attendance_records: int
    overall_attendance_percentage: float

    assigned_classes: list[AssignedClassItem] = Field(default_factory=list)
    assigned_subjects: list[AssignedSubjectItem] = Field(default_factory=list)


class StudentInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    roll_number: str
    email: EmailStr
    phone: str
    course: str
    semester: int


class StudentMarkItem(BaseModel):
    mark_id: int
    exam_id: int
    subject_id: int
    subject_name: str
    marks: float
    grade: str


class StudentDashboardResponse(BaseModel):
    student: StudentInfo
    academic_class: ClassResponse | None = None

    # Marks / academic performance. These values are computed by reusing the
    # existing grade-calculation logic in app/services/grades.py and
    # app/services/performance.py rather than duplicating the grading scale.
    total_results: int
    total_possible_marks: int
    marks_obtained: float
    percentage: float
    average_marks: float
    overall_grade: str
    recent_marks: list[StudentMarkItem] = Field(default_factory=list)

    # Attendance, scoped to this student only.
    total_attendance_records: int
    present_attendance_records: int
    absent_attendance_records: int
    attendance_percentage: float

    # Exams for the student's academic class only.
    total_exams: int
    upcoming_exams: list[UpcomingExamItem] = Field(default_factory=list)
    past_exams_count: int

    # Assignments for the student's academic class, submissions scoped to
    # this student only.
    total_assignments: int
    submitted_assignments: int
    pending_assignments: int

    # Fees, scoped to this student only.
    total_fee_records: int
    paid_fee_records: int
    pending_fee_records: int
    total_fee_amount: float
    paid_fee_amount: float
    due_fee_amount: float