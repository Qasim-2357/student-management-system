from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class ExamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    exam_type: str = Field(min_length=1, max_length=50)
    exam_date: date
    academic_class_id: int = Field(ge=1)


class ExamUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    exam_type: str | None = Field(default=None, min_length=1, max_length=50)
    exam_date: date | None = None
    academic_class_id: int | None = Field(default=None, ge=1)


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