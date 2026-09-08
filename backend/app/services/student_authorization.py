from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.models import (
    Assignment,
    AssignmentSubmission,
    Attendance,
    Fee,
    Mark,
    Student,
    Teacher,
    User,
    teacher_academic_classes,
    teacher_subjects,
)


def authorized_student_ids(
    db: Session,
    current_user: User,
) -> list[int] | None:
    """
    Return the student IDs that the current user is allowed to access.

    Admin:
        None means no student restriction.

    Student:
        Only their own student profile.

    Teacher:
        Students belonging to classes assigned to that teacher.

    Other roles:
        Empty list.
    """
    if current_user.role == "admin":
        return None

    if current_user.role == "student":
        student_id = db.scalar(
            select(Student.id).where(
                Student.user_id == current_user.id
            )
        )

        return [student_id] if student_id is not None else []

    if current_user.role == "teacher":
        teacher_exists = db.scalar(
            select(Teacher.id).where(
                Teacher.user_id == current_user.id
            )
        )

        if teacher_exists is None:
            return []

        return list(
            db.scalars(
                select(Student.id)
                .join(
                    teacher_academic_classes,
                    Student.academic_class_id
                    == teacher_academic_classes.c.academic_class_id,
                )
                .join(
                    Teacher,
                    Teacher.id
                    == teacher_academic_classes.c.teacher_id,
                )
                .where(
                    Teacher.user_id == current_user.id
                )
                .order_by(Student.id.asc())
            ).all()
        )

    return []


def authorize_student_access(
    db: Session,
    student_id: int,
    current_user: User,
) -> Student:
    """
    Verify that the current user is allowed to access a student.
    """
    student = db.get(Student, student_id)

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} was not found",
        )

    if current_user.role == "admin":
        return student

    if current_user.role == "student":
        allowed = student.user_id == current_user.id

    elif current_user.role == "teacher":
        scoped_ids = authorized_student_ids(
            db,
            current_user,
        )
        allowed = bool(scoped_ids) and student_id in scoped_ids

    else:
        allowed = False

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this student's data",
        )

    return student


def authorize_mark_access(
    db: Session,
    mark: Mark,
    current_user: User,
) -> None:
    """
    Verify access to a mark through its student.
    """
    authorize_student_access(
        db,
        mark.student_id,
        current_user,
    )


def authorize_attendance_access(
    db: Session,
    attendance: Attendance,
    current_user: User,
) -> None:
    """
    Verify access to attendance through its student.
    """
    authorize_student_access(
        db,
        attendance.student_id,
        current_user,
    )


def authorize_fee_access(
    db: Session,
    fee: Fee,
    current_user: User,
) -> None:
    """
    Verify access to fees through the associated student.
    """
    authorize_student_access(
        db,
        fee.student_id,
        current_user,
    )


def authorize_assignment_access(
    db: Session,
    assignment: Assignment,
    current_user: User,
) -> None:
    """
    Verify that the current user is allowed to access an assignment.

    Admin:
        All assignments.

    Student:
        Assignments belonging to their academic class.

    Teacher:
        Assignment must belong to a class AND subject that are both
        assigned to the same teacher.
    """
    if current_user.role == "admin":
        return

    if current_user.role == "student":
        student = db.scalar(
            select(Student).where(
                Student.user_id == current_user.id
            )
        )

        allowed = (
            student is not None
            and student.academic_class_id
            == assignment.academic_class_id
        )

    elif current_user.role == "teacher":
        teacher_id = db.scalar(
            select(Teacher.id).where(
                Teacher.user_id == current_user.id
            )
        )

        if teacher_id is None:
            allowed = False
        else:
            # The same teacher must be assigned to:
            # 1. the assignment's academic class
            # 2. the assignment's subject
            #
            # The teacher ID equality is important because it prevents
            # combining one teacher's class assignment with another
            # teacher's subject assignment.
            allowed = (
                db.scalar(
                    select(Assignment.id)
                    .join(
                        teacher_academic_classes,
                        Assignment.academic_class_id
                        == teacher_academic_classes.c.academic_class_id,
                    )
                    .join(
                        teacher_subjects,
                        Assignment.subject_id
                        == teacher_subjects.c.subject_id,
                    )
                    .where(
                        Assignment.id == assignment.id,
                        teacher_academic_classes.c.teacher_id
                        == teacher_id,
                        teacher_subjects.c.teacher_id
                        == teacher_id,
                    )
                )
                is not None
            )

    else:
        allowed = False

    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this assignment",
        )


def authorize_submission_access(
    db: Session,
    submission: AssignmentSubmission,
    current_user: User,
) -> None:
    """
    A submission requires authorization through both:
    1. the student
    2. the assignment
    """
    authorize_student_access(
        db,
        submission.student_id,
        current_user,
    )

    authorize_assignment_access(
        db,
        submission.assignment,
        current_user,
    )