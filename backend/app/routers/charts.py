from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.charts import AttendanceChartResponse, ExamChartResponse, MarksChartResponse
from app.security import get_current_user
from app.services.charts import (
    get_student_attendance_chart,
    get_student_exam_chart,
    get_student_marks_chart,
)

router = APIRouter(tags=["Charts"])


@router.get("/students/{student_id}/charts/marks", response_model=MarksChartResponse)
def get_student_marks_chart_endpoint(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_student_marks_chart(db, student_id)


@router.get("/students/{student_id}/charts/exams", response_model=ExamChartResponse)
def get_student_exam_chart_endpoint(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_student_exam_chart(db, student_id)


@router.get("/students/{student_id}/charts/attendance", response_model=AttendanceChartResponse)
def get_student_attendance_chart_endpoint(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_student_attendance_chart(db, student_id)
