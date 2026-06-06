from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.dependencies import get_db, get_current_tenant
from app.services.dashboard_service import get_tenant_dashboard_metrics

router = APIRouter(prefix="/dashboard", tags=["Dashboard Metrics"])

class DashboardStatsResponse(BaseModel):
    documents: int
    chat_sessions: int
    messages: int
    tenants: int

@router.get("/stats", response_model=DashboardStatsResponse)
def read_dashboard_stats(
    db: Session = Depends(get_db),
    tenant_id: str = Depends(get_current_tenant)
):
    # Pure delegation to our new standalone dashboard service layer
    return get_tenant_dashboard_metrics(db=db, tenant_id=tenant_id)