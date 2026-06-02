# # app/database/init_db.py
# from app.database.connection import engine
# from app.database.base import Base

# # ⚠️ CRUCIAL: We must explicitly import our models here. 
# # If SQLAlchemy doesn't see the Document model imported, it won't know the table exists!
# from app.models.document import Document

# def init_database():
#     print("Connecting to PostgreSQL network mesh...")
    
#     # 🚀 This line inspects 'Base', finds all attached tables, and creates them if they don't exist yet
#     Base.metadata.create_all(bind=engine)
    
#     print("Database initialized successfully! 'documents' table is now live.")

# if __name__ == "__main__":
#     init_database()



# app/database/init_db.py
from app.database.connection import engine
from app.database.base import Base

# ⚠️ CRUCIAL: We must explicitly import all of our models here. 
# If SQLAlchemy doesn't see these models imported before metadata compilation, 
# it won't discover the data structures and won't generate the tables!
from app.models.document import Document
from app.models.chat_session import ChatSession
from app.models.message import Message

def init_database():
    print("Connecting to PostgreSQL network mesh...")
    
    # 🚀 This line inspects 'Base', finds all attached model tables, 
    # and generates them inside your Postgres cluster database if they do not exist yet.
    Base.metadata.create_all(bind=engine)
    
    print("Database initialized successfully! 'documents', 'chat_sessions', and 'messages' tables are now live.")

if __name__ == "__main__":
    init_database()

