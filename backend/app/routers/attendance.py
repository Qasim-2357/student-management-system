from datetime import date
from math import ceil

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.attendance import (
    AttendanceCreate,
    AttendanceListResponse,
    AttendanceResponse,
    AttendanceStatus,
    AttendanceUpdate,
)
from app.security import get_current_admin, get_current_user
from app.services.attendance import (
    create_attendance,
    delete_attendance,
    get_attendance_or_404,
    list_attendance,
    update_attendance,
)
from app.services.student_authorization import (
    authorize_attendance_access,
    authorize_student_access,
    authorized_student_ids,
)

router = APIRouter(prefix="/attendance", tags=["Attendance"])


@router.post("", response_model=AttendanceResponse, status_code=status.HTTP_201_CREATED)
def create_attendance_endpoint(
    attendance_data: AttendanceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return create_attendance(db, attendance_data)


@router.get("", response_model=AttendanceListResponse)
def list_attendance_endpoint(
    student_id: int | None = Query(default=None, ge=1),
    attendance_date: date | None = Query(default=None),
    attendance_status: AttendanceStatus | None = Query(default=None, alias="status"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    scoped_student_ids = authorized_student_ids(db, current_user)
    if student_id is not None:
        authorize_student_access(db, student_id, current_user)
        scoped_student_ids = [student_id]
    records, total = list_attendance(
        db,
        student_id=student_id,
        attendance_date=attendance_date,
        attendance_status=attendance_status,
        page=page,
        page_size=page_size,
        student_ids=scoped_student_ids,
    )
    return AttendanceListResponse(
        items=records,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total else 0,
    )


@router.get("/{attendance_id}", response_model=AttendanceResponse)
def get_attendance_endpoint(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    attendance = get_attendance_or_404(db, attendance_id)
    authorize_attendance_access(db, attendance, current_user)
    return attendance


@router.patch("/{attendance_id}", response_model=AttendanceResponse)
def update_attendance_endpoint(
    attendance_id: int,
    attendance_data: AttendanceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return update_attendance(
        db,
        get_attendance_or_404(db, attendance_id),
        attendance_data,
    )


@router.delete("/{attendance_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_attendance_endpoint(
    attendance_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Response:
    delete_attendance(db, get_attendance_or_404(db, attendance_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
