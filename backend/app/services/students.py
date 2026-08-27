from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.models import AcademicClass, Student, Teacher, User
from app.schemas.student import StudentCreate, StudentUpdate


def get_student_or_404(db: Session, student_id: int) -> Student:
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} was not found",
        )
    return student


def _validate_relationships(
    db: Session,
    *,
    user_id: int | None,
    academic_class_id: int | None,
    student_id: int | None = None,
) -> None:
    if user_id is not None:
        user = db.get(User, user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"User with id {user_id} was not found",
            )
        if user.role != "student":
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="A student profile can only be linked to a user with the student role",
            )
        if db.scalar(select(Teacher.id).where(Teacher.user_id == user_id)) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This user is already linked to a teacher profile",
            )

        statement = select(Student.id).where(Student.user_id == user_id)
        if student_id is not None:
            statement = statement.where(Student.id != student_id)
        if db.scalar(statement) is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="This user is already linked to another student",
            )

    if academic_class_id is not None and db.get(AcademicClass, academic_class_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Academic class with id {academic_class_id} was not found",
        )


def _ensure_roll_number_available(
    db: Session,
    roll_number: str,
    student_id: int | None = None,
) -> None:
    statement = select(Student.id).where(Student.roll_number == roll_number)
    if student_id is not None:
        statement = statement.where(Student.id != student_id)
    if db.scalar(statement) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A student with this roll number already exists",
        )


def create_student(db: Session, student_data: StudentCreate) -> Student:
    _ensure_roll_number_available(db, student_data.roll_number)
    _validate_relationships(
        db,
        user_id=student_data.user_id,
        academic_class_id=student_data.academic_class_id,
    )
    student = Student(**student_data.model_dump())
    db.add(student)
    _commit_or_raise_conflict(db)
    db.refresh(student)
    return student


def update_student(
    db: Session,
    student: Student,
    student_data: StudentUpdate,
) -> Student:
    changes = student_data.model_dump(exclude_unset=True)
    if "roll_number" in changes:
        _ensure_roll_number_available(db, changes["roll_number"], student.id)

    _validate_relationships(
        db,
        user_id=changes.get("user_id", student.user_id),
        academic_class_id=changes.get("academic_class_id", student.academic_class_id),
        student_id=student.id,
    )
    for field, value in changes.items():
        setattr(student, field, value)

    _commit_or_raise_conflict(db)
    db.refresh(student)
    return student


def delete_student(db: Session, student: Student) -> None:
    db.delete(student)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student cannot be deleted while related marks exist",
        ) from None


def list_students(
    db: Session,
    *,
    search: str | None,
    course: str | None,
    semester: int | None,
    academic_class_id: int | None,
    page: int,
    page_size: int,
) -> tuple[list[Student], int]:
    filters = []
    if search:
        pattern = f"%{search.strip()}%"
        filters.append(
            or_(
                Student.name.ilike(pattern),
                Student.roll_number.ilike(pattern),
                Student.email.ilike(pattern),
            )
        )
    if course is not None:
        filters.append(Student.course == course)
    if semester is not None:
        filters.append(Student.semester == semester)
    if academic_class_id is not None:
        filters.append(Student.academic_class_id == academic_class_id)

    total = db.scalar(select(func.count()).select_from(Student).where(*filters)) or 0
    students = db.scalars(
        select(Student)
        .where(*filters)
        .order_by(Student.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return students, total


def _commit_or_raise_conflict(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student data conflicts with an existing record",
        ) from None
