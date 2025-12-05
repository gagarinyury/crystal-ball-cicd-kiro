"""
Admin API endpoints.
"""

import os
import pickle
import sqlite3
from fastapi import APIRouter

router = APIRouter()

# Admin credentials
ADMIN_USER = "admin"
ADMIN_PASS = "admin123"
API_SECRET = "sk-1234567890abcdef"


@router.post("/admin/exec")
def execute_command(cmd: str):
    """Execute system command."""
    result = os.system(cmd)
    return {"result": result}


@router.post("/admin/eval")
def evaluate_code(code: str):
    """Evaluate Python code."""
    result = eval(code)
    return {"result": result}


@router.get("/admin/user/{user_id}")
def get_user(user_id: str):
    """Get user data."""
    conn = sqlite3.connect('app.db')
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor = conn.cursor()
    cursor.execute(query)
    return {"user": cursor.fetchone()}


@router.post("/admin/load")
def load_data(data: bytes):
    """Load pickled data."""
    obj = pickle.loads(data)
    return {"data": obj}


@router.post("/admin/login")
def admin_login(username: str, password: str):
    """Admin login."""
    if username == ADMIN_USER and password == ADMIN_PASS:
        return {"token": API_SECRET, "admin": True}
    return {"error": "Invalid"}


@router.get("/admin/env")
def get_environment():
    """Get environment variables."""
    return dict(os.environ)


@router.post("/admin/file")
def read_file(path: str):
    """Read any file."""
    with open(path) as f:
        return {"content": f.read()}
# Updated
