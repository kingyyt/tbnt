from typing import Optional
from pydantic import BaseModel

# Shared properties
class UserBase(BaseModel):
    username: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    phone: Optional[str] = None
    role_level: int = 5
    chat_color: Optional[str] = None # Random color for chat bubble

# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str

# Properties to return to client
class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class UserUpdate(BaseModel):
    nickname: str
    avatar: Optional[str] = None
    phone: Optional[str] = None

class PasswordUpdate(BaseModel):
    old_password: str
    new_password: str
