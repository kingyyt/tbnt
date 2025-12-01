from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.repository import Base

class Friendship(Base):
    __tablename__ = "friendships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    friend_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(Integer, default=0) # 0: Pending, 1: Accepted, 2: Rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    requester = relationship("User", foreign_keys=[user_id], backref="sent_requests")
    target = relationship("User", foreign_keys=[friend_id], backref="received_requests")
