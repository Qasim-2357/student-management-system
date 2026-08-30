from math import ceil

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.mark import MarkCreate, MarkListResponse, MarkResponse, MarkUpdate
from app.security import get_current_admin, get_current_user
from app.services.marks import (
    create_mark,
    delete_mark,
    get_mark_or_404,
    list_marks,
    update_mark,
)
from app.services.student_authorization import (
    authorize_mark_access,
    authorize_student_access,
    authorized_student_ids,
)

router = APIRouter(prefix="/marks", tags=["Marks"])


@router.post("", response_model=MarkResponse, status_code=status.HTTP_201_CREATED)
def create_mark_endpoint(
    mark_data: MarkCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return create_mark(db, mark_data)


@router.get("", response_model=MarkListResponse)
def list_marks_endpoint(
    search: str | None = Query(default=None, min_length=1, max_length=100),
    exam_id: int | None = Query(default=None, ge=1),
    student_id: int | None = Query(default=None, ge=1),
    subject_id: int | None = Query(default=None, ge=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    scoped_student_ids = authorized_student_ids(db, current_user)
    if student_id is not None:
        authorize_student_access(db, student_id, current_user)
        scoped_student_ids = [student_id]
    marks, total = list_marks(
        db,
        search=search,
        exam_id=exam_id,
        student_id=student_id,
        subject_id=subject_id,
        page=page,
        page_size=page_size,
        student_ids=scoped_student_ids,
    )
    return MarkListResponse(
        items=marks,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total else 0,
    )


@router.get("/{mark_id}", response_model=MarkResponse)
def get_mark_endpoint(
    mark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mark = get_mark_or_404(db, mark_id)
    authorize_mark_access(db, mark, current_user)
    return mark


@router.patch("/{mark_id}", response_model=MarkResponse)
def update_mark_endpoint(
    mark_id: int,
    mark_data: MarkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return update_mark(db, get_mark_or_404(db, mark_id), mark_data)


@router.delete("/{mark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mark_endpoint(
    mark_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Response:
    delete_mark(db, get_mark_or_404(db, mark_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)