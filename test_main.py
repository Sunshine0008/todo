import pytest
import os
import sqlite3
from fastapi.testclient import TestClient
from app import app, DATABASE

client = TestClient(app)

# --- FIXTURES ---
@pytest.fixture(autouse=True)
def setup_db():
    """Ensures a clean database before each test."""
    # Create a temporary test database
    if os.path.exists(DATABASE):
        os.remove(DATABASE)
    
    # Re-initialize the schema
    conn = sqlite3.connect(DATABASE)
    conn.execute('CREATE TABLE users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT)')
    conn.execute('CREATE TABLE tasks (id INTEGER PRIMARY KEY, user_id INTEGER, text TEXT, status TEXT)')
    conn.commit()
    conn.close()
    yield
    # Cleanup after test if desired
    # os.remove(DATABASE)

# --- TESTS ---

def test_signup_and_login():
    """Tests the full user authentication flow."""
    user_payload = {"email": "test@meme.com", "password": "123"}
    
    # Signup
    response = client.post("/signup", json=user_payload)
    assert response.status_code == 201
    assert "user_id" in response.json()

    # Login
    response = client.post("/login", json=user_payload)
    assert response.status_code == 200
    assert response.json()["message"] == "Success"

def test_duplicate_signup_fails():
    """Ensures users can't register twice with the same email."""
    user_payload = {"email": "unique@meme.com", "password": "123"}
    client.post("/signup", json=user_payload)
    
    response = client.post("/signup", json=user_payload)
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"

def test_task_lifecycle():
    """Tests creating, updating, and deleting a task."""
    # 1. Setup User
    user_res = client.post("/signup", json={"email": "tasker@meme.com", "password": "123"})
    user_id = user_res.json()["user_id"]

    # 2. Add Task
    task_payload = {"user_id": user_id, "text": "🚀 Deploy to Moon"}
    task_res = client.post("/tasks", json=task_payload)
    assert task_res.status_code == 200
    task_id = task_res.json()["id"]

    # 3. Update to Done (Checks 'W' logic)
    update_res = client.put(f"/tasks/{task_id}", json={"status": "done"})
    assert update_res.status_code == 200
    
    # Verify the backend appended "(W)" to the text
    get_res = client.get(f"/tasks/{user_id}")
    tasks = get_res.json()
    assert "(W)" in tasks[0]["text"]
    assert tasks[0]["status"] == "done"

    # 4. Banish (Delete)
    del_res = client.delete(f"/tasks/{task_id}")
    assert del_res.status_code == 200
    
    # Verify it's gone
    final_get = client.get(f"/tasks/{user_id}")
    assert len(final_get.json()) == 0
