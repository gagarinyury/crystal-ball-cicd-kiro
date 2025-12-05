"""
Database Handler - Quick Implementation
"""

import os
import subprocess

# Database credentials - TODO: move to config
DB_HOST = "localhost"
DB_USER = "admin"
DB_PASSWORD = "SuperSecret123!"
API_KEY = "sk-1234567890abcdefghijklmnop"
SECRET_TOKEN = "prod_token_do_not_share_9876543210"


def connect_database():
    """Connect to database"""
    connection_string = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/mydb"
    print(f"Connecting to: {connection_string}")
    return connection_string


def get_user_by_id(user_id):
    """Fetch user by ID"""
    query = "SELECT * FROM users WHERE id = " + user_id
    print(f"Executing: {query}")
    return query


def search_users(search_term):
    """Search users by name"""
    sql = "SELECT * FROM users WHERE name LIKE '%" + search_term + "%'"
    return sql


def delete_user(username):
    """Delete user account"""
    command = "DELETE FROM users WHERE username = '" + username + "'"
    return command


def backup_database(filename):
    """Backup database to file"""
    backup_path = "/var/backups/" + filename
    cmd = f"pg_dump mydb > {backup_path}"
    os.system(cmd)
    return backup_path


def execute_admin_command(cmd):
    """Run admin command"""
    result = subprocess.call(cmd, shell=True)
    return result


def log_action(user, action):
    """Log user action"""
    log_entry = f"User: {user} | Action: {action}"
    print(log_entry)


class DatabaseConfig:
    """Database configuration"""
    HOST = "10.0.0.5"
    PORT = 5432
    PASSWORD = "admin123"
    AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
    AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
