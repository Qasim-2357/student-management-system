from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.models import AcademicClass, Assignment, Student, Subject
from app.schemas.assignment import AssignmentCreate, AssignmentUpdate


def get_assignment_or_404(db: Session, assignment_id: int) -> Assignment:
    assignment = db.get(Assignment, assignment_id)
    if assignment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assignment with id {assignment_id} was not found",
        )
    return assignment


def _ensure_subject_exists(db: Session, subject_id: int) -> None:
    if db.get(Subject, subject_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with id {subject_id} was not found",
        )


def _ensure_academic_class_exists(db: Session, academic_class_id: int) -> None:
    if db.get(AcademicClass, academic_class_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Academic class with id {academic_class_id} was not found",
        )


def _recalculate_submission_statuses(assignment: Assignment) -> None:
    for submission in assignment.submissions:
        if submission.submitted_at is None:
            submission.status = "pending"
        elif submission.submitted_at.date() <= assignment.due_date:
            submission.status = "submitted"
        else:
            submission.status = "late"


def create_assignment(db: Session, assignment_data: AssignmentCreate) -> Assignment:
    _ensure_subject_exists(db, assignment_data.subject_id)
    _ensure_academic_class_exists(db, assignment_data.academic_class_id)

    assignment = Assignment(**assignment_data.model_dump())
    db.add(assignment)
    _commit_or_raise_conflict(db)
    db.refresh(assignment)
    return assignment


def update_assignment(
    db: Session,
    assignment: Assignment,
    assignment_data: AssignmentUpdate,
) -> Assignment:
    changes = assignment_data.model_dump(exclude_unset=True)

    if "subject_id" in changes:
        _ensure_subject_exists(db, changes["subject_id"])
    if "academic_class_id" in changes:
        _ensure_academic_class_exists(db, changes["academic_class_id"])

    for field, value in changes.items():
        setattr(assignment, field, value)

    if "due_date" in changes:
        _recalculate_submission_statuses(assignment)

    _commit_or_raise_conflict(db)
    db.refresh(assignment)
    return assignment


def delete_assignment(db: Session, assignment: Assignment) -> None:
    db.delete(assignment)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Assignment cannot be deleted while related submissions exist",
        ) from None


def list_assignments(
    db: Session,
    *,
    search: str | None,
    subject_id: int | None,
    academic_class_id: int | None,
    due_date,
    page: int,
    page_size: int,
) -> tuple[list[Assignment], int]:
    filters = []
    if subject_id is not None:
        filters.append(Assignment.subject_id == subject_id)
    if academic_class_id is not None:
        filters.append(Assignment.academic_class_id == academic_class_id)
    if due_date is not None:
        filters.append(Assignment.due_date == due_date)

    base_query = select(Assignment)
    count_query = select(func.count()).select_from(Assignment)

    if search:
        pattern = f"%{search.strip()}%"
        filters.append(or_(Assignment.title.ilike(pattern), Assignment.description.ilike(pattern)))

    total = db.scalar(count_query.where(*filters)) or 0
    assignments = db.scalars(
        base_query
        .where(*filters)
        .order_by(Assignment.due_date.asc(), Assignment.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return assignments, total


def _commit_or_raise_conflict(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Assignment data conflicts with an existing record",
        ) from None
