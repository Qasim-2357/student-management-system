from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Student, Teacher, User
from app.schemas.dashboard import (
    AdminDashboardResponse,
    DashboardOverviewResponse,
    StudentDashboardResponse,
    TeacherDashboardResponse,
)
from app.security import get_current_admin, get_current_student, get_current_teacher
from app.services.dashboard import (
    get_admin_dashboard,
    get_dashboard_overview,
    get_student_dashboard,
    get_teacher_dashboard,
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/overview", response_model=DashboardOverviewResponse)
def get_dashboard_overview_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return get_dashboard_overview(db)


@router.get("/admin", response_model=AdminDashboardResponse)
def get_admin_dashboard_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return get_admin_dashboard(db)


@router.get("/teacher", response_model=TeacherDashboardResponse)
def get_teacher_dashboard_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_teacher),
):
    teacher = db.scalar(select(Teacher).where(Teacher.user_id == current_user.id))
    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Teacher profile not found for the current user",
        )
    return get_teacher_dashboard(db, teacher)


@router.get("/student", response_model=StudentDashboardResponse)
def get_student_dashboard_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_student),
):
    student = db.scalar(select(Student).where(Student.user_id == current_user.id))
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found for the current user",
        )
    return get_student_dashboard(db, student)