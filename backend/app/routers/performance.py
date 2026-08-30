from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.performance import PerformanceResponse
from app.security import get_current_user
from app.services.performance import get_student_performance
from app.services.student_authorization import authorize_student_access

router = APIRouter(tags=["Performance"])


@router.get("/students/{student_id}/performance", response_model=PerformanceResponse)
def get_student_performance_endpoint(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    authorize_student_access(db, student_id, current_user)
    return get_student_performance(db, student_id)
