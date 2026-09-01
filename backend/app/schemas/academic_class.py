from pydantic import BaseModel, ConfigDict, Field, field_validator


def _non_blank_string(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} cannot be blank")
    return cleaned


class ClassCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    code: str = Field(min_length=1, max_length=50)
    course: str = Field(min_length=1, max_length=100)
    semester: int = Field(ge=1)

    @field_validator("name", "code", "course", mode="before")
    @classmethod
    def trim_text_fields(cls, value: str | None, info):
        if value is None:
            return value
        return _non_blank_string(value, info.field_name)


class ClassUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    code: str | None = Field(default=None, min_length=1, max_length=50)
    course: str | None = Field(default=None, min_length=1, max_length=100)
    semester: int | None = Field(default=None, ge=1)

    @field_validator("name", "code", "course", mode="before")
    @classmethod
    def trim_text_fields(cls, value: str | None, info):
        if value is None:
            return value
        return _non_blank_string(value, info.field_name)


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