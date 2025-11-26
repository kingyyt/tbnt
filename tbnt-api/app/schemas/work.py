from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Work Settings Schemas
class WorkSettingsBase(BaseModel):
    start_time: str
    end_time: str

class WorkSettingsCreate(WorkSettingsBase):
    pass

class WorkSettingsUpdate(WorkSettingsBase):
    pass

class WorkSettings(WorkSettingsBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# Work Item Schemas
class WorkItemBase(BaseModel):
    type: str
    content: str
    status: Optional[str] = "pending"
    percentage: Optional[int] = 0

class WorkItemCreate(WorkItemBase):
    pass

class WorkItemUpdate(BaseModel):
    content: Optional[str] = None
    status: Optional[str] = None
    percentage: Optional[int] = None

class WorkItem(WorkItemBase):
    id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Work Record Schemas
class WorkRecordBase(BaseModel):
    date: str
    clock_in_time: Optional[str] = None
    clock_out_time: Optional[str] = None

class WorkRecordCreate(BaseModel):
    pass

class WorkRecord(WorkRecordBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
