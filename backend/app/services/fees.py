from fastapi import HTTPException, status
from sqlalchemy import and_, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.models import Fee, Student
from app.schemas.fee import FeeCreate, FeeUpdate


def get_fee_or_404(db: Session, fee_id: int) -> Fee:
    fee = db.get(Fee, fee_id)
    if fee is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Fee with id {fee_id} was not found",
        )
    return fee


def _ensure_student_exists(db: Session, student_id: int) -> None:
    if db.get(Student, student_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} was not found",
        )


def _validate_payment_amounts(amount: float, paid_amount: float) -> None:
    if amount < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="amount must be greater than or equal to 0",
        )
    if paid_amount < 0:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="paid_amount must be greater than or equal to 0",
        )
    if paid_amount > amount:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="paid_amount cannot be greater than amount",
        )


def create_fee(db: Session, fee_data: FeeCreate) -> Fee:
    _ensure_student_exists(db, fee_data.student_id)
    _validate_payment_amounts(fee_data.amount, fee_data.paid_amount)

    fee = Fee(**fee_data.model_dump())
    db.add(fee)
    _commit_or_raise_conflict(db)
    db.refresh(fee)
    return fee


def update_fee(
    db: Session,
    fee: Fee,
    fee_data: FeeUpdate,
) -> Fee:
    changes = fee_data.model_dump(exclude_unset=True)

    if "student_id" in changes:
        _ensure_student_exists(db, changes["student_id"])

    if "amount" in changes or "paid_amount" in changes:
        new_amount = changes.get("amount", fee.amount)
        new_paid_amount = changes.get("paid_amount", fee.paid_amount)
        _validate_payment_amounts(new_amount, new_paid_amount)

    for field, value in changes.items():
        setattr(fee, field, value)

    _commit_or_raise_conflict(db)
    db.refresh(fee)
    return fee


def delete_fee(db: Session, fee: Fee) -> None:
    db.delete(fee)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Fee cannot be deleted while related records exist",
        ) from None


def list_fees(
    db: Session,
    *,
    search: str | None,
    student_id: int | None,
    status: str | None,
    due_date: object | None,
    page: int,
    page_size: int,
    student_ids: list[int] | None = None,
) -> tuple[list[Fee], int]:
    filters = []
    if student_ids is not None:
        filters.append(Fee.student_id.in_(student_ids))
    if student_id is not None:
        filters.append(Fee.student_id == student_id)
    if due_date is not None:
        filters.append(Fee.due_date == due_date)
    if status is not None:
        if status == "pending":
            filters.append(Fee.paid_amount == 0)
        elif status == "partial":
            filters.append(and_(Fee.paid_amount > 0, Fee.paid_amount < Fee.amount))
        elif status == "paid":
            filters.append(Fee.paid_amount == Fee.amount)

    base_query = select(Fee)
    count_query = select(func.count()).select_from(Fee)

    if search:
        pattern = f"%{search.strip()}%"
        base_query = base_query.join(Student, Fee.student_id == Student.id)
        count_query = count_query.join(Student, Fee.student_id == Student.id)
        filters.append(or_(Student.name.ilike(pattern), Student.roll_number.ilike(pattern)))

    total = db.scalar(count_query.where(*filters)) or 0
    fees = db.scalars(
        base_query
        .where(*filters)
        .order_by(Fee.due_date.asc(), Fee.id.asc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    ).all()
    return fees, total


def _commit_or_raise_conflict(db: Session) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Fee data conflicts with an existing record",
        ) from None
