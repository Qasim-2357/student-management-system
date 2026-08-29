from pydantic import BaseModel, ConfigDict, Field


class MarkCreate(BaseModel):
    exam_id: int = Field(ge=1)
    student_id: int = Field(ge=1)
    subject_id: int = Field(ge=1)
    marks: float = Field(ge=0, le=100)


class MarkUpdate(BaseModel):
    exam_id: int | None = Field(default=None, ge=1)
    student_id: int | None = Field(default=None, ge=1)
    subject_id: int | None = Field(default=None, ge=1)
    marks: float | None = Field(default=None, ge=0, le=100)


class MarkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    exam_id: int
    student_id: int
    subject_id: int
    marks: float


class MarkListResponse(BaseModel):
    items: list[MarkResponse]
    total: int
    page: int
    page_size: int
    total_pages: int