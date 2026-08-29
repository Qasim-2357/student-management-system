from math import ceil

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.exam import ExamCreate, ExamListResponse, ExamResponse, ExamUpdate
from app.security import get_current_admin, get_current_user
from app.services.exams import (
    create_exam,
    delete_exam,
    get_exam_or_404,
    list_exams,
    update_exam,
)

router = APIRouter(prefix="/exams", tags=["Exams"])


@router.post("", response_model=ExamResponse, status_code=status.HTTP_201_CREATED)
def create_exam_endpoint(
    exam_data: ExamCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return create_exam(db, exam_data)


@router.get("", response_model=ExamListResponse)
def list_exams_endpoint(
    search: str | None = Query(default=None, min_length=1, max_length=100),
    academic_class_id: int | None = Query(default=None, ge=1),
    exam_type: str | None = Query(default=None, min_length=1, max_length=50),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    exams, total = list_exams(
        db,
        search=search,
        academic_class_id=academic_class_id,
        exam_type=exam_type,
        page=page,
        page_size=page_size,
    )
    return ExamListResponse(
        items=exams,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total else 0,
    )


@router.get("/{exam_id}", response_model=ExamResponse)
def get_exam_endpoint(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_exam_or_404(db, exam_id)


@router.patch("/{exam_id}", response_model=ExamResponse)
def update_exam_endpoint(
    exam_id: int,
    exam_data: ExamUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return update_exam(db, get_exam_or_404(db, exam_id), exam_data)


@router.delete("/{exam_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_exam_endpoint(
    exam_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Response:
    delete_exam(db, get_exam_or_404(db, exam_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)