from pydantic import BaseModel, ConfigDict, Field


class ClassCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    code: str = Field(min_length=1, max_length=50)
    course: str = Field(min_length=1, max_length=100)
    semester: int = Field(ge=1)


class ClassUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    code: str | None = Field(default=None, min_length=1, max_length=50)
    course: str | None = Field(default=None, min_length=1, max_length=100)
    semester: int | None = Field(default=None, ge=1)


class ClassResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    code: str
    course: str
    semester: int


class ClassListResponse(BaseModel):
    items: list[ClassResponse]
    total: int
    page: int
    page_size: int
    total_pages: int