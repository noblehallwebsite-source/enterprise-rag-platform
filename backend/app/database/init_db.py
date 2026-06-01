# app/database/init_db.py
from app.database.connection import engine
from app.database.base import Base

# ⚠️ CRUCIAL: We must explicitly import our models here. 
# If SQLAlchemy doesn't see the Document model imported, it won't know the table exists!
from app.models.document import Document

def init_database():
    print("Connecting to PostgreSQL network mesh...")
    
    # 🚀 This line inspects 'Base', finds all attached tables, and creates them if they don't exist yet
    Base.metadata.create_all(bind=engine)
    
    print("Database initialized successfully! 'documents' table is now live.")

if __name__ == "__main__":
    init_database()