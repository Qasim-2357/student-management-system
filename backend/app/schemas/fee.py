from datetime import date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

FeeStatus = Literal["pending", "partial", "paid"]


class FeeCreate(BaseModel):
    student_id: int = Field(ge=1)
    amount: float = Field(ge=0)
    paid_amount: float = Field(default=0.0, ge=0)
    due_date: date

    @model_validator(mode="after")
    def validate_amounts(self):
        if self.paid_amount > self.amount:
            raise ValueError("paid_amount cannot be greater than amount")
        return self


class FeeUpdate(BaseModel):
    student_id: int | None = Field(default=None, ge=1)
    amount: float | None = Field(default=None, ge=0)
    paid_amount: float | None = Field(default=None, ge=0)
    due_date: date | None = None

    @model_validator(mode="after")
    def validate_amounts(self):
        if self.amount is not None and self.paid_amount is not None:
            if self.paid_amount > self.amount:
                raise ValueError("paid_amount cannot be greater than amount")
        return self


class FeeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    amount: float
    paid_amount: float
    due_amount: float
    due_date: date
    status: FeeStatus
    created_at: datetime


class FeeListResponse(BaseModel):
    items: list[FeeResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
