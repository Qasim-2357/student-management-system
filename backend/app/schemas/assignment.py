from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _normalize_optional_text(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} cannot be blank")
    return cleaned


class AssignmentCreate(BaseModel):
    title: str = Field(min_length=1)
    description: str | None = None
    subject_id: int = Field(ge=1)
    academic_class_id: int = Field(ge=1)
    due_date: date

    @field_validator("title", mode="before")
    @classmethod
    def trim_title(cls, value):
        if value is None:
            return value
        return _normalize_optional_text(value, "title")

    @field_validator("description", mode="before")
    @classmethod
    def trim_description(cls, value):
        if value is None:
            return value
        return _normalize_optional_text(value, "description")


class AssignmentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1)
    description: str | None = None
    subject_id: int | None = Field(default=None, ge=1)
    academic_class_id: int | None = Field(default=None, ge=1)
    due_date: date | None = None

    @field_validator("title", mode="before")
    @classmethod
    def trim_title(cls, value):
        if value is None:
            return value
        return _normalize_optional_text(value, "title")

    @field_validator("description", mode="before")
    @classmethod
    def trim_description(cls, value):
        if value is None:
            return value
        return _normalize_optional_text(value, "description")


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
