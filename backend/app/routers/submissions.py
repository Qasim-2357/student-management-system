from datetime import datetime
from math import ceil

from fastapi import APIRouter, Depends, Query, Response, status as http_status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.submission import (
    SubmissionCreate,
    SubmissionListResponse,
    SubmissionResponse,
    SubmissionUpdate,
)
from app.security import get_current_admin, get_current_user
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


@router.get("/assignments/{assignment_id}/submissions", response_model=SubmissionListResponse)
def list_submissions_endpoint(
    assignment_id: int,
    student_id: int | None = Query(default=None, ge=1),
    status: str | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    submissions, total = list_submissions(
        db,
        assignment_id=assignment_id,
        student_id=student_id,
        status=status,
        page=page,
        page_size=page_size,
    )
    return SubmissionListResponse(
        items=submissions,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total else 0,
    )


@router.get("/submissions/{submission_id}", response_model=SubmissionResponse)
def get_submission_endpoint(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_submission_or_404(db, submission_id)


@router.patch("/submissions/{submission_id}", response_model=SubmissionResponse)
def update_submission_endpoint(
    submission_id: int,
    submission_data: SubmissionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return update_submission(db, get_submission_or_404(db, submission_id), submission_data)


@router.delete("/submissions/{submission_id}", status_code=http_status.HTTP_204_NO_CONTENT)
def delete_submission_endpoint(
    submission_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Response:
    delete_submission(db, get_submission_or_404(db, submission_id))
    return Response(status_code=http_status.HTTP_204_NO_CONTENT)
