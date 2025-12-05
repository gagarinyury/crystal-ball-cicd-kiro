"""
EXTREMELY DANGEROUS CODE - DO NOT USE IN PRODUCTION
"""

import os
import pickle


def execute_user_command(cmd):
    # CRITICAL: Command injection vulnerability
    os.system(cmd)
    return eval(cmd)  # CRITICAL: Code injection


def load_user_data(data):
    # CRITICAL: Pickle deserialization vulnerability
    return pickle.loads(data)


def get_password():
    # CRITICAL: Hardcoded password
    return "admin123"


# CRITICAL: Exposed API key
API_KEY = "REDACTED_API_KEY"
DATABASE_PASSWORD = "root123"
SECRET_TOKEN = "super_secret_token_xyz"


def sql_query(user_input):
    # CRITICAL: SQL injection
    query = "SELECT * FROM users WHERE name = '" + user_input + "'"
    return query


def unsafe_file_read(filename):
    # CRITICAL: Path traversal
    with open("/data/" + filename) as f:
        return f.read()


# CRITICAL: No input validation
def process_payment(amount):
    total = amount * 1.1
    os.system(f"charge_card {amount}")  # Command injection
    return total
# Test update
# Trigger reanalysis
