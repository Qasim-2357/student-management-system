from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

AttendanceStatus = Literal["present", "absent"]


class AttendanceCreate(BaseModel):
    student_id: int = Field(ge=1)
    attendance_date: date
    status: AttendanceStatus


class AttendanceUpdate(BaseModel):
    attendance_date: date | None = None
    status: AttendanceStatus | None = None


class AttendanceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    attendance_date: date
    status: AttendanceStatus


class AttendanceListResponse(BaseModel):
    items: list[AttendanceResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
