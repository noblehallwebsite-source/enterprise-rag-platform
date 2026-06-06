from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.chat_session import ChatSession
from app.models.message import Message

from app.services.metrics_service import (
    rag_requests_total,
    rag_failures_total,
    rag_latency_seconds,
    retrieved_documents_total
)

def get_tenant_dashboard_metrics(db: Session, tenant_id: str) -> dict:
    """
    Executes precise structural counts across core system relational entities
    scoped entirely to a single tenant partition boundary.
    """
    
    # 1. Total documents processed and indexed for the tenant
    document_count = (
        db.query(Document)
        .filter(Document.tenant_id == tenant_id)
        .count()
    )

    # 2. Total active conversational thread frameworks allocated
    session_count = (
        db.query(ChatSession)
        .filter(ChatSession.tenant_id == tenant_id)
        .count()
    )

    # 3. Total message blocks generated across all tenant sessions
    # 🚀 Fixed: Updated the join clause to match the schema's 'session_id' attribute
    message_count = (
        db.query(Message)
        .join(ChatSession, Message.session_id == ChatSession.id)
        .filter(ChatSession.tenant_id == tenant_id)
        .count()
    )

    return {
        "documents": document_count,
        "chat_sessions": session_count,
        "messages": message_count,
        "tenants": 1  # Standard baseline constant for single-tenant isolation view
    }


def get_tenant_dashboard_metrics(db: Session, tenant_id: str) -> dict:
    # 1. Existing Relational Database Counts (Kept exactly as is)
    document_count = db.query(Document).filter(Document.tenant_id == tenant_id).count()
    session_count = db.query(ChatSession).filter(ChatSession.tenant_id == tenant_id).count()
    message_count = db.query(Message).join(ChatSession, Message.session_id == ChatSession.id).filter(ChatSession.tenant_id == tenant_id).count()

    # 2. Extract Prometheus Counter Values
    total_requests = rag_requests_total._value.get()
    total_failures = rag_failures_total._value.get()
    
    success_rate = 100.0
    if total_requests > 0:
        success_rate = round(((total_requests - total_failures) / total_requests) * 100, 1)

    # 3. 🚀 Fixed: Correctly extract Histogram Sum and Count
    # Prometheus Histograms store live runtime metrics inside the multi-wrapper local_value array
    try:
        # Index 0 gets the running sum, Index 1 gets the total item count
        latency_sum = rag_latency_seconds.local_value[0]
        latency_count = rag_latency_seconds.local_value[1]
        avg_latency = round(latency_sum / latency_count, 2) if latency_count > 0 else 0.0
    except (AttributeError, IndexError, TypeError):
        avg_latency = 0.0

    return {
        "documents": document_count,
        "chat_sessions": session_count,
        "messages": message_count,
        "tenants": 1,
        "success_rate": success_rate,
        "avg_latency": avg_latency,
        "total_requests": int(total_requests)
    }