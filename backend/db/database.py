
import sqlite3
import json
from datetime import datetime
from threading import Lock

DB_NAME = "tasks.db"
db_lock = Lock()


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def get_all_tasks():
    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT task_id, status, result, created_at
        FROM tasks
        ORDER BY created_at DESC
        """)

        rows = cursor.fetchall()
        conn.close()

        tasks = []
        for row in rows:
            tasks.append({
                "task_id": row[0],
                "status": row[1],
                "result": json.loads(row[2]) if row[2] else None,
                "created_at": row[3]
            })

        return tasks

def init_db():
    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            status TEXT,
            result TEXT,
            created_at TEXT,
            updated_at TEXT
        )
        """)

        conn.commit()
        conn.close()


# ---------------------------
# CRUD OPERATIONS
# ---------------------------

def create_task(task_id):
    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()

        now = datetime.utcnow().isoformat()

        cursor.execute("""
        INSERT INTO tasks (task_id, status, result, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """, (task_id, "processing", None, now, now))

        conn.commit()
        conn.close()


def update_task(task_id, status=None, result=None):
    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()

        now = datetime.utcnow().isoformat()

        if result is not None:
            result = json.dumps(result)

        cursor.execute("""
        UPDATE tasks
        SET status = COALESCE(?, status),
            result = COALESCE(?, result),
            updated_at = ?
        WHERE task_id = ?
        """, (status, result, now, task_id))

        conn.commit()
        conn.close()


def get_task(task_id):
    with db_lock:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT task_id, status, result, created_at, updated_at
        FROM tasks
        WHERE task_id = ?
        """, (task_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return None

        task = {
            "task_id": row[0],
            "status": row[1],
            "result": json.loads(row[2]) if row[2] else None,
            "created_at": row[3],
            "updated_at": row[4]
        }

        return task