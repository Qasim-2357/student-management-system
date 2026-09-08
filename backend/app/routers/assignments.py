from datetime import date
from math import ceil

from fastapi import APIRouter, Depends, HTTPException, Response, status as http_status
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
    list_all_filtered_assignments,
    list_assignments,
    update_assignment,
)
from app.services.student_authorization import authorize_assignment_access

router = APIRouter(prefix="/assignments", tags=["Assignments"])


@router.post(
    "",
    response_model=AssignmentResponse,
    status_code=http_status.HTTP_201_CREATED,
)
def create_assignment_endpoint(
    assignment_data: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return create_assignment(db, assignment_data)


@router.get("", response_model=AssignmentListResponse)
def list_assignments_endpoint(
    search: str | None = None,
    subject_id: int | None = None,
    academic_class_id: int | None = None,
    due_date: date | None = None,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.role == "admin":
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

    all_assignments = list_all_filtered_assignments(
        db,
        search=search,
        subject_id=subject_id,
        academic_class_id=academic_class_id,
        due_date=due_date,
    )

    authorized_assignments = []

    for assignment in all_assignments:
        try:
            authorize_assignment_access(
                db,
                assignment,
                current_user,
            )
        except HTTPException as exc:
            if exc.status_code == http_status.HTTP_403_FORBIDDEN:
                continue
            raise

        authorized_assignments.append(assignment)

    total = len(authorized_assignments)

    start = (page - 1) * page_size
    end = start + page_size

    paginated_assignments = authorized_assignments[start:end]

    return AssignmentListResponse(
        items=paginated_assignments,
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
    assignment = get_assignment_or_404(db, assignment_id)

    authorize_assignment_access(
        db,
        assignment,
        current_user,
    )

    return assignment


@router.patch("/{assignment_id}", response_model=AssignmentResponse)
def update_assignment_endpoint(
    assignment_id: int,
    assignment_data: AssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    assignment = get_assignment_or_404(db, assignment_id)

    return update_assignment(
        db,
        assignment,
        assignment_data,
    )


@router.delete(
    "/{assignment_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
)
def delete_assignment_endpoint(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Response:
    assignment = get_assignment_or_404(db, assignment_id)

    delete_assignment(db, assignment)

    return Response(
        status_code=http_status.HTTP_204_NO_CONTENT,
    )