from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    title : str
    description : str
    status : str
    priority : Optional[int] = 0

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None

class TaskOut(TaskBase):
    id : int
    creation_date : datetime
    
    model_config = ConfigDict(from_attributes=True)