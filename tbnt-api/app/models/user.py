from sqlalchemy import Boolean, Column, Integer, String
from app.db.repository import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    nickname = Column(String)
    avatar = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String)
    phone = Column(String, nullable=True)
    role_level = Column(Integer, default=5)
    is_active = Column(Boolean, default=True)
    chat_color = Column(String, default="#3b82f6") # Default blue, but should be random on creation
