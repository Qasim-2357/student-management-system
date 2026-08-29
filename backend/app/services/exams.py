from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.models import AcademicClass, Exam
from app.schemas.exam import ExamCreate, ExamUpdate


def get_exam_or_404(db: Session, exam_id: int) -> Exam:
    exam = db.get(Exam, exam_id)
    if exam is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exam with id {exam_id} was not found",
        )
    return exam


def _ensure_academic_class_exists(db: Session, academic_class_id: int) -> None:
    if db.get(AcademicClass, academic_class_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Academic class with id {academic_class_id} was not found",
        )


def create_exam(db: Session, exam_data: ExamCreate) -> Exam:
    _ensure_academic_class_exists(db, exam_data.academic_class_id)
    exam = Exam(**exam_data.model_dump())
    db.add(exam)
    _commit_or_raise_conflict(db)
    db.refresh(exam)
    return exam


def update_exam(
    db: Session,
    exam: Exam,
    exam_data: ExamUpdate,
) -> Exam:
    changes = exam_data.model_dump(exclude_unset=True)
    if "academic_class_id" in changes:
        _ensure_academic_class_exists(db, changes["academic_class_id"])

    for field, value in changes.items():
        setattr(exam, field, value)

    _commit_or_raise_conflict(db)
    db.refresh(exam)
    return exam


def delete_exam(db: Session, exam: Exam) -> None:
    db.delete(exam)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Exam cannot be deleted while related records exist",
        ) from None


def list_exams(
    db: Session,
    *,
    search: str | None,
    academic_class_id: int | None,
    exam_type: str | None,
    page: int,
    page_size: int,
) -> tuple[list[Exam], int]:
    filters = []
    if search:
        pattern = f"%{search.strip()}%"
        filters.append(Exam.name.ilike(pattern))
    if academic_class_id is not None:
        filters.append(Exam.academic_class_id == academic_class_id)
    if exam_type is not None:
        filters.append(Exam.exam_type == exam_type)

    total = db.scalar(select(func.count()).select_from(Exam).where(*filters)) or 0
    exams = db.scalars(
        select(Exam)
        .where(*filters)
        .order_by(Exam.exam_date.asc(), Exam.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return exams, total


def _commit_or_raise_conflict(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Exam data conflicts with an existing record",
        ) from None