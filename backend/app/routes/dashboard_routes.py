# app/routes/dashboard_routes.py
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

# 🔌 Fixed: Points directly to your exact database dependencies module
from app.database.dependencies import get_db  

router = APIRouter(prefix="/dashboard", tags=["Dashboard Metrics"])

# 🏢 Lightweight Tenant Resolution Helper
def get_current_tenant() -> str:
    """
    Temporary or static dependency to provide tenant context.
    Can be upgraded later to parse JWTs or headers like X-Tenant-ID.
    """
    return "company-a"

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
    # Lazy-loaded inline import to completely prevent any circular import issues
    from app.services.dashboard_service import get_tenant_dashboard_metrics
    
    return get_tenant_dashboard_metrics(db=db, tenant_id=tenant_id)