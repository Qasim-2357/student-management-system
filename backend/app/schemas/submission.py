from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

SubmissionStatus = Literal["pending", "submitted", "late"]


class SubmissionCreate(BaseModel):
    student_id: int = Field(ge=1)
    submitted_at: datetime | None = None


class SubmissionUpdate(BaseModel):
    student_id: int | None = Field(default=None, ge=1)
    submitted_at: datetime | None = None


class SubmissionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    assignment_id: int
    student_id: int
    submitted_at: datetime | None
    status: SubmissionStatus


class SubmissionListResponse(BaseModel):
    items: list[SubmissionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
