from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from uuid import UUID

from app.database.dependencies import get_db
from app.services.security_service import authorize_request
from app.services.chat_service import (
    create_chat_session,
    get_sessions,
    get_messages
)
from app.models.chat_session import ChatSession

router = APIRouter()

# =====================================================================
# PYDANTIC VALIDATION SCHEMAS
# =====================================================================
class SessionCreateRequest(BaseModel):
    title: str

class SessionUpdateRequest(BaseModel):
    title: str


# =====================================================================
# CHAT SESSION ROUTE ENDPOINTS
# =====================================================================

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
    # Verify existence and multi-tenant isolation context matching
    session_record = db.query(ChatSession).filter(ChatSession.id == UUID(str(session_id))).first()
    
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


@router.patch("/chat/sessions/{session_id}", status_code=status.HTTP_200_OK)
def update_session_title(
    session_id: str,
    body: SessionUpdateRequest,
    auth: dict = Depends(authorize_request),
    db: Session = Depends(get_db)
):
    """
    Modifies the title attribute of an active session tracking thread.
    Enforces cross-tenant tenant verification.
    """
    session_record = db.query(ChatSession).filter(ChatSession.id == UUID(str(session_id))).first()

    if not session_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The target chat session thread entity context not found."
        )

    if session_record.tenant_id != auth["tenant_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: The security credentials provided are not authorized to modify this tenant workspace."
        )

    # Apply modification patch
    session_record.title = body.title.strip()
    db.commit()
    db.refresh(session_record)

    return {
        "id": str(session_record.id),
        "title": session_record.title,
        "created_at": session_record.created_at
    }


@router.delete("/chat/sessions/{session_id}", status_code=status.HTTP_200_OK)
def delete_session(
    session_id: str,
    auth: dict = Depends(authorize_request),
    db: Session = Depends(get_db)
):
    """
    Issues a hard deletion signal to drop a workspace session tracking record.
    Cascades into linked history message tables automatically.
    """
    session_record = db.query(ChatSession).filter(ChatSession.id == UUID(str(session_id))).first()

    if not session_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The target chat session thread entity context not found."
        )

    if session_record.tenant_id != auth["tenant_id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access Denied: The security credentials provided are not authorized to drop this tenant entity."
        )

    db.delete(session_record)
    db.commit()

    return {
        "status": "SUCCESS",
        "detail": f"Session thread row {session_id} and cascading histories purged cleanly."
    }