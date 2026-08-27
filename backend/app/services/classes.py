from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.models import AcademicClass
from app.schemas.academic_class import ClassCreate, ClassUpdate


def get_class_or_404(db: Session, class_id: int) -> AcademicClass:
    academic_class = db.get(AcademicClass, class_id)
    if academic_class is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Class with id {class_id} was not found",
        )
    return academic_class


def _ensure_code_available(
    db: Session,
    code: str,
    class_id: int | None = None,
) -> None:
    statement = select(AcademicClass.id).where(AcademicClass.code == code)
    if class_id is not None:
        statement = statement.where(AcademicClass.id != class_id)
    if db.scalar(statement) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A class with this code already exists",
        )


def create_class(db: Session, class_data: ClassCreate) -> AcademicClass:
    _ensure_code_available(db, class_data.code)
    academic_class = AcademicClass(**class_data.model_dump())
    db.add(academic_class)
    _commit_or_raise_conflict(db)
    db.refresh(academic_class)
    return academic_class


def update_class(
    db: Session,
    academic_class: AcademicClass,
    class_data: ClassUpdate,
) -> AcademicClass:
    changes = class_data.model_dump(exclude_unset=True)
    if "code" in changes:
        _ensure_code_available(db, changes["code"], academic_class.id)

    for field, value in changes.items():
        setattr(academic_class, field, value)

    _commit_or_raise_conflict(db)
    db.refresh(academic_class)
    return academic_class


def delete_class(db: Session, academic_class: AcademicClass) -> None:
    db.delete(academic_class)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Class cannot be deleted while related records exist",
        ) from None


def list_classes(
    db: Session,
    *,
    search: str | None,
    page: int,
    page_size: int,
) -> tuple[list[AcademicClass], int]:
    filters = []
    if search:
        pattern = f"%{search.strip()}%"
        filters.append(
            or_(
                AcademicClass.name.ilike(pattern),
                AcademicClass.code.ilike(pattern),
                AcademicClass.course.ilike(pattern),
            )
        )

    total = db.scalar(select(func.count()).select_from(AcademicClass).where(*filters)) or 0
    classes = db.scalars(
        select(AcademicClass)
        .where(*filters)
        .order_by(AcademicClass.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return classes, total


def _commit_or_raise_conflict(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Class data conflicts with an existing record",
        ) from None