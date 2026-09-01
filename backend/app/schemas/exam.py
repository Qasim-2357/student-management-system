from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


def _non_blank_string(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} cannot be blank")
    return cleaned


class ExamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    exam_type: str = Field(min_length=1, max_length=50)
    exam_date: date
    academic_class_id: int = Field(ge=1)

    @field_validator("name", "exam_type", mode="before")
    @classmethod
    def trim_text_fields(cls, value: str | None, info):
        if value is None:
            return value
        return _non_blank_string(value, info.field_name)


class ExamUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    exam_type: str | None = Field(default=None, min_length=1, max_length=50)
    exam_date: date | None = None
    academic_class_id: int | None = Field(default=None, ge=1)

    @field_validator("name", "exam_type", mode="before")
    @classmethod
    def trim_text_fields(cls, value: str | None, info):
        if value is None:
            return value
        return _non_blank_string(value, info.field_name)


class ExamResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    exam_type: str
    exam_date: date
    academic_class_id: int


class ExamListResponse(BaseModel):
    items: list[ExamResponse]
    total: int
    page: int
    page_size: int
    total_pages: int