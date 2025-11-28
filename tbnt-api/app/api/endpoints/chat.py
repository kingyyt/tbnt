from typing import List, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
import shutil
import os
import uuid
import json

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

@router.post("/upload", response_model=dict)
def upload_chat_image(
    file: UploadFile = File(...),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Upload an image for chat.
    """
    # Ensure directory exists
    upload_dir = "/Users/edric/Desktop/react/tbnt-api/data/image"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    if not file_ext:
        file_ext = ".png" # Default to png if no extension
        
    filename = f"{uuid.uuid4()}{file_ext}"
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # Return URL
    return {"url": f"/static/{filename}"}


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
            data_str = await websocket.receive_text()
            
            # Parse data (could be simple text or JSON with type)
            try:
                data_json = json.loads(data_str)
                content = data_json.get("content", "")
                message_type = data_json.get("type", "text")
            except json.JSONDecodeError:
                # Backward compatibility or simple text
                content = data_str
                message_type = "text"
            
            # Save message
            china_tz = timezone(timedelta(hours=8))
            now = datetime.now(china_tz)
            now_str = now.strftime("%Y-%m-%d %H:%M:%S")
            
            message = ChatMessage(
                user_id=user.id,
                content=content,
                message_type=message_type,
                created_at=now_str
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            
            # Prepare response with user info
            response = {
                "id": message.id,
                "content": message.content,
                "message_type": message.message_type,
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
