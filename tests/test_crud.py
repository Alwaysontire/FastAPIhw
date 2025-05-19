import pytest
from sqlalchemy.orm import sessionmaker

from src.database import Base, engine
from src import crud
from src import schemas

@pytest.fixture(scope="module")
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()
    yield session
    session.close()

def test_create_and_get_task(db):
    tc = schemas.TaskCreate(
        title="T1", description="d1", status="new", priority=5
    )
    task = crud.create_task(db, tc)
    assert task.id == 1
    assert task.title == "T1"

    got = crud.get_task(db, task.id)
    assert got.id == task.id

def test_update_task(db):
    tc = schemas.TaskCreate(
        title="A", description="B", status="S", priority=1
    )
    task = crud.create_task(db, tc)
    upd = schemas.TaskUpdate(status="done")
    updated = crud.update_task(db, task, upd) 
    assert updated.status == "done"

def test_delete_task(db):
    tc = schemas.TaskCreate(
        title="X", description="Y", status="Z", priority=0
    )
    task = crud.create_task(db, tc)
    crud.delete_task(db, task) 
    assert crud.get_task(db, task.id) is None

def test_get_tasks_sort(db):
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    for i in range(1, 6):
        crud.create_task(
            db,
            schemas.TaskCreate(
                title=f"t{i}", description="d", status="s", priority=i
            ),
        )
    tasks = crud.get_tasks(db, sort_by="priority", order="desc")
    prios = [t.priority for t in tasks]
    assert prios == sorted(prios, reverse=True)
