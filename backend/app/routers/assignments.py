from datetime import date
from math import ceil

from fastapi import APIRouter, Depends, Query, Response, status as http_status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.assignment import (
    AssignmentCreate,
    AssignmentListResponse,
    AssignmentResponse,
    AssignmentUpdate,
)
from app.security import get_current_admin, get_current_user
from app.services.assignments import (
    create_assignment,
    delete_assignment,
    get_assignment_or_404,
    list_assignments,
    update_assignment,
)

router = APIRouter(prefix="/assignments", tags=["Assignments"])


@router.post("", response_model=AssignmentResponse, status_code=http_status.HTTP_201_CREATED)
def create_assignment_endpoint(
    assignment_data: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return create_assignment(db, assignment_data)


@router.get("", response_model=AssignmentListResponse)
def list_assignments_endpoint(
    search: str | None = Query(default=None, min_length=1, max_length=100),
    subject_id: int | None = Query(default=None, ge=1),
    academic_class_id: int | None = Query(default=None, ge=1),
    due_date: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assignments, total = list_assignments(
        db,
        search=search,
        subject_id=subject_id,
        academic_class_id=academic_class_id,
        due_date=due_date,
        page=page,
        page_size=page_size,
    )
    return AssignmentListResponse(
        items=assignments,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total else 0,
    )


@router.get("/{assignment_id}", response_model=AssignmentResponse)
def get_assignment_endpoint(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_assignment_or_404(db, assignment_id)


@router.patch("/{assignment_id}", response_model=AssignmentResponse)
def update_assignment_endpoint(
    assignment_id: int,
    assignment_data: AssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return update_assignment(db, get_assignment_or_404(db, assignment_id), assignment_data)


@router.delete("/{assignment_id}", status_code=http_status.HTTP_204_NO_CONTENT)
def delete_assignment_endpoint(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Response:
    delete_assignment(db, get_assignment_or_404(db, assignment_id))
    return Response(status_code=http_status.HTTP_204_NO_CONTENT)
