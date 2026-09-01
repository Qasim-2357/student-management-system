from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


def _non_blank_string(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} cannot be blank")
    return cleaned


class TeacherCreate(BaseModel):
    user_id: int = Field(ge=1)
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    phone: str = Field(min_length=1, max_length=20)

    @field_validator("name", mode="before")
    @classmethod
    def trim_name(cls, value: str | None):
        if value is None:
            return value
        return _non_blank_string(value, "name")

    @field_validator("phone", mode="before")
    @classmethod
    def trim_phone(cls, value: str | None):
        if value is None:
            return value
        return _non_blank_string(value, "phone")

    @field_validator("email", mode="before")
    @classmethod
    def trim_email(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("email cannot be blank")
        return value


class TeacherUpdate(BaseModel):
    user_id: int | None = Field(default=None, ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=1, max_length=20)

    @field_validator("name", mode="before")
    @classmethod
    def trim_name(cls, value: str | None):
        if value is None:
            return value
        return _non_blank_string(value, "name")

    @field_validator("phone", mode="before")
    @classmethod
    def trim_phone(cls, value: str | None):
        if value is None:
            return value
        return _non_blank_string(value, "phone")

    @field_validator("email", mode="before")
    @classmethod
    def trim_email(cls, value):
        if value is None:
            return None
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("email cannot be blank")
        return value


class TeacherResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    name: str
    email: EmailStr
    phone: str


class TeacherListResponse(BaseModel):
    items: list[TeacherResponse]
    total: int
    page: int
    page_size: int
    total_pages: int