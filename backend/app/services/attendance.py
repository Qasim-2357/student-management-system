from datetime import date

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.models import Attendance, Student
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate


def get_attendance_or_404(db: Session, attendance_id: int) -> Attendance:
    attendance = db.get(Attendance, attendance_id)
    if attendance is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance with id {attendance_id} was not found",
        )
    return attendance


def _ensure_student_exists(db: Session, student_id: int) -> None:
    if db.get(Student, student_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} was not found",
        )


def _ensure_attendance_available(
    db: Session,
    student_id: int,
    attendance_date: date,
    attendance_id: int | None = None,
) -> None:
    statement = select(Attendance.id).where(
        Attendance.student_id == student_id,
        Attendance.attendance_date == attendance_date,
    )
    if attendance_id is not None:
        statement = statement.where(Attendance.id != attendance_id)
    if db.scalar(statement) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Attendance for this student and date already exists",
        )


def create_attendance(db: Session, attendance_data: AttendanceCreate) -> Attendance:
    _ensure_student_exists(db, attendance_data.student_id)
    _ensure_attendance_available(
        db,
        attendance_data.student_id,
        attendance_data.attendance_date,
    )
    attendance = Attendance(**attendance_data.model_dump())
    db.add(attendance)
    _commit_or_raise_conflict(db)
    db.refresh(attendance)
    return attendance


def update_attendance(
    db: Session,
    attendance: Attendance,
    attendance_data: AttendanceUpdate,
) -> Attendance:
    changes = attendance_data.model_dump(exclude_unset=True)
    next_date = changes.get("attendance_date", attendance.attendance_date)
    if "attendance_date" in changes:
        _ensure_attendance_available(
            db,
            attendance.student_id,
            next_date,
            attendance.id,
        )

    for field, value in changes.items():
        setattr(attendance, field, value)

    _commit_or_raise_conflict(db)
    db.refresh(attendance)
    return attendance


def delete_attendance(db: Session, attendance: Attendance) -> None:
    db.delete(attendance)
    db.commit()


def list_attendance(
    db: Session,
    *,
    student_id: int | None,
    attendance_date: date | None,
    attendance_status: str | None,
    page: int,
    page_size: int,
) -> tuple[list[Attendance], int]:
    filters = []
    if student_id is not None:
        filters.append(Attendance.student_id == student_id)
    if attendance_date is not None:
        filters.append(Attendance.attendance_date == attendance_date)
    if attendance_status is not None:
        filters.append(Attendance.status == attendance_status)

    total = db.scalar(select(func.count()).select_from(Attendance).where(*filters)) or 0
    records = db.scalars(
        select(Attendance)
        .where(*filters)
        .order_by(Attendance.attendance_date.desc(), Attendance.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return records, total


def _commit_or_raise_conflict(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Attendance data conflicts with an existing record",
        ) from None
