from datetime import date
from typing import Any, List, Optional, Sequence, Tuple, Union
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.models import Attendance, Student, AcademicClass
from app.schemas.attendance import AttendanceCreate, AttendanceUpdate


def get_attendance(db: Session, attendance_id: int) -> Attendance:
    record = db.query(Attendance).filter(Attendance.id == attendance_id).first()
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Attendance record {attendance_id} not found"
        )
    return record


get_attendance_or_404 = get_attendance


def list_attendance(
    db: Session,
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    student_id: Optional[int] = None,
    student_ids: Optional[Sequence[int]] = None,
    class_id: Optional[int] = None,
    attendance_date: Optional[date] = None,
    attendance_status: Optional[str] = None,
    status: Optional[str] = None,
    **kwargs: Any,
) -> Tuple[List[Attendance], int]:
    query = db.query(Attendance)

    if student_id is not None:
        query = query.filter(Attendance.student_id == student_id)
    elif student_ids is not None:
        query = query.filter(Attendance.student_id.in_(student_ids))

    if class_id is not None:
        query = query.filter(Attendance.class_id == class_id)

    if attendance_date is not None:
        query = query.filter(Attendance.attendance_date == attendance_date)

    effective_status = attendance_status or status
    if effective_status is not None:
        query = query.filter(Attendance.status == effective_status)

    query = query.order_by(Attendance.attendance_date.desc(), Attendance.id.desc())
    total = query.count()

    if page is not None and page_size is not None:
        calculated_skip = max(0, (page - 1) * page_size)
        items = query.offset(calculated_skip).limit(page_size).all()
    else:
        offset_val = skip if skip is not None else 0
        limit_val = limit if limit is not None else 100
        items = query.offset(offset_val).limit(limit_val).all()

    return items, total


def create_attendance(db: Session, data: AttendanceCreate) -> Attendance:
    student = db.query(Student).filter(Student.id == data.student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student {data.student_id} not found"
        )

    class_id = data.class_id or getattr(student, "class_id", None)
    if class_id:
        cls = db.query(AcademicClass).filter(AcademicClass.id == class_id).first()
        if not cls:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Class {class_id} not found"
            )

    existing = db.query(Attendance).filter(
        Attendance.student_id == data.student_id,
        Attendance.attendance_date == data.attendance_date
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Attendance record already exists for this student on this date"
        )

    attendance = Attendance(
        student_id=data.student_id,
        class_id=class_id,
        attendance_date=data.attendance_date,
        status=data.status,
        remarks=getattr(data, "remarks", None),
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


def update_attendance(
    db: Session,
    attendance_or_id: Union[Attendance, int],
    data: AttendanceUpdate,
) -> Attendance:
    record = attendance_or_id if isinstance(attendance_or_id, Attendance) else get_attendance(db, attendance_or_id)
    update_data = data.model_dump(exclude_unset=True)

    new_date = update_data.get("attendance_date", record.attendance_date)
    new_student_id = update_data.get("student_id", record.student_id)

    if new_date != record.attendance_date or new_student_id != record.student_id:
        existing = db.query(Attendance).filter(
            Attendance.student_id == new_student_id,
            Attendance.attendance_date == new_date,
            Attendance.id != record.id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Attendance record already exists for this student on this date"
            )

    for field, val in update_data.items():
        setattr(record, field, val)

    db.commit()
    db.refresh(record)
    return record


def delete_attendance(
    db: Session,
    attendance_or_id: Union[Attendance, int],
) -> None:
    record = attendance_or_id if isinstance(attendance_or_id, Attendance) else get_attendance(db, attendance_or_id)
    db.delete(record)
    db.commit()


def calculate_student_attendance_percentage(db: Session, student_id: int) -> dict:
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student {student_id} not found"
        )

    total_records = db.query(func.count(Attendance.id)).filter(
        Attendance.student_id == student_id
    ).scalar() or 0

    if total_records == 0:
        return {
            "student_id": student_id,
            "total_days": 0,
            "present_days": 0,
            "absent_days": 0,
            "percentage": 0.0
        }

    present_days = db.query(func.count(Attendance.id)).filter(
        Attendance.student_id == student_id,
        Attendance.status == "PRESENT"
    ).scalar() or 0

    absent_days = total_records - present_days
    pct = round((present_days / total_records) * 100.0, 2)

    return {
        "student_id": student_id,
        "total_days": total_records,
        "present_days": present_days,
        "absent_days": absent_days,
        "percentage": pct
    }