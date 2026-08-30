from datetime import date
from math import ceil

from fastapi import APIRouter, Depends, Query, Response, status as http_status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.fee_receipt import FeeReceiptResponse
from app.schemas.fee import FeeCreate, FeeListResponse, FeeResponse, FeeStatus, FeeUpdate
from app.security import get_current_admin, get_current_user
from app.services.fee_receipts import generate_fee_receipt_pdf, get_fee_receipt
from app.services.fees import create_fee, delete_fee, get_fee_or_404, list_fees, update_fee

router = APIRouter(prefix="/fees", tags=["Fees"])


@router.post("", response_model=FeeResponse, status_code=http_status.HTTP_201_CREATED)
def create_fee_endpoint(
    fee_data: FeeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return create_fee(db, fee_data)


@router.get("", response_model=FeeListResponse)
def list_fees_endpoint(
    search: str | None = Query(default=None, min_length=1, max_length=100),
    student_id: int | None = Query(default=None, ge=1),
    fee_status: FeeStatus | None = Query(default=None, alias="status"),
    due_date: date | None = Query(default=None),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    fees, total = list_fees(
        db,
        search=search,
        student_id=student_id,
        status=fee_status,
        due_date=due_date,
        page=page,
        page_size=page_size,
    )
    return FeeListResponse(
        items=fees,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total else 0,
    )


@router.get("/{fee_id}/receipt", response_model=FeeReceiptResponse)
def get_fee_receipt_endpoint(
    fee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_fee_receipt(db, fee_id)


@router.get("/{fee_id}/receipt/pdf")
def get_fee_receipt_pdf_endpoint(
    fee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    pdf_content = generate_fee_receipt_pdf(db, fee_id)
    return Response(
        content=pdf_content,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="fee-receipt-{fee_id}.pdf"'
        },
    )


@router.get("/{fee_id}", response_model=FeeResponse)
def get_fee_endpoint(
    fee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_fee_or_404(db, fee_id)


@router.patch("/{fee_id}", response_model=FeeResponse)
def update_fee_endpoint(
    fee_id: int,
    fee_data: FeeUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return update_fee(db, get_fee_or_404(db, fee_id), fee_data)


@router.delete("/{fee_id}", status_code=http_status.HTTP_204_NO_CONTENT)
def delete_fee_endpoint(
    fee_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Response:
    delete_fee(db, get_fee_or_404(db, fee_id))
    return Response(status_code=http_status.HTTP_204_NO_CONTENT)
