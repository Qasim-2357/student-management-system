from pydantic import BaseModel


class MarkGradeResponse(BaseModel):
    mark_id: int
    student_id: int
    subject_id: int
    exam_id: int
    marks: float
    grade: str


class StudentGradeItem(BaseModel):
    mark_id: int
    exam_id: int
    subject_id: int
    marks: float
    grade: str


class StudentGradesResponse(BaseModel):
    student_id: int
    grades: list[StudentGradeItem]