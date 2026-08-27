from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.models import Subject
from app.schemas.subject import SubjectCreate, SubjectUpdate


def get_subject_or_404(db: Session, subject_id: int) -> Subject:
    subject = db.get(Subject, subject_id)
    if subject is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject with id {subject_id} was not found",
        )
    return subject


def _ensure_code_available(
    db: Session,
    code: str,
    subject_id: int | None = None,
) -> None:
    statement = select(Subject.id).where(Subject.code == code)
    if subject_id is not None:
        statement = statement.where(Subject.id != subject_id)
    if db.scalar(statement) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A subject with this code already exists",
        )


def create_subject(db: Session, subject_data: SubjectCreate) -> Subject:
    _ensure_code_available(db, subject_data.code)
    subject = Subject(**subject_data.model_dump())
    db.add(subject)
    _commit_or_raise_conflict(db)
    db.refresh(subject)
    return subject


def update_subject(
    db: Session,
    subject: Subject,
    subject_data: SubjectUpdate,
) -> Subject:
    changes = subject_data.model_dump(exclude_unset=True)
    if "code" in changes:
        _ensure_code_available(db, changes["code"], subject.id)

    for field, value in changes.items():
        setattr(subject, field, value)

    _commit_or_raise_conflict(db)
    db.refresh(subject)
    return subject


def delete_subject(db: Session, subject: Subject) -> None:
    db.delete(subject)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Subject cannot be deleted while related records exist",
        ) from None


def list_subjects(
    db: Session,
    *,
    search: str | None,
    page: int,
    page_size: int,
) -> tuple[list[Subject], int]:
    filters = []
    if search:
        pattern = f"%{search.strip()}%"
        filters.append(
            or_(
                Subject.name.ilike(pattern),
                Subject.code.ilike(pattern),
            )
        )

    total = db.scalar(select(func.count()).select_from(Subject).where(*filters)) or 0
    subjects = db.scalars(
        select(Subject)
        .where(*filters)
        .order_by(Subject.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return subjects, total


def _commit_or_raise_conflict(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Subject data conflicts with an existing record",
        ) from None