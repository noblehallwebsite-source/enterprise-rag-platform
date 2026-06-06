from sqlalchemy.orm import Session
from app.models.document import Document
from app.models.chat_session import ChatSession
from app.models.message import Message

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