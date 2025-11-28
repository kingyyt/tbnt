from typing import Optional, List
from pydantic import BaseModel
from app.api.models.user import User

class ChatMessageBase(BaseModel):
    content: str
    message_type: Optional[str] = "text"

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessage(ChatMessageBase):
    id: int
    user_id: int
    created_at: str
    message_type: str
    sender: Optional[User] = None

    class Config:
        from_attributes = True
