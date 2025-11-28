from typing import List, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta

from app.db.repository import get_db
from app.api import deps
from app.models.chat import ChatMessage
from app.models.user import User
from app.schemas.chat import ChatMessage as ChatMessageSchema, ChatMessageCreate
from app.core import security

router = APIRouter()

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

manager = ConnectionManager()

@router.get("/history", response_model=List[ChatMessageSchema])
def get_chat_history(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get chat history.
    """
    messages = db.query(ChatMessage).order_by(ChatMessage.id.desc()).offset(skip).limit(limit).all()
    # Reverse to show oldest first in UI if needed, but usually frontend handles it. 
    # Returning descending order (newest first) is good for pagination, 
    # but for chat we usually want to load "latest 50" and show them bottom-up.
    return messages[::-1] # Return in chronological order

@router.websocket("/ws/{token}")
async def websocket_endpoint(websocket: WebSocket, token: str, db: Session = Depends(get_db)):
    # Verify token
    try:
        payload = security.verify_token(token)
        username = payload.sub
        if username is None:
            await websocket.close(code=1008)
            return
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            await websocket.close(code=1008)
            return
            
        # Ensure user has a chat color
        if not user.chat_color:
            import random
            user.chat_color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
            db.commit()
            
    except Exception:
        await websocket.close(code=1008)
        return

    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            
            # Save message
            china_tz = timezone(timedelta(hours=8))
            now = datetime.now(china_tz)
            now_str = now.strftime("%Y-%m-%d %H:%M:%S")
            
            message = ChatMessage(
                user_id=user.id,
                content=data,
                created_at=now_str
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            
            # Prepare response with user info
            response = {
                "id": message.id,
                "content": message.content,
                "created_at": message.created_at,
                "user_id": user.id,
                "sender": {
                    "id": user.id,
                    "username": user.username,
                    "nickname": user.nickname,
                    "avatar": user.avatar,
                    "chat_color": user.chat_color
                }
            }
            
            await manager.broadcast(response)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
