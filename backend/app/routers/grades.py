from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.grade import MarkGradeResponse, StudentGradesResponse
from app.security import get_current_user
from app.services.grades import get_mark_grade, get_student_grades
from app.services.marks import get_mark_or_404
from app.services.student_authorization import authorize_mark_access, authorize_student_access

router = APIRouter(tags=["Grades"])


@router.get("/grades/{mark_id}", response_model=MarkGradeResponse)
def get_mark_grade_endpoint(
    mark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mark = get_mark_or_404(db, mark_id)
    authorize_mark_access(db, mark, current_user)
    return get_mark_grade(db, mark_id)


@router.get("/students/{student_id}/grades", response_model=StudentGradesResponse)
def get_student_grades_endpoint(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    authorize_student_access(db, student_id, current_user)
    return get_student_grades(db, student_id)