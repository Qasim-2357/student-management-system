from math import ceil

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.subject import SubjectCreate, SubjectListResponse, SubjectResponse, SubjectUpdate
from app.security import get_current_admin, get_current_user
from app.services.subjects import (
    create_subject,
    delete_subject,
    get_subject_or_404,
    list_subjects,
    update_subject,
)

router = APIRouter(prefix="/subjects", tags=["Subjects"])


@router.post("", response_model=SubjectResponse, status_code=status.HTTP_201_CREATED)
def create_subject_endpoint(
    subject_data: SubjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return create_subject(db, subject_data)


@router.get("", response_model=SubjectListResponse)
def list_subjects_endpoint(
    search: str | None = Query(default=None, min_length=1, max_length=100),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    subjects, total = list_subjects(
        db,
        search=search,
        page=page,
        page_size=page_size,
    )
    return SubjectListResponse(
        items=subjects,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total else 0,
    )


@router.get("/{subject_id}", response_model=SubjectResponse)
def get_subject_endpoint(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_subject_or_404(db, subject_id)


@router.patch("/{subject_id}", response_model=SubjectResponse)
def update_subject_endpoint(
    subject_id: int,
    subject_data: SubjectUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return update_subject(db, get_subject_or_404(db, subject_id), subject_data)


@router.delete("/{subject_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_subject_endpoint(
    subject_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Response:
    delete_subject(db, get_subject_or_404(db, subject_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)