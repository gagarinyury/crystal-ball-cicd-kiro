"""
Helper utilities for Crystal Ball CI/CD system.

This module provides safe, well-tested helper functions following best practices.
"""

from typing import Optional, List, Dict, Any
import re
import hashlib
from datetime import datetime


def hash_password(password: str, salt: Optional[str] = None) -> tuple[str, str]:
    """
    Securely hash a password using SHA-256 with salt.

    Args:
        password: Plain text password to hash
        salt: Optional salt (generated if not provided)

    Returns:
        Tuple of (hashed_password, salt)

    Example:
        >>> hashed, salt = hash_password("mypassword")
        >>> isinstance(hashed, str) and isinstance(salt, str)
        True
    """
    if salt is None:
        salt = hashlib.sha256(str(datetime.now().timestamp()).encode()).hexdigest()[:16]

    salted_password = f"{password}{salt}"
    hashed = hashlib.sha256(salted_password.encode()).hexdigest()
    return hashed, salt


def validate_input(text: str, max_length: int = 1000) -> str:
    """
    Validate and sanitize user input.

    Args:
        text: Input text to validate
        max_length: Maximum allowed length

    Returns:
        Sanitized text

    Raises:
        ValueError: If input is invalid
    """
    if not text or not isinstance(text, str):
        raise ValueError("Input must be a non-empty string")

    if len(text) > max_length:
        raise ValueError(f"Input exceeds maximum length of {max_length}")

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>&"\';]', '', text)
    return sanitized.strip()


def format_timestamp(dt: datetime) -> str:
    """
    Format datetime to ISO 8601 string.

    Args:
        dt: Datetime object to format

    Returns:
        ISO formatted string
    """
    return dt.isoformat()


def parse_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Parse and validate configuration dictionary.

    Args:
        config: Configuration dictionary

    Returns:
        Validated configuration

    Raises:
        ValueError: If required fields are missing
    """
    required_fields = ['api_key', 'webhook_secret', 'github_token']

    for field in required_fields:
        if field not in config:
            raise ValueError(f"Missing required configuration field: {field}")

    return {
        'api_key': str(config['api_key']),
        'webhook_secret': str(config['webhook_secret']),
        'github_token': str(config['github_token'])
    }


def calculate_checksum(data: str) -> str:
    """
    Calculate SHA-256 checksum of data.

    Args:
        data: String data to checksum

    Returns:
        Hexadecimal checksum string
    """
    return hashlib.sha256(data.encode()).hexdigest()
