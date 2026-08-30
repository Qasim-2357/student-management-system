from io import BytesIO

from reportlab.lib import colors
from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Spacer, Table, TableStyle, Paragraph
from sqlalchemy.orm import Session

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


def generate_fee_receipt_pdf(db: Session, fee_id: int) -> bytes:
    receipt = get_fee_receipt(db, fee_id)
    output = BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=LETTER,
        pageCompression=0,
        rightMargin=0.7 * inch,
        leftMargin=0.7 * inch,
        topMargin=0.6 * inch,
        bottomMargin=0.6 * inch,
    )
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Fee Receipt", styles["Title"]),
        Spacer(1, 0.2 * inch),
    ]

    class_name = (
        f"{receipt.academic_class.name} ({receipt.academic_class.code})"
        if receipt.academic_class is not None
        else "Not assigned"
    )
    rows = [
        ["Receipt / Fee ID", str(receipt.fee.id)],
        ["Student Name", receipt.student.name],
        ["Roll Number", receipt.student.roll_number],
        ["Email", receipt.student.email],
        ["Phone", receipt.student.phone],
        ["Course", receipt.student.course],
        ["Semester", str(receipt.student.semester)],
        ["Academic Class", class_name],
        ["Fee Amount", f"{receipt.fee.amount:.2f}"],
        ["Paid Amount", f"{receipt.fee.paid_amount:.2f}"],
        ["Due Amount", f"{receipt.fee.due_amount:.2f}"],
        ["Status", receipt.fee.status],
        ["Due Date", receipt.fee.due_date.isoformat()],
        ["Created Date", receipt.fee.created_at.isoformat()],
    ]
    table = Table(rows, colWidths=[1.7 * inch, 4.8 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#EAF0F6")),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("PADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.append(table)
    document.build(story)
    return output.getvalue()
