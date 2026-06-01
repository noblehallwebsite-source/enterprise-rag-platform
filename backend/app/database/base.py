# app/database/base.py
from sqlalchemy.orm import declarative_base

# The baseline model registry that maps Python classes directly to SQL tables
Base = declarative_base()