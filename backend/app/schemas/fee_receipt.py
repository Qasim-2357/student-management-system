from pydantic import BaseModel, ConfigDict, EmailStr

from app.schemas.academic_class import ClassResponse
from app.schemas.fee import FeeResponse


class FeeReceiptStudent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    roll_number: str
    email: EmailStr
    phone: str
    course: str
    semester: int


class FeeReceiptResponse(BaseModel):
    fee: FeeResponse
    student: FeeReceiptStudent
    academic_class: ClassResponse | None
