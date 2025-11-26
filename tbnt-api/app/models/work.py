from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.repository import Base
from datetime import datetime

class WorkSettings(Base):
    __tablename__ = "work_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    start_time = Column(String, default="09:00") # Format: HH:MM
    end_time = Column(String, default="18:00")   # Format: HH:MM
    
    # Relationship
    user = relationship("User", backref="work_settings")

class WorkItem(Base):
    __tablename__ = "work_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    type = Column(String) # 'memo', 'plan', 'progress'
    content = Column(String)
    status = Column(String, default="pending") # 'pending', 'done'
    percentage = Column(Integer, default=0) # For 'progress' type
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship
    user = relationship("User", backref="work_items")
