from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from .. import crud, models, schemas
from ..database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/tasks", tags=["tasks"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.TaskOut)
def create(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, task)

@router.get("/", response_model=List[schemas.TaskOut])
def read_all(
    sort_by: str = Query("creation_date", regex="^(title|status|creation_date)$"),
    order: str   = Query("asc", regex="^(asc|desc)$"),
    q: Optional[str] = None,
    db: Session = Depends(get_db)
):
    return crud.get_tasks(db, sort_by=sort_by, order=order, q=q)

@router.get("/{task_id}", response_model=schemas.TaskOut)
def read(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return db_task

@router.put("/{task_id}", response_model=schemas.TaskOut)
def update(task_id: int, updates: schemas.TaskUpdate, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return crud.update_task(db, db_task, updates)

@router.delete("/{task_id}", status_code=204)
def delete(task_id: int, db: Session = Depends(get_db)):
    db_task = crud.get_task(db, task_id)
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    crud.delete_task(db, db_task)
    return

@router.get("/top/{n}", response_model=List[schemas.TaskOut])
def top_n_tasks(n: int, db: Session = Depends(get_db)):
    return crud.get_top_tasks(db, n)
