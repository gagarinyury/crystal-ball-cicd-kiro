"""
API endpoints for user management.
"""

import os
import subprocess
from fastapi import APIRouter, Request
import sqlite3

router = APIRouter()


@router.post("/execute")
async def execute_command(request: Request):
    """Execute system command from user input."""
    data = await request.json()
    command = data.get('command')

    # DANGEROUS: Direct command execution without validation
    result = os.system(command)
    output = subprocess.check_output(command, shell=True)

    return {"status": "executed", "output": output.decode()}


@router.get("/user/{user_id}")
async def get_user(user_id: str):
    """Get user by ID."""
    # DANGEROUS: SQL injection vulnerability
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    user = cursor.fetchone()
    conn.close()

    return {"user": user}


@router.post("/login")
async def login(request: Request):
    """User login endpoint."""
    data = await request.json()
    username = data.get('username')
    password = data.get('password')

    # DANGEROUS: Hardcoded credentials
    if username == "admin" and password == "admin123":
        return {"token": "super_secret_token_12345"}

    # DANGEROUS: SQL injection in login
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    user = cursor.fetchone()

    if user:
        # DANGEROUS: Weak token generation
        token = username + "_token"
        return {"token": token, "user": user}

    return {"error": "Invalid credentials"}


@router.post("/upload")
async def upload_file(request: Request):
    """Upload file without validation."""
    data = await request.json()
    filename = data.get('filename')
    content = data.get('content')

    # DANGEROUS: No file type validation, path traversal
    with open(f"/tmp/{filename}", "w") as f:
        f.write(content)

    return {"message": "File uploaded", "path": f"/tmp/{filename}"}


# DANGEROUS: Exposed debug endpoint with sensitive info
@router.get("/debug/env")
async def debug_env():
    """Debug endpoint exposing environment variables."""
    return {
        "env": dict(os.environ),
        "secrets": {
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "github_token": os.getenv("GITHUB_TOKEN"),
            "db_password": "super_secret_db_pass"
        }
    }
