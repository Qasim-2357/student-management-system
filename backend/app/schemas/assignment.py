from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class AssignmentCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None
    subject_id: int = Field(ge=1)
    academic_class_id: int = Field(ge=1)
    due_date: date


class AssignmentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    description: str | None = None
    subject_id: int | None = Field(default=None, ge=1)
    academic_class_id: int | None = Field(default=None, ge=1)
    due_date: date | None = None


class AssignmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    subject_id: int
    academic_class_id: int
    due_date: date
    created_at: datetime


class AssignmentListResponse(BaseModel):
    items: list[AssignmentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
