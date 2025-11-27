from typing import List, Any
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api import deps
from app.models.work import WorkSettings, WorkItem, WorkRecord
from app.schemas.work import (
    WorkSettings as WorkSettingsSchema,
    WorkSettingsCreate,
    WorkSettingsUpdate,
    WorkItem as WorkItemSchema,
    WorkItemCreate,
    WorkItemUpdate,
    WorkRecord as WorkRecordSchema
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

# --- Work Records ---

@router.post("/clock-out", response_model=WorkRecordSchema)
def clock_out(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Clock out for the day. Can be called multiple times, will update the latest record or create new one if needed.
    """
    china_tz = timezone(timedelta(hours=8))
    now = datetime.now(china_tz)
    today = now.strftime("%Y-%m-%d")
    now_str = now.strftime("%Y-%m-%d %H:%M:%S")
    
    # Check if there is already a record for today
    record = db.query(WorkRecord).filter(
        WorkRecord.user_id == current_user.id,
        WorkRecord.date == today
    ).first()

    if not record:
        # Get user settings for start time
        settings = db.query(WorkSettings).filter(WorkSettings.user_id == current_user.id).first()
        start_time_str = "09:00:00"
        if settings and settings.start_time:
            # Ensure format is HH:MM:SS
            if len(settings.start_time) == 5:
                start_time_str = f"{settings.start_time}:00"
            else:
                start_time_str = settings.start_time

        clock_in_str = f"{today} {start_time_str}"

        record = WorkRecord(
            user_id=current_user.id,
            date=today,
            clock_in_time=clock_in_str, 
            clock_out_time=now_str
        )
        db.add(record)
    else:
        record.clock_out_time = now_str
    
    db.commit()
    db.refresh(record)
    return record

@router.get("/records/today", response_model=WorkRecordSchema | None)
def get_today_work_record(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get today's work record. Returns None if no record found.
    """
    china_tz = timezone(timedelta(hours=8))
    today = datetime.now(china_tz).strftime("%Y-%m-%d")
    record = db.query(WorkRecord).filter(
        WorkRecord.user_id == current_user.id,
        WorkRecord.date == today
    ).first()
    return record

@router.get("/records", response_model=List[WorkRecordSchema])
def get_work_records(
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Any:
    """
    Get work history records.
    """
    return db.query(WorkRecord).filter(WorkRecord.user_id == current_user.id).order_by(WorkRecord.date.desc()).all()
