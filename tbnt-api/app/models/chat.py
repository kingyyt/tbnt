from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.db.repository import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    content = Column(String)
    message_type = Column(String, default="text") # text, image
    created_at = Column(String) # Format: YYYY-MM-DD HH:MM:SS
    
    # For private chat
    to_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    is_read = Column(Boolean, default=False)

    sender = relationship("User", foreign_keys=[user_id], backref="sent_messages")
    receiver = relationship("User", foreign_keys=[to_user_id], backref="received_messages")
