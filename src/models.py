from datetime import datetime, UTC
from .database import Base
from sqlalchemy import Column, Integer, String, DateTime

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    status = Column(String, index=True)
    creation_date = Column(DateTime, default=lambda: datetime.now(UTC))
    priority = Column(Integer, default=0)