from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.models import User
from app.schemas.dashboard import AdminDashboardResponse
from app.security import get_current_admin
from app.services.dashboard import get_admin_dashboard

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/admin", response_model=AdminDashboardResponse)
def get_admin_dashboard_endpoint(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin),
):
    return get_admin_dashboard(db)
