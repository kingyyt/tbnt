from typing import Optional, List
from pydantic import BaseModel
from app.api.models.user import User

class ChatMessageBase(BaseModel):
    content: str

class ChatMessageCreate(ChatMessageBase):
    pass

class ChatMessage(ChatMessageBase):
    id: int
    user_id: int
    created_at: str
    sender: Optional[User] = None

    class Config:
        from_attributes = True
