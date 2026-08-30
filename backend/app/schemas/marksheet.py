from datetime import date

from pydantic import BaseModel, ConfigDict

from app.schemas.academic_class import ClassResponse


class StudentMarksheetInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    roll_number: str
    email: str
    phone: str
    date_of_birth: date | None
    course: str
    semester: int


class MarksheetSubjectItem(BaseModel):
    subject_id: int
    subject_name: str
    subject_code: str
    marks_obtained: float
    grade: str


class MarksheetExamItem(BaseModel):
    exam_id: int
    exam_name: str
    exam_type: str
    exam_date: date
    subjects: list[MarksheetSubjectItem]


class MarksheetOverallStats(BaseModel):
    total_marks_obtained: float
    total_possible_marks: int
    percentage: float
    overall_grade: str


class MarksheetResponse(BaseModel):
    student: StudentMarksheetInfo
    academic_class: ClassResponse | None
    exam_marks: list[MarksheetExamItem]
    overall: MarksheetOverallStats
