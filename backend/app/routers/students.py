from math import ceil

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.student import (
    StudentCreate,
    StudentListResponse,
    StudentProfileResponse,
    StudentResponse,
    StudentUpdate,
)
from app.security import get_current_admin, get_current_user
from app.services.students import (
    create_student,
    delete_student,
    get_student_or_404,
    get_student_profile_or_404,
    list_students,
    update_student,
)

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
def create_student_endpoint(
    student_data: StudentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return create_student(db, student_data)


@router.get("", response_model=StudentListResponse)
def list_students_endpoint(
    search: str | None = Query(default=None, min_length=1, max_length=100),
    course: str | None = Query(default=None, min_length=1, max_length=100),
    semester: int | None = Query(default=None, ge=1),
    academic_class_id: int | None = Query(default=None, ge=1),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    students, total = list_students(
        db,
        search=search,
        course=course,
        semester=semester,
        academic_class_id=academic_class_id,
        page=page,
        page_size=page_size,
    )
    return StudentListResponse(
        items=students,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total else 0,
    )


@router.get("/{student_id}/profile", response_model=StudentProfileResponse)
def get_student_profile_endpoint(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_student_profile_or_404(db, student_id)


@router.get("/{student_id}", response_model=StudentResponse)
def get_student_endpoint(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_student_or_404(db, student_id)


@router.patch("/{student_id}", response_model=StudentResponse)
def update_student_endpoint(
    student_id: int,
    student_data: StudentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return update_student(db, get_student_or_404(db, student_id), student_data)


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student_endpoint(
    student_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Response:
    delete_student(db, get_student_or_404(db, student_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
