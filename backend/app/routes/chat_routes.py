from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.dependencies import get_db
from app.services.security_service import authorize_request
from app.services.chat_service import (
    create_chat_session,
    get_sessions,
    get_messages
)

router = APIRouter()

# Simple request validation block for payload mapping
class SessionCreateRequest(BaseModel):
    title: str

@router.post("/chat/sessions", status_code=status.HTTP_201_CREATED)
def initialize_session(
    body: SessionCreateRequest,
    auth: dict = Depends(authorize_request),
    db: Session = Depends(get_db)
):
    """
    Spawns a persistent conversation thread assigned to the authenticated workspace context.
    """
    session = create_chat_session(
        db=db,
        tenant_id=auth["tenant_id"],
        title=body.title
    )
    return {
        "id": str(session.id),
        "title": session.title,
        "created_at": session.created_at
    }

@router.get("/chat/sessions", status_code=status.HTTP_200_OK)
def list_sessions(
    auth: dict = Depends(authorize_request),
    db: Session = Depends(get_db)
):
    """
    Lists historical session summaries available inside the isolated organization scope.
    """
    sessions = get_sessions(db=db, tenant_id=auth["tenant_id"])
    return [
        {
            "id": str(s.id),
            "title": s.title,
            "created_at": s.created_at
        } for s in sessions
    ]

@router.get("/chat/sessions/{session_id}", status_code=status.HTTP_200_OK)
def session_messages(
    session_id: str,
    auth: dict = Depends(authorize_request),
    db: Session = Depends(get_db)
):
    """
    Fetches the historical message ledger tracking entries for a requested thread ID.
    Enforces cross-tenant protection checks.
    """
    from app.models.chat_session import ChatSession
    
    # Verify existence and multi-tenant isolation context matching
    session_record = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    if not session_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested chat session thread could not be located."
        )
        
    if session_record.tenant_id != auth["tenant_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: The security credentials provided are restricted from accessing this session data."
        )

    messages = get_messages(db=db, session_id=session_id)
    return {
        "session_id": session_id,
        "messages": [
            {
                "role": m.role,
                "content": m.content,
                "created_at": m.created_at
            } for m in messages
        ]
    }