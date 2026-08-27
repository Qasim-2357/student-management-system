from math import ceil

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.teacher import TeacherCreate, TeacherListResponse, TeacherResponse, TeacherUpdate
from app.security import get_current_admin, get_current_user
from app.services.teachers import (
    create_teacher,
    delete_teacher,
    get_teacher_or_404,
    list_teachers,
    update_teacher,
)

router = APIRouter(prefix="/teachers", tags=["Teachers"])


@router.post("", response_model=TeacherResponse, status_code=status.HTTP_201_CREATED)
def create_teacher_endpoint(
    teacher_data: TeacherCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return create_teacher(db, teacher_data)


@router.get("", response_model=TeacherListResponse)
def list_teachers_endpoint(
    search: str | None = Query(default=None, min_length=1, max_length=100),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    teachers, total = list_teachers(
        db,
        search=search,
        page=page,
        page_size=page_size,
    )
    return TeacherListResponse(
        items=teachers,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total else 0,
    )


@router.get("/{teacher_id}", response_model=TeacherResponse)
def get_teacher_endpoint(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_teacher_or_404(db, teacher_id)


@router.patch("/{teacher_id}", response_model=TeacherResponse)
def update_teacher_endpoint(
    teacher_id: int,
    teacher_data: TeacherUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return update_teacher(db, get_teacher_or_404(db, teacher_id), teacher_data)


@router.delete("/{teacher_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_teacher_endpoint(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Response:
    delete_teacher(db, get_teacher_or_404(db, teacher_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)