from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime
from app.api.models.user import User

class FriendshipBase(BaseModel):
    pass

class FriendshipCreate(FriendshipBase):
    target_number: int

class FriendshipUpdate(FriendshipBase):
    status: int

class Friendship(FriendshipBase):
    id: int
    user_id: int
    friend_id: int
    status: int
    created_at: datetime
    friend_info: Optional[User] = None

    class Config:
        from_attributes = True
