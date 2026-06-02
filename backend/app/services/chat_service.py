from sqlalchemy.orm import Session
from uuid import UUID
from app.models.chat_session import ChatSession
from app.models.message import Message

def create_chat_session(db: Session, tenant_id: str, title: str) -> ChatSession:
    """
    Initializes a new tracking session thread for conversational history
    partitioned under a specific workspace tenant.
    """
    session = ChatSession(
        tenant_id=tenant_id,
        title=title
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def save_message(db: Session, session_id: str, role: str, content: str) -> Message:
    """
    Persists a historical interaction item safely indexed inside 
    the active session context.
    """
    message = Message(
        session_id=UUID(str(session_id)),
        role=role,
        content=content
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message

def get_sessions(db: Session, tenant_id: str) -> list[ChatSession]:
    """
    Retrieves all available conversation instances matching a tenant workspace boundary.
    """
    return (
        db.query(ChatSession)
        .filter(ChatSession.tenant_id == tenant_id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )

def get_messages(db: Session, session_id: str) -> list[Message]:
    """
    Fetches the full chronologically sorted dialog logs belonging to a unique session thread.
    """
    return (
        db.query(Message)
        .filter(Message.session_id == UUID(str(session_id)))
        .order_by(Message.created_at.asc())
        .all()
    )