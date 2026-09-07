from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import AcademicClass, Subject, Teacher
from app.schemas.relationships import (
    ClassSubjectsResponse,
    RelationshipIds,
    TeacherRelationshipsResponse,
)
from app.security import get_current_admin

router = APIRouter(prefix="/relationships", tags=["Relationships"])


def _get_records(db: Session, model, ids: list[int], label: str):
    records = db.query(model).filter(model.id.in_(ids)).all() if ids else []
    if len(records) != len(set(ids)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=f"One or more {label} IDs are invalid",
        )
    return records


@router.get("/teachers/{teacher_id}", response_model=TeacherRelationshipsResponse)
def get_teacher_relationships(
    teacher_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    teacher = db.get(Teacher, teacher_id)
    if teacher is None:
        raise HTTPException(status_code=404, detail=f"Teacher with id {teacher_id} was not found")
    return TeacherRelationshipsResponse(
        teacher_id=teacher.id,
        class_ids=[item.id for item in teacher.academic_classes],
        subject_ids=[item.id for item in teacher.subjects],
    )


@router.put("/teachers/{teacher_id}", response_model=TeacherRelationshipsResponse)
def update_teacher_relationships(
    teacher_id: int,
    data: TeacherRelationshipsResponse,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    teacher = db.get(Teacher, teacher_id)
    if teacher is None:
        raise HTTPException(status_code=404, detail=f"Teacher with id {teacher_id} was not found")
    if data.teacher_id != teacher_id:
        raise HTTPException(status_code=422, detail="teacher_id does not match the route")
    teacher.academic_classes = _get_records(db, AcademicClass, data.class_ids, "class")
    teacher.subjects = _get_records(db, Subject, data.subject_ids, "subject")
    db.commit()
    db.refresh(teacher)
    return get_teacher_relationships(teacher_id, db, current_user)


@router.get("/classes/{class_id}/subjects", response_model=ClassSubjectsResponse)
def get_class_subjects(
    class_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    academic_class = db.get(AcademicClass, class_id)
    if academic_class is None:
        raise HTTPException(status_code=404, detail=f"Class with id {class_id} was not found")
    return ClassSubjectsResponse(class_id=class_id, subject_ids=[item.id for item in academic_class.subjects])


@router.put("/classes/{class_id}/subjects", response_model=ClassSubjectsResponse)
def update_class_subjects(
    class_id: int,
    data: RelationshipIds,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin),
):
    academic_class = db.get(AcademicClass, class_id)
    if academic_class is None:
        raise HTTPException(status_code=404, detail=f"Class with id {class_id} was not found")
    academic_class.subjects = _get_records(db, Subject, data.ids, "subject")
    db.commit()
    return ClassSubjectsResponse(class_id=class_id, subject_ids=[item.id for item in academic_class.subjects])
