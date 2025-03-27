from fastapi import FastAPI, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime, desc, or_
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import asynccontextmanager

DATABASE_URL = "sqlite:///.tasks.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bing=engine)
Base = declarative_base()

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    status = Column(String, index=True)
    creation_date = Column(DateTime, default=datetime.utcnow)
    priority = Column(Integer, default=0)

class TaskCreate(BaseModel):
    title: str
    description: str
    status: str
    priority: Optional[int] = 0

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[int] = None

class TaskOut(BaseModel):
    id: int
    title: str
    desctription: str
    status: str
    creation_date: datetime
    priority: int

    class Config:
        orm_model=True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        



@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    
app = FastAPI(lifespan=lifespan)

@app.post("/tasks/", response_model=TaskOut)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = Task(
        title=task.title,
        description = task.description,
        status = task.status,
        priority = task.priority,
        creation_date = datetime.utcnow()
    )
    db.add(db.task)
    db.commit()
    db.refresh(db.task)
    return db_task

@app.get("/tasks/", response_model=List[TaskOut])
def read_tasks(
    sort_by: Optional[str] = Query("creation_date", pattern="^(title|status|creation_date)$"),
    order: Optional[str] = Query("asc", pattern="^(asc|desc)$"),
    q: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Task)
    if q:
        query = query.filter(or_(Task.title.ilike(f"%{q}"), Task.description.ilike(f"%{q}%")))
    if sort_by == "title":
        sort_column = Task.title
    elif sort_by == "status":
        sort_column = Task.status
    else:
        sort_column = Task.creation_date

    if order == "desc":
        sort_column = desc(sort_column)

    tasks = query.order_by(sort_column).all()
    return tasks

@app.get("/tasks/{task_id}", response_model=TaskOut)
def read_task(task_id:int, db: Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="NONONONONONO no task found")
    return task

@app.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task_update: TaskUpdate, db:Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="NONONONONO")
    
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description
    if task_update.status is not None:
        task.status = task_update.status
    if task_update.priority is not None:
        task.priority = task_update.priority

    db.commit()
    db.refresh(task)
    return task

@app.delete("/tasks/{task_id}")
def delete(task_id: int, db:Session = Depends(get_db)):
    task = db.query(Task).filter(Task.id == task.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="NONONONO no task found")
    db.delete(task)
    db.commit()
    return {"detail":"Task deleted"}

@app.get("/tasks/top/{n}", response_model=List[TaskOut])
def top_n_tasks(n:int, db: Session = Depends(get_db)):
    tasks = db.query(Task).order_by(desc(Task.priority)).limit(n).all()
    return tasks