from fastapi import HTTPException, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.models.models import AcademicClass, Mark, Student, Teacher, User
from app.schemas.academic_class import ClassResponse
from app.schemas.marksheet import (
    MarksheetExamItem,
    MarksheetOverallStats,
    MarksheetResponse,
    MarksheetSubjectItem,
    StudentMarksheetInfo,
)
from app.schemas.student import (
    StudentCreate,
    StudentProfileMark,
    StudentProfileResponse,
    StudentUpdate,
)
from app.services.grading import calculate_grade


def get_student_or_404(db: Session, student_id: int) -> Student:
    student = db.get(Student, student_id)
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} was not found",
        )
    return student


def get_student_profile_or_404(db: Session, student_id: int) -> StudentProfileResponse:
    student = db.scalars(
        select(Student)
        .where(Student.id == student_id)
        .options(
            selectinload(Student.academic_class),
            selectinload(Student.marks).selectinload(Mark.subject),
        )
    ).first()
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} was not found",
        )
    return StudentProfileResponse(
        student=student,
        academic_class=student.academic_class,
        marks=[
            StudentProfileMark(
                id=mark.id,
                subject_id=mark.subject_id,
                subject_name=mark.subject.name,
                marks=mark.marks,
            )
            for mark in sorted(student.marks, key=lambda item: item.id)
        ],
    )


def get_student_marksheet(db: Session, student_id: int) -> MarksheetResponse:
    student = db.scalars(
        select(Student)
        .where(Student.id == student_id)
        .options(
            selectinload(Student.academic_class),
            selectinload(Student.marks)
            .selectinload(Mark.subject),
            selectinload(Student.marks)
            .selectinload(Mark.exam),
        )
    ).first()
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} was not found",
        )

    marks = sorted(student.marks, key=lambda item: (item.exam_id, item.subject_id, item.id))
    exam_groups: dict[int, list[Mark]] = {}
    for mark in marks:
        exam_groups.setdefault(mark.exam_id, []).append(mark)

    exam_marks = []
    for exam_id in sorted(exam_groups):
        exam_marks_for_exam = exam_groups[exam_id]
        exam = exam_marks_for_exam[0].exam
        exam_marks.append(
            MarksheetExamItem(
                exam_id=exam.id,
                exam_name=exam.name,
                exam_type=exam.exam_type,
                exam_date=exam.exam_date,
                subjects=[
                    MarksheetSubjectItem(
                        subject_id=mark.subject_id,
                        subject_name=mark.subject.name,
                        subject_code=mark.subject.code,
                        marks_obtained=mark.marks,
                        grade=calculate_grade(mark.marks),
                    )
                    for mark in sorted(exam_marks_for_exam, key=lambda item: (item.subject_id, item.id))
                ],
            )
        )

    total_marks_obtained = sum(float(mark.marks) for mark in marks)
    total_possible_marks = len(marks) * 100
    percentage = round((total_marks_obtained / total_possible_marks) * 100, 2) if total_possible_marks else 0.0
    overall_grade = calculate_grade(percentage)

    return MarksheetResponse(
        student=StudentMarksheetInfo(
            id=student.id,
            name=student.name,
            roll_number=student.roll_number,
            email=student.email,
            phone=student.phone,
            date_of_birth=student.date_of_birth,
            course=student.course,
            semester=student.semester,
        ),
        academic_class=(
            ClassResponse.model_validate(student.academic_class)
            if student.academic_class is not None
            else None
        ),
        exam_marks=exam_marks,
        overall=MarksheetOverallStats(
            total_marks_obtained=total_marks_obtained,
            total_possible_marks=total_possible_marks,
            percentage=percentage,
            overall_grade=overall_grade,
        ),
    )


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
