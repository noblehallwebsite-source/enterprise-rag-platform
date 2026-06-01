# app/database/dependencies.py
from app.database.connection import SessionLocal

def get_db():
    """
    FastAPI Yield Dependency worker.
    Creates a standalone transactional database block per request, 
    ensuring safe socket recycling under intense load conditions.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()