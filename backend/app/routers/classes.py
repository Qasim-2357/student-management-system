from math import ceil

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.academic_class import ClassCreate, ClassListResponse, ClassResponse, ClassUpdate
from app.security import get_current_admin, get_current_user
from app.services.classes import (
    create_class,
    delete_class,
    get_class_or_404,
    list_classes,
    update_class,
)

router = APIRouter(prefix="/classes", tags=["Classes"])


@router.post("", response_model=ClassResponse, status_code=status.HTTP_201_CREATED)
def create_class_endpoint(
    class_data: ClassCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return create_class(db, class_data)


@router.get("", response_model=ClassListResponse)
def list_classes_endpoint(
    search: str | None = Query(default=None, min_length=1, max_length=100),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    classes, total = list_classes(
        db,
        search=search,
        page=page,
        page_size=page_size,
    )
    return ClassListResponse(
        items=classes,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total else 0,
    )


@router.get("/{class_id}", response_model=ClassResponse)
def get_class_endpoint(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_class_or_404(db, class_id)


@router.patch("/{class_id}", response_model=ClassResponse)
def update_class_endpoint(
    class_id: int,
    class_data: ClassUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return update_class(db, get_class_or_404(db, class_id), class_data)


@router.delete("/{class_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_class_endpoint(
    class_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
) -> Response:
    delete_class(db, get_class_or_404(db, class_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)