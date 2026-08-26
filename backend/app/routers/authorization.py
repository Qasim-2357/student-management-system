from fastapi import APIRouter, Depends

from app.models.models import User
from app.security import (
    get_current_admin,
    get_current_student,
    get_current_teacher,
)

router = APIRouter(tags=["Authorization"])


@router.get("/admin/test")
def admin_test(current_user: User = Depends(get_current_admin)):
    return {"message": "Admin access granted"}


@router.get("/teacher/test")
def teacher_test(current_user: User = Depends(get_current_teacher)):
    return {"message": "Teacher access granted"}


@router.get("/student/test")
def student_test(current_user: User = Depends(get_current_student)):
    return {"message": "Student access granted"}
