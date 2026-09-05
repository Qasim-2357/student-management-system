from typing import Any, List, Optional, Sequence, Tuple, Union
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.models import Mark, Student, Subject, Exam
from app.schemas.mark import MarkCreate, MarkUpdate


def get_mark(db: Session, mark_id: int) -> Mark:
    mark = db.query(Mark).filter(Mark.id == mark_id).first()
    if not mark:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Mark record {mark_id} not found"
        )
    return mark


get_mark_or_404 = get_mark


def list_marks(
    db: Session,
    skip: Optional[int] = None,
    limit: Optional[int] = None,
    page: Optional[int] = None,
    page_size: Optional[int] = None,
    student_id: Optional[int] = None,
    student_ids: Optional[Sequence[int]] = None,
    subject_id: Optional[int] = None,
    exam_id: Optional[int] = None,
    search: Optional[str] = None,
    **kwargs: Any,
) -> Tuple[List[Mark], int]:
    query = db.query(Mark)

    if student_id is not None:
        query = query.filter(Mark.student_id == student_id)
    elif student_ids is not None:
        query = query.filter(Mark.student_id.in_(student_ids))

    if subject_id is not None:
        query = query.filter(Mark.subject_id == subject_id)

    if exam_id is not None:
        query = query.filter(Mark.exam_id == exam_id)

    if search:
        search_term = f"%{search}%"
        query = query.join(Mark.student).join(Mark.subject)
        query = query.filter(
            or_(
                Student.name.ilike(search_term),
                Subject.code.ilike(search_term),
                Subject.name.ilike(search_term),
            )
        )

    query = query.order_by(Mark.id.asc())
    total = query.count()

    if page is not None and page_size is not None:
        calculated_skip = max(0, (page - 1) * page_size)
        items = query.offset(calculated_skip).limit(page_size).all()
    else:
        offset_val = skip if skip is not None else 0
        limit_val = limit if limit is not None else 100
        items = query.offset(offset_val).limit(limit_val).all()

    return items, total


def create_mark(db: Session, data: MarkCreate) -> Mark:
    marks_val = getattr(data, "marks", getattr(data, "marks_obtained", None))
    if marks_val is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Marks value is required"
        )
    if marks_val < 0 or marks_val > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Marks must be between 0 and 100"
        )

    if not db.query(Student).filter(Student.id == data.student_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student {data.student_id} not found"
        )
    if not db.query(Subject).filter(Subject.id == data.subject_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subject {data.subject_id} not found"
        )
    if not db.query(Exam).filter(Exam.id == data.exam_id).first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Exam {data.exam_id} not found"
        )

    existing = db.query(Mark).filter(
        Mark.student_id == data.student_id,
        Mark.subject_id == data.subject_id,
        Mark.exam_id == data.exam_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Mark record already exists for this student, subject, and exam"
        )

    mark = Mark(
        student_id=data.student_id,
        subject_id=data.subject_id,
        exam_id=data.exam_id,
        marks=marks_val,
    )
    db.add(mark)
    db.commit()
    db.refresh(mark)
    return mark


def update_mark(
    db: Session,
    mark_or_id: Union[Mark, int],
    data: MarkUpdate,
) -> Mark:
    mark = mark_or_id if isinstance(mark_or_id, Mark) else get_mark(db, mark_or_id)
    update_data = data.model_dump(exclude_unset=True)

    marks_val = update_data.get("marks", update_data.get("marks_obtained"))
    if marks_val is not None:
        if marks_val < 0 or marks_val > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Marks must be between 0 and 100"
            )
        mark.marks = marks_val

    new_student = update_data.get("student_id", mark.student_id)
    new_subject = update_data.get("subject_id", mark.subject_id)
    new_exam = update_data.get("exam_id", mark.exam_id)

    if new_student != mark.student_id and not db.query(Student).filter(Student.id == new_student).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Student {new_student} not found")
    if new_subject != mark.subject_id and not db.query(Subject).filter(Subject.id == new_subject).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Subject {new_subject} not found")
    if new_exam != mark.exam_id and not db.query(Exam).filter(Exam.id == new_exam).first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Exam {new_exam} not found")

    if new_student != mark.student_id or new_subject != mark.subject_id or new_exam != mark.exam_id:
        existing = db.query(Mark).filter(
            Mark.student_id == new_student,
            Mark.subject_id == new_subject,
            Mark.exam_id == new_exam,
            Mark.id != mark.id,
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Mark record already exists for this student, subject, and exam"
            )

    for field in ("student_id", "subject_id", "exam_id"):
        if field in update_data and update_data[field] is not None:
            setattr(mark, field, update_data[field])

    db.commit()
    db.refresh(mark)
    return mark


def delete_mark(
    db: Session,
    mark_or_id: Union[Mark, int],
) -> None:
    mark = mark_or_id if isinstance(mark_or_id, Mark) else get_mark(db, mark_or_id)
    db.delete(mark)
    db.commit()