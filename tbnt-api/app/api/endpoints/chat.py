from typing import List, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
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

# Store active connections for private chat
# Dictionary mapping user_id to their WebSocket connection
active_connections: dict[int, WebSocket] = {}

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        self.active_connections.append(websocket)
        active_connections[user_id] = websocket

    def disconnect(self, websocket: WebSocket, user_id: int):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if user_id in active_connections:
            del active_connections[user_id]

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            await connection.send_json(message)

    async def send_personal_message(self, message: dict, user_id: int):
        if user_id in active_connections:
            await active_connections[user_id].send_json(message)

manager = ConnectionManager()

@router.get("/history", response_model=List[ChatMessageSchema])
def get_chat_history(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get chat history (public lobby).
    """
    messages = db.query(ChatMessage).filter(ChatMessage.to_user_id == None).order_by(ChatMessage.id.desc()).offset(skip).limit(limit).all()
    return messages[::-1] # Return in chronological order

@router.get("/private/history", response_model=List[ChatMessageSchema])
def get_private_chat_history(
    friend_id: int,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get private chat history between current user and friend.
    """
    messages = db.query(ChatMessage).filter(
        or_(
            and_(ChatMessage.user_id == current_user.id, ChatMessage.to_user_id == friend_id),
            and_(ChatMessage.user_id == friend_id, ChatMessage.to_user_id == current_user.id)
        )
    ).order_by(ChatMessage.id.desc()).offset(skip).limit(limit).all()
    
    return messages[::-1]

from pydantic import BaseModel

class MarkReadRequest(BaseModel):
    friend_id: int

@router.post("/private/read")
def mark_messages_read(
    request: MarkReadRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Mark all messages from a friend as read.
    """
    try:
        # Update messages where sender is friend and receiver is current user
        db.query(ChatMessage).filter(
            ChatMessage.user_id == request.friend_id,
            ChatMessage.to_user_id == current_user.id,
            ChatMessage.is_read == False
        ).update({"is_read": True}, synchronize_session=False)
        
        db.commit()
        return {"message": "Messages marked as read"}
    except Exception as e:
        print(f"Error marking messages as read: {e}")
        # Import traceback to print full stack trace
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/unread", response_model=dict[int, int])
def get_unread_counts(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
):
    """
    Get unread message counts for each sender.
    """
    # Group by user_id (sender) and count where to_user_id is current_user and is_read is False
    from sqlalchemy import func
    results = db.query(
        ChatMessage.user_id, func.count(ChatMessage.id)
    ).filter(
        ChatMessage.to_user_id == current_user.id,
        ChatMessage.is_read == False
    ).group_by(ChatMessage.user_id).all()
    
    return {user_id: count for user_id, count in results}

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

    await manager.connect(websocket, user.id)
    try:
        while True:
            data_str = await websocket.receive_text()
            
            # Parse data
            try:
                data_json = json.loads(data_str)
                content = data_json.get("content", "")
                message_type = data_json.get("type", "text")
                to_user_id = data_json.get("to_user_id", None) # Optional target for private message
            except json.JSONDecodeError:
                content = data_str
                message_type = "text"
                to_user_id = None
            
            # Save message
            china_tz = timezone(timedelta(hours=8))
            now = datetime.now(china_tz)
            now_str = now.strftime("%Y-%m-%d %H:%M:%S")
            
            message = ChatMessage(
                user_id=user.id,
                content=content,
                message_type=message_type,
                created_at=now_str,
                to_user_id=to_user_id
            )
            db.add(message)
            db.commit()
            db.refresh(message)
            
            # Prepare response
            response = {
                "id": message.id,
                "content": message.content,
                "message_type": message.message_type,
                "created_at": message.created_at,
                "user_id": user.id,
                "to_user_id": message.to_user_id,
                "sender": {
                    "id": user.id,
                    "username": user.username,
                    "nickname": user.nickname,
                    "avatar": user.avatar,
                    "chat_color": user.chat_color,
                    "number": user.number
                }
            }
            
            if to_user_id:
                # Private Message: Send to sender and receiver only
                await manager.send_personal_message(response, user.id) # Echo back to sender
                await manager.send_personal_message(response, int(to_user_id))
            else:
                # Public Message: Broadcast to all
                await manager.broadcast(response)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket, user.id)
