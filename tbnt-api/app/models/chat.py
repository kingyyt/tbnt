from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.repository import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)
    message_type = Column(String, default="text") # text, image
    created_at = Column(String) # Format: YYYY-MM-DD HH:MM:SS

    sender = relationship("User", backref="messages")
