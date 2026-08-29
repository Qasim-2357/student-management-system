from pydantic import BaseModel


class MarksChartItem(BaseModel):
    subject_id: int
    subject_name: str
    average_marks: float


class MarksChartResponse(BaseModel):
    student_id: int
    data: list[MarksChartItem]


class ExamChartItem(BaseModel):
    exam_id: int
    exam_name: str
    average_marks: float


class ExamChartResponse(BaseModel):
    student_id: int
    data: list[ExamChartItem]


class AttendanceChartResponse(BaseModel):
    student_id: int
    present: int
    absent: int
    total: int
    percentage: float
