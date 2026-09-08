from math import ceil

from fastapi import APIRouter, Depends, Query, Response, status as http_status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionListResponse,
    SubmissionResponse,
    SubmissionStatus,
    SubmissionUpdate,
)
from app.security import get_current_admin, get_current_user
from app.services.assignments import get_assignment_or_404
from app.services.student_authorization import (
    authorize_assignment_access,
    authorize_student_access,
    authorize_submission_access,
    authorized_student_ids,
)
from app.services.submissions import (
    create_submission,
    delete_submission,
    get_submission_or_404,
    list_submissions,
    update_submission,
)

router = APIRouter(tags=["Assignments"])


@router.post(
    "/assignments/{assignment_id}/submissions",
    response_model=SubmissionResponse,
    status_code=http_status.HTTP_201_CREATED,
)
def create_submission_endpoint(
    assignment_id: int,
    submission_data: SubmissionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return create_submission(db, assignment_id, submission_data)


@router.get(
    "/assignments/{assignment_id}/submissions",
    response_model=SubmissionListResponse,
)
def list_submissions_endpoint(
    assignment_id: int,
    student_id: int | None = Query(default=None, ge=1),
    submission_status: SubmissionStatus | None = Query(
        default=None,
        alias="status",
    ),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    assignment = get_assignment_or_404(db, assignment_id)

    # Verify that the current user can access this assignment.
    authorize_assignment_access(db, assignment, current_user)

    # Determine which students the current user is allowed to see.
    #
    # Admin   -> None (no restriction)
    # Teacher -> students in their assigned classes
    # Student -> only their own student profile
    scoped_student_ids = authorized_student_ids(db, current_user)

    # If a specific student was requested, verify access before
    # performing the database query and pagination.
    if student_id is not None:
        authorize_student_access(db, student_id, current_user)
        scoped_student_ids = [student_id]

    submissions, total = list_submissions(
        db,
        assignment_id=assignment_id,
        student_id=student_id,
        status=submission_status,
        page=page,
        page_size=page_size,
        student_ids=scoped_student_ids,
    )

    return SubmissionListResponse(
        items=submissions,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total else 0,
    )


@router.get(
    "/submissions/{submission_id}",
    response_model=SubmissionResponse,
)
def get_submission_endpoint(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    submission = get_submission_or_404(db, submission_id)

    # Verify access to both the student and the assignment.
    authorize_submission_access(db, submission, current_user)

    return submission


@router.patch(
    "/submissions/{submission_id}",
    response_model=SubmissionResponse,
)
def update_submission_endpoint(
    submission_id: int,
    submission_data: SubmissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    submission = get_submission_or_404(db, submission_id)

    return update_submission(db, submission, submission_data)


@router.delete(
    "/submissions/{submission_id}",
    status_code=http_status.HTTP_204_NO_CONTENT,
)
def delete_submission_endpoint(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Response:
    submission = get_submission_or_404(db, submission_id)

    delete_submission(db, submission)

    return Response(status_code=http_status.HTTP_204_NO_CONTENT)