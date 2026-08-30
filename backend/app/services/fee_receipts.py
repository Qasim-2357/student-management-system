from sqlalchemy.orm import Session

from app.models.models import Fee
from app.schemas.academic_class import ClassResponse
from app.schemas.fee import FeeResponse
from app.schemas.fee_receipt import FeeReceiptResponse
from app.schemas.fee_receipt import FeeReceiptStudent
from app.services.fees import get_fee_or_404


def get_fee_receipt(db: Session, fee_id: int) -> FeeReceiptResponse:
    fee = get_fee_or_404(db, fee_id)
    student = fee.student

    return FeeReceiptResponse(
        fee=FeeResponse.model_validate(fee),
        student=FeeReceiptStudent.model_validate(student),
        academic_class=(
            ClassResponse.model_validate(student.academic_class)
            if student.academic_class is not None
            else None
        ),
    )
