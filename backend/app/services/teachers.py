from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.models import Student, Teacher, User
from app.schemas.teacher import TeacherCreate, TeacherUpdate


def get_teacher_or_404(db: Session, teacher_id: int) -> Teacher:
    teacher = db.get(Teacher, teacher_id)
    if teacher is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with id {teacher_id} was not found",
        )
    return teacher


def _validate_relationships(
    db: Session,
    *,
    user_id: int,
    teacher_id: int | None = None,
) -> None:
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"User with id {user_id} was not found",
        )
    if user.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="A teacher profile can only be linked to a user with the teacher role",
        )
    if db.scalar(select(Student.id).where(Student.user_id == user_id)) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This user is already linked to a student profile",
        )

    statement = select(Teacher.id).where(Teacher.user_id == user_id)
    if teacher_id is not None:
        statement = statement.where(Teacher.id != teacher_id)
    if db.scalar(statement) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This user is already linked to another teacher",
        )


def _ensure_email_available(
    db: Session,
    email: str,
    teacher_id: int | None = None,
) -> None:
    statement = select(Teacher.id).where(Teacher.email == email)
    if teacher_id is not None:
        statement = statement.where(Teacher.id != teacher_id)
    if db.scalar(statement) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A teacher with this email already exists",
        )


def create_teacher(db: Session, teacher_data: TeacherCreate) -> Teacher:
    _ensure_email_available(db, teacher_data.email)
    _validate_relationships(db, user_id=teacher_data.user_id)
    teacher = Teacher(**teacher_data.model_dump())
    db.add(teacher)
    _commit_or_raise_conflict(db)
    db.refresh(teacher)
    return teacher


def update_teacher(
    db: Session,
    teacher: Teacher,
    teacher_data: TeacherUpdate,
) -> Teacher:
    changes = teacher_data.model_dump(exclude_unset=True)
    if "email" in changes:
        _ensure_email_available(db, changes["email"], teacher.id)

    if "user_id" in changes:
        _validate_relationships(db, user_id=changes["user_id"], teacher_id=teacher.id)

    for field, value in changes.items():
        setattr(teacher, field, value)

    _commit_or_raise_conflict(db)
    db.refresh(teacher)
    return teacher


def delete_teacher(db: Session, teacher: Teacher) -> None:
    db.delete(teacher)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Teacher cannot be deleted while related records exist",
        ) from None


def list_teachers(
    db: Session,
    *,
    search: str | None,
    page: int,
    page_size: int,
) -> tuple[list[Teacher], int]:
    filters = []
    if search:
        pattern = f"%{search.strip()}%"
        filters.append(
            or_(
                Teacher.name.ilike(pattern),
                Teacher.email.ilike(pattern),
                Teacher.phone.ilike(pattern),
            )
        )

    total = db.scalar(select(func.count()).select_from(Teacher).where(*filters)) or 0
    teachers = db.scalars(
        select(Teacher)
        .where(*filters)
        .order_by(Teacher.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return teachers, total


def _commit_or_raise_conflict(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Teacher data conflicts with an existing record",
        ) from None