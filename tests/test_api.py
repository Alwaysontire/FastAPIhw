import os, sys
import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from src.main import app
from src.database import Base, engine
from src.routers.tasks import get_db 
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

TEST_DB = os.path.join(os.getcwd(), "tests.db")
TEST_DATABASE_URL = f"sqlite:///{TEST_DB}"

test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False},)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def client():
    Base.metadata.drop_all(bind=test_engine) 
    Base.metadata.create_all(bind=test_engine) 
    with TestClient(app) as c:
        yield c
        
def test_create_and_read(client):
    r = client.post(
        "/tasks/",
        json={"title": "foo", "description": "bar", "status": "new", "priority": 7},
    )
    assert r.status_code in (200, 201)
    out = r.json()
    assert out["id"] == 1
    assert out["title"] == "foo"

    r2 = client.get("/tasks/")
    assert r2.status_code == 200
    arr = r2.json()
    assert isinstance(arr, list) and len(arr) >= 1

def test_read_single_notfound(client):
    r = client.get("/tasks/999")
    assert r.status_code == 404

def test_update_and_delete(client):
    post = client.post(
        "/tasks/", json={"title": "u", "description": "d", "status": "s", "priority": 0}
    )
    tid = post.json()["id"]

    r2 = client.put(f"/tasks/{tid}", json={"status": "done"})
    assert r2.status_code == 200
    assert r2.json()["status"] == "done"

    r3 = client.delete(f"/tasks/{tid}")
    assert r3.status_code == 204

    r4 = client.get(f"/tasks/{tid}")
    assert r4.status_code == 404

def test_top_n(client):
    for i in range(1, 6):
        client.post(
            "/tasks/",
            json={"title": f"t{i}", "description": "d", "status": "s", "priority": i},
        )
    r = client.get("/tasks/top/3")
    assert r.status_code == 200
    prios = [t["priority"] for t in r.json()]
    assert prios == [5,4,3]

def test_sort_query_params(client):
    client.post(
        "/tasks/",
        json={"title": "a", "description": "d", "status": "s", "priority": 1},
    )
    client.post(
        "/tasks/",
        json={"title": "b", "description": "d", "status": "s", "priority": 2},
    )
    r = client.get("/tasks/?sort_by=title&order=desc")
    names = [t["title"] for t in r.json()]
    assert names == sorted(names, reverse=True)
