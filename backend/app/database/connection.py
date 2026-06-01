# app/database/connection.py
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 🔌 Grab the uniform connection string injected from your .env
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://postgres:postgres@postgres:5432/enterprise_rag"
)

# Initialize the synchronous engine matrix
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True  # 🔄 Automatically checks connection health before issuing queries
)

# Session factory for handling individual data transaction blocks
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Dependency Helper function to cleanly open/close database connections
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()