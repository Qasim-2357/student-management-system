from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.schemas.academic_class import ClassResponse


def _non_blank_string(value: str | None, field_name: str) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} cannot be blank")
    return cleaned


class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    roll_number: str = Field(min_length=1, max_length=50)
    email: EmailStr
    phone: str = Field(min_length=1, max_length=20)
    date_of_birth: date | None = None
    course: str = Field(min_length=1, max_length=100)
    semester: int = Field(ge=1)
    user_id: int | None = Field(default=None, ge=1)
    academic_class_id: int | None = Field(default=None, ge=1)

    @field_validator("name", "roll_number", "course", "phone", mode="before")
    @classmethod
    def trim_text_fields(cls, value: str | None, info):
        if value is None:
            return value
        return _non_blank_string(value, info.field_name)

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


class StudentUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    roll_number: str | None = Field(default=None, min_length=1, max_length=50)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, min_length=1, max_length=20)
    date_of_birth: date | None = None
    course: str | None = Field(default=None, min_length=1, max_length=100)
    semester: int | None = Field(default=None, ge=1)
    user_id: int | None = Field(default=None, ge=1)
    academic_class_id: int | None = Field(default=None, ge=1)

    @field_validator("name", "roll_number", "course", "phone", mode="before")
    @classmethod
    def trim_text_fields(cls, value: str | None, info):
        if value is None:
            return value
        return _non_blank_string(value, info.field_name)

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


class StudentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    academic_class_id: int | None
    name: str
    roll_number: str
    email: EmailStr
    phone: str
    date_of_birth: date | None
    course: str
    semester: int
    created_at: datetime


class StudentListResponse(BaseModel):
    items: list[StudentResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class StudentProfileInfo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    roll_number: str
    email: EmailStr
    phone: str
    date_of_birth: date | None
    course: str
    semester: int


class StudentProfileMark(BaseModel):
    id: int
    subject_id: int
    subject_name: str
    marks: float


class StudentProfileResponse(BaseModel):
    student: StudentProfileInfo
    academic_class: ClassResponse | None
    marks: list[StudentProfileMark]
