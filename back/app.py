import sqlite3
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Enable CORS (Same logic as Flask-CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE = 'tasks.db'

# --- MODELS (Pydantic) ---
class UserAuth(BaseModel):
    email: str
    password: str

class TaskCreate(BaseModel):
    user_id: int
    text: str

class TaskStatusUpdate(BaseModel):
    status: str

class TaskResponse(BaseModel):
    id: int
    user_id: int
    text: str
    status: str

# --- DB UTILS ---
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    conn = sqlite3.connect(DATABASE)
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )''')
    conn.execute('''CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        text TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')
    conn.commit()
    conn.close()

init_db()

# --- AUTH ROUTES ---

@app.post("/signup", status_code=201)
def signup(user: UserAuth):
    conn = sqlite3.connect(DATABASE)
    try:
        cursor = conn.execute('INSERT INTO users (email, password) VALUES (?, ?)', 
                             (user.email, user.password))
        conn.commit()
        return {"message": "User Created", "user_id": cursor.lastrowid}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Email already exists")
    finally:
        conn.close()

@app.post("/login")
def login(user: UserAuth):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    res = conn.execute('SELECT * FROM users WHERE email = ? AND password = ?', 
                        (user.email, user.password)).fetchone()
    conn.close()
    
    if res:
        return {"message": "Success", "user_id": res['id']}
    raise HTTPException(status_code=401, detail="Invalid email or password")

# --- TASK ROUTES ---

@app.get("/tasks/{user_id}", response_model=List[TaskResponse])
def get_tasks(user_id: int):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    tasks = conn.execute('SELECT * FROM tasks WHERE user_id = ?', (user_id,)).fetchall()
    conn.close()
    return [dict(row) for row in tasks]

@app.post("/tasks")
def add_task(task: TaskCreate):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.execute('INSERT INTO tasks (user_id, text, status) VALUES (?, ?, ?)', 
                         (task.user_id, task.text, 'todo'))
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id, "text": task.text, "status": "todo"}

@app.put("/tasks/{task_id}")
def update_task(task_id: int, update: TaskStatusUpdate):
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    task = conn.execute('SELECT * FROM tasks WHERE id = ?', (task_id,)).fetchone()
    
    if not task:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")

    new_status = update.status
    current_text = task['text']
    
    if new_status == 'done' and "(W)" not in current_text:
        current_text += " (W)"
            
    conn.execute('UPDATE tasks SET status = ?, text = ? WHERE id = ?', 
                 (new_status, current_text, task_id))
    conn.commit()
    conn.close()
    return {"message": "Task updated"}

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    conn = sqlite3.connect(DATABASE)
    conn.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()
    return {"message": "Banishment complete"}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000)
