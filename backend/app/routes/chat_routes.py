from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database.dependencies import get_db
from app.services.security_service import authorize_request
from app.services.chat_service import (
    create_chat_session,
    save_message,
    get_sessions,
    get_messages
)

router = APIRouter()

# Input Validation Contracts
class SessionCreateRequest(BaseModel):
    title: string

@router.post("/chat/sessions", status_code=status.HTTP_201_CREATED)
def initialize_session(
    body: SessionCreateRequest,
    auth: dict = Depends(authorize_request),
    db: Session = Depends(get_db)
):
    """Creates a persistent session context under the active tenant's workspace."""
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
    """Retrieves chronological history titles matching the verified credentials context."""
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
    """Returns chronologically ordered messages from a specific session after checking tenant access."""
    # Fetch first message or session directly to verify tenant ownership
    messages = get_messages(db=db, session_id=session_id)
    
    # Simple verification logic: find matching parent session tracking metadata
    from app.models.chat_session import ChatSession
    session_record = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    if not session_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The specified chat thread session could not be resolved."
        )
        
    if session_record.tenant_id != auth["tenant_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: Unprivileged multi-tenant organizational space partition."
        )

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