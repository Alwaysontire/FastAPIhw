from sqlalchemy.orm import Session
from . import models, schemas
from datetime import datetime

def create_task(db : Session, task : schemas.TaskCreate):
    db_task = models.Task(
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

def get_task(db : Session, task_id : int):
    return db.query(models.Task).filter(models.Task.id == task_id).first()

def get_tasks(db : Session, *, sort_by, order, q = None):
    query = db.query(models.Task)
    if q:
        query = query.filter(
            models.Task.title.ilike(f"%{q}%") | models.Task.description.ilike(f"%{q}%")
        )
    col = {"title" : models.Task.title, "status" : models.Task.status, "creation_date" : models.Task.creation_date}[sort_by]
    if order == "desc":
        col = col.desc()
        return query.order_by(col).all()
    
def update_task(db : Session, db_task : models.Task, updates : schemas.TaskUpdate):
    for field, value in updates.dict(exclude_unset=True).items():
        setattr(db_task, field, value)
    db.commit()
    db.refresh(db_task)
    return db_task

def delete_task(db : Session, db_task : models.Task):
    db.delete(db_task)
    db.commit()


def get_top_tasks(db: Session, n: int):
    return db.query(models.Task).order_by(models.Task.priority.desc()).limit(n).all()
