from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.models import Assignment, AssignmentSubmission, Student
from app.schemas.submission import SubmissionCreate, SubmissionUpdate


def get_submission_or_404(db: Session, submission_id: int) -> AssignmentSubmission:
    submission = db.get(AssignmentSubmission, submission_id)
    if submission is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Submission with id {submission_id} was not found",
        )
    return submission


def _ensure_assignment_exists(db: Session, assignment_id: int) -> Assignment:
    assignment = db.get(Assignment, assignment_id)
    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with id {assignment_id} was not found",
        )
    return assignment


def _ensure_student_exists(db: Session, student_id: int) -> None:
    if db.get(Student, student_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} was not found",
        )


def _calculate_submission_status(
    submitted_at,
    due_date,
) -> str:
    if submitted_at is None:
        return "pending"
    if submitted_at.date() <= due_date:
        return "submitted"
    return "late"


def _ensure_unique_submission(
    db: Session,
    assignment_id: int,
    student_id: int,
    submission_id: int | None = None,
) -> None:
    statement = select(AssignmentSubmission.id).where(
        AssignmentSubmission.assignment_id == assignment_id,
        AssignmentSubmission.student_id == student_id,
    )
    if submission_id is not None:
        statement = statement.where(AssignmentSubmission.id != submission_id)
    if db.scalar(statement) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A submission for this assignment and student already exists",
        )


def create_submission(
    db: Session,
    assignment_id: int,
    submission_data: SubmissionCreate,
) -> AssignmentSubmission:
    assignment = _ensure_assignment_exists(db, assignment_id)
    _ensure_student_exists(db, submission_data.student_id)
    _ensure_unique_submission(db, assignment_id, submission_data.student_id)

    submission = AssignmentSubmission(
        assignment_id=assignment_id,
        student_id=submission_data.student_id,
        submitted_at=submission_data.submitted_at,
        status=_calculate_submission_status(
            submission_data.submitted_at,
            assignment.due_date,
        ),
    )
    db.add(submission)
    _commit_or_raise_conflict(db)
    db.refresh(submission)
    return submission


def update_submission(
    db: Session,
    submission: AssignmentSubmission,
    submission_data: SubmissionUpdate,
) -> AssignmentSubmission:
    changes = submission_data.model_dump(exclude_unset=True)

    if "student_id" in changes:
        _ensure_student_exists(db, changes["student_id"])
        _ensure_unique_submission(
            db,
            submission.assignment_id,
            changes["student_id"],
            submission.id,
        )

    for field, value in changes.items():
        setattr(submission, field, value)

    submission.status = _calculate_submission_status(
        submission.submitted_at,
        submission.assignment.due_date,
    )

    _commit_or_raise_conflict(db)
    db.refresh(submission)
    return submission


def delete_submission(db: Session, submission: AssignmentSubmission) -> None:
    db.delete(submission)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Submission cannot be deleted while related records exist",
        ) from None


def list_submissions(
    db: Session,
    *,
    assignment_id: int,
    student_id: int | None,
    status: str | None,
    page: int,
    page_size: int,
) -> tuple[list[AssignmentSubmission], int]:
    _ensure_assignment_exists(db, assignment_id)

    filters = [AssignmentSubmission.assignment_id == assignment_id]
    if student_id is not None:
        filters.append(AssignmentSubmission.student_id == student_id)
    if status is not None:
        filters.append(AssignmentSubmission.status == status)

    total = db.scalar(select(func.count()).select_from(AssignmentSubmission).where(*filters)) or 0
    submissions = db.scalars(
        select(AssignmentSubmission)
        .where(*filters)
        .order_by(AssignmentSubmission.student_id.asc(), AssignmentSubmission.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return submissions, total


def _commit_or_raise_conflict(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Submission data conflicts with an existing record",
        ) from None
