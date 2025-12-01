from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from app.db.repository import get_db
from app.api import deps
from app.models.friend import Friendship
from app.models.user import User
from app.schemas.friend import Friendship as FriendshipSchema, FriendshipCreate, FriendshipUpdate

router = APIRouter()

@router.post("/request", response_model=FriendshipSchema)
def send_friend_request(
    request_in: FriendshipCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Send a friend request by user number.
    """
    # 1. Find target user
    target_user = db.query(User).filter(User.number == request_in.target_number).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found with this number")
    
    if target_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="You cannot add yourself as a friend")

    # 2. Check if friendship already exists
    existing_friendship = db.query(Friendship).filter(
        or_(
            and_(Friendship.user_id == current_user.id, Friendship.friend_id == target_user.id),
            and_(Friendship.user_id == target_user.id, Friendship.friend_id == current_user.id)
        )
    ).first()

    if existing_friendship:
        if existing_friendship.status == 1:
            raise HTTPException(status_code=400, detail="You are already friends")
        if existing_friendship.status == 0:
            if existing_friendship.user_id == current_user.id:
                raise HTTPException(status_code=400, detail="Friend request already sent")
            else:
                # Automatically accept if the other person also sent a request (optional, but nice)
                # For now, just say request is pending
                raise HTTPException(status_code=400, detail="This user has already sent you a friend request")

    # 3. Create request
    friendship = Friendship(
        user_id=current_user.id,
        friend_id=target_user.id,
        status=0 # Pending
    )
    db.add(friendship)
    db.commit()
    db.refresh(friendship)
    
    # Attach info for response
    friendship.friend_info = target_user
    return friendship

@router.get("/requests", response_model=List[FriendshipSchema])
def get_friend_requests(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get pending friend requests (received).
    """
    requests = db.query(Friendship).filter(
        Friendship.friend_id == current_user.id,
        Friendship.status == 0
    ).all()
    
    # Populate requester info
    for req in requests:
        req.friend_info = req.requester
        
    return requests

@router.get("/", response_model=List[FriendshipSchema])
def get_friends(
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get accepted friends.
    """
    friendships = db.query(Friendship).filter(
        or_(Friendship.user_id == current_user.id, Friendship.friend_id == current_user.id),
        Friendship.status == 1
    ).all()
    
    # Populate friend info
    for f in friendships:
        if f.user_id == current_user.id:
            f.friend_info = f.target
        else:
            f.friend_info = f.requester
            
    return friendships

@router.put("/{friendship_id}", response_model=FriendshipSchema)
def respond_friend_request(
    friendship_id: int,
    status_in: FriendshipUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Accept (1) or Reject (2) a friend request.
    """
    friendship = db.query(Friendship).filter(Friendship.id == friendship_id).first()
    if not friendship:
        raise HTTPException(status_code=404, detail="Request not found")
        
    if friendship.friend_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    friendship.status = status_in.status
    db.commit()
    db.refresh(friendship)
    
    friendship.friend_info = friendship.requester
    return friendship

@router.delete("/{friend_id}", response_model=dict)
def delete_friend(
    friend_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Delete a friend.
    """
    friendship = db.query(Friendship).filter(
        or_(
            and_(Friendship.user_id == current_user.id, Friendship.friend_id == friend_id),
            and_(Friendship.user_id == friend_id, Friendship.friend_id == current_user.id)
        ),
        Friendship.status == 1
    ).first()
    
    if not friendship:
        raise HTTPException(status_code=404, detail="Friendship not found")
        
    db.delete(friendship)
    db.commit()
    
    return {"message": "Friend deleted"}
