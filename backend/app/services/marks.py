from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.models import Exam, Mark, Student, Subject
from app.schemas.mark import MarkCreate, MarkUpdate


def get_mark_or_404(db: Session, mark_id: int) -> Mark:
    mark = db.get(Mark, mark_id)
    if mark is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mark with id {mark_id} was not found",
        )
    return mark


def _ensure_exam_exists(db: Session, exam_id: int) -> None:
    if db.get(Exam, exam_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exam with id {exam_id} was not found",
        )


def _ensure_student_exists(db: Session, student_id: int) -> None:
    if db.get(Student, student_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} was not found",
        )


def _ensure_subject_exists(db: Session, subject_id: int) -> None:
    if db.get(Subject, subject_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with id {subject_id} was not found",
        )


def _ensure_combination_available(
    db: Session,
    exam_id: int,
    student_id: int,
    subject_id: int,
    mark_id: int | None = None,
) -> None:
    statement = select(Mark.id).where(
        Mark.exam_id == exam_id,
        Mark.student_id == student_id,
        Mark.subject_id == subject_id,
    )
    if mark_id is not None:
        statement = statement.where(Mark.id != mark_id)
    if db.scalar(statement) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A mark for this exam, student, and subject already exists",
        )


def create_mark(db: Session, mark_data: MarkCreate) -> Mark:
    _ensure_exam_exists(db, mark_data.exam_id)
    _ensure_student_exists(db, mark_data.student_id)
    _ensure_subject_exists(db, mark_data.subject_id)
    _ensure_combination_available(
        db,
        mark_data.exam_id,
        mark_data.student_id,
        mark_data.subject_id,
    )
    mark = Mark(**mark_data.model_dump())
    db.add(mark)
    _commit_or_raise_conflict(db)
    db.refresh(mark)
    return mark


def update_mark(
    db: Session,
    mark: Mark,
    mark_data: MarkUpdate,
) -> Mark:
    changes = mark_data.model_dump(exclude_unset=True)

    if "exam_id" in changes:
        _ensure_exam_exists(db, changes["exam_id"])
    if "student_id" in changes:
        _ensure_student_exists(db, changes["student_id"])
    if "subject_id" in changes:
        _ensure_subject_exists(db, changes["subject_id"])

    if any(field in changes for field in ("exam_id", "student_id", "subject_id")):
        _ensure_combination_available(
            db,
            changes.get("exam_id", mark.exam_id),
            changes.get("student_id", mark.student_id),
            changes.get("subject_id", mark.subject_id),
            mark.id,
        )

    for field, value in changes.items():
        setattr(mark, field, value)

    _commit_or_raise_conflict(db)
    db.refresh(mark)
    return mark


def delete_mark(db: Session, mark: Mark) -> None:
    db.delete(mark)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Mark cannot be deleted while related records exist",
        ) from None


def list_marks(
    db: Session,
    *,
    search: str | None,
    exam_id: int | None,
    student_id: int | None,
    subject_id: int | None,
    page: int,
    page_size: int,
    student_ids: list[int] | None = None,
) -> tuple[list[Mark], int]:
    filters = []
    if student_ids is not None:
        filters.append(Mark.student_id.in_(student_ids))
    if exam_id is not None:
        filters.append(Mark.exam_id == exam_id)
    if student_id is not None:
        filters.append(Mark.student_id == student_id)
    if subject_id is not None:
        filters.append(Mark.subject_id == subject_id)

    base_query = select(Mark)
    count_query = select(func.count()).select_from(Mark)

    if search:
        pattern = f"%{search.strip()}%"
        base_query = base_query.join(Student, Mark.student_id == Student.id).join(
            Subject, Mark.subject_id == Subject.id
        )
        count_query = count_query.join(Student, Mark.student_id == Student.id).join(
            Subject, Mark.subject_id == Subject.id
        )
        filters.append(
            or_(
                Student.name.ilike(pattern),
                Student.roll_number.ilike(pattern),
                Subject.name.ilike(pattern),
                Subject.code.ilike(pattern),
            )
        )

    total = db.scalar(count_query.where(*filters)) or 0
    marks = db.scalars(
        base_query
        .where(*filters)
        .order_by(Mark.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return marks, total


def _commit_or_raise_conflict(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Mark data conflicts with an existing record",
        ) from None