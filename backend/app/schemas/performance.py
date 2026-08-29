from pydantic import BaseModel


class PerformanceResultItem(BaseModel):
    mark_id: int
    exam_id: int
    subject_id: int
    marks: float
    grade: str


class PerformanceResponse(BaseModel):
    student_id: int
    total_marks: int
    marks_obtained: float
    percentage: float
    average_marks: float
    grade: str
    total_subjects: int
    results: list[PerformanceResultItem]
