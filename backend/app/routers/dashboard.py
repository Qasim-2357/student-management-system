from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import Teacher, User
from app.schemas.dashboard import AdminDashboardResponse, TeacherDashboardResponse
from app.security import get_current_admin, get_current_teacher
from app.services.dashboard import get_admin_dashboard, get_teacher_dashboard

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


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