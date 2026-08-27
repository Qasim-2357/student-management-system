from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.schemas.academic_class import ClassResponse


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
