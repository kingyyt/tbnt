from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.work import WorkSettings, WorkItem
from app.schemas.work import (
    WorkSettings as WorkSettingsSchema,
    WorkSettingsCreate,
    WorkSettingsUpdate,
    WorkItem as WorkItemSchema,
    WorkItemCreate,
    WorkItemUpdate
)
from app.models.user import User

router = APIRouter()

# --- Work Settings ---

@router.get("/settings", response_model=WorkSettingsSchema)
def get_work_settings(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get current user's work settings.
    """
    settings = db.query(WorkSettings).filter(WorkSettings.user_id == current_user.id).first()
    if not settings:
        # Create default settings if not exists
        settings = WorkSettings(user_id=current_user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings

@router.put("/settings", response_model=WorkSettingsSchema)
def update_work_settings(
    settings_in: WorkSettingsUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update work settings.
    """
    settings = db.query(WorkSettings).filter(WorkSettings.user_id == current_user.id).first()
    if not settings:
        settings = WorkSettings(user_id=current_user.id)
        db.add(settings)
    
    settings.start_time = settings_in.start_time
    settings.end_time = settings_in.end_time
    db.commit()
    db.refresh(settings)
    return settings

# --- Work Items ---

@router.get("/items", response_model=List[WorkItemSchema])
def get_work_items(
    type: str = None,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get work items (memos, plans, progress).
    """
    query = db.query(WorkItem).filter(WorkItem.user_id == current_user.id)
    if type:
        query = query.filter(WorkItem.type == type)
    return query.all()

@router.post("/items", response_model=WorkItemSchema)
def create_work_item(
    item_in: WorkItemCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Create a new work item.
    """
    item = WorkItem(**item_in.model_dump(), user_id=current_user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.put("/items/{item_id}", response_model=WorkItemSchema)
def update_work_item(
    item_id: int,
    item_in: WorkItemUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Update a work item.
    """
    item = db.query(WorkItem).filter(WorkItem.id == item_id, WorkItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    update_data = item_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)
    
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

@router.delete("/items/{item_id}", response_model=WorkItemSchema)
def delete_work_item(
    item_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Delete a work item.
    """
    item = db.query(WorkItem).filter(WorkItem.id == item_id, WorkItem.user_id == current_user.id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    db.delete(item)
    db.commit()
    return item
