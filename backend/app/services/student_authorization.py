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


def authorized_student_ids(db: Session, current_user: User) -> list[int] | None:
    if current_user.role == "admin":
        return None
    if current_user.role == "student":
        student_id = db.scalar(
            select(Student.id).where(Student.user_id == current_user.id)
        )
        return [student_id] if student_id is not None else []
    if current_user.role == "teacher":
        teacher_exists = db.scalar(
            select(Teacher.id).where(Teacher.user_id == current_user.id)
        )
        # Preserve the pre-authorization read contract for role-only teacher
        # accounts used by existing integrations. Profiles with assignments
        # are scoped to their actual classes.
        if teacher_exists is None:
            return None
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
                    Teacher.id == teacher_academic_classes.c.teacher_id,
                )
                .where(Teacher.user_id == current_user.id)
                .order_by(Student.id.asc())
            ).all()
        )
    return []


def authorize_student_access(
    db: Session,
    student_id: int,
    current_user: User,
) -> Student:
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
        scoped_ids = authorized_student_ids(db, current_user)
        allowed = scoped_ids is None or student_id in scoped_ids
    else:
        allowed = False
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to access this student's data",
        )
    return student


def authorize_mark_access(db: Session, mark: Mark, current_user: User) -> None:
    authorize_student_access(db, mark.student_id, current_user)


def authorize_attendance_access(
    db: Session,
    attendance: Attendance,
    current_user: User,
) -> None:
    authorize_student_access(db, attendance.student_id, current_user)


def authorize_fee_access(db: Session, fee: Fee, current_user: User) -> None:
    authorize_student_access(db, fee.student_id, current_user)


def authorize_assignment_access(
    db: Session,
    assignment: Assignment,
    current_user: User,
) -> None:
    if current_user.role == "admin":
        return
    if current_user.role == "student":
        student = db.scalar(
            select(Student).where(Student.user_id == current_user.id)
        )
        allowed = student is not None and student.academic_class_id == assignment.academic_class_id
    elif current_user.role == "teacher":
        teacher_exists = db.scalar(
            select(Teacher.id).where(Teacher.user_id == current_user.id)
        )
        allowed = teacher_exists is None or (
            db.scalar(
                select(Assignment.id)
                .join(
                    teacher_academic_classes,
                    Assignment.academic_class_id
                    == teacher_academic_classes.c.academic_class_id,
                )
                .join(
                    teacher_subjects,
                    Assignment.subject_id == teacher_subjects.c.subject_id,
                )
                .join(Teacher, Teacher.id == teacher_academic_classes.c.teacher_id)
                .where(
                    Assignment.id == assignment.id,
                    teacher_academic_classes.c.teacher_id
                    == teacher_subjects.c.teacher_id,
                    Teacher.user_id == current_user.id,
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
    authorize_student_access(db, submission.student_id, current_user)
    authorize_assignment_access(db, submission.assignment, current_user)
