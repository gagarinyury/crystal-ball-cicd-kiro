"""
Input validation utilities for Crystal Ball CI/CD.

Provides secure input validation and sanitization functions.
"""

import re
from typing import Optional, List
from urllib.parse import urlparse


def validate_github_url(url: str) -> bool:
    """
    Validate GitHub URL format.

    Args:
        url: GitHub URL to validate

    Returns:
        True if valid GitHub URL, False otherwise

    Example:
        >>> validate_github_url("https://github.com/user/repo")
        True
        >>> validate_github_url("https://evil.com/hack")
        False
    """
    try:
        parsed = urlparse(url)
        return (
            parsed.scheme in ('http', 'https') and
            parsed.netloc in ('github.com', 'api.github.com', 'patch-diff.githubusercontent.com')
        )
    except Exception:
        return False


def sanitize_filename(filename: str, max_length: int = 255) -> str:
    """
    Sanitize filename by removing dangerous characters.

    Args:
        filename: Original filename
        max_length: Maximum allowed length

    Returns:
        Sanitized filename safe for filesystem operations

    Example:
        >>> sanitize_filename("../../etc/passwd")
        'etcpasswd'
        >>> sanitize_filename("test<script>.py")
        'testscript.py'
    """
    # Remove path traversal attempts
    filename = filename.replace('..', '')
    filename = filename.replace('/', '')
    filename = filename.replace('\\', '')

    # Remove potentially dangerous characters
    filename = re.sub(r'[<>:"|?*]', '', filename)

    # Truncate to max length
    return filename[:max_length]


def validate_severity(severity: int) -> bool:
    """
    Validate severity score is within acceptable range.

    Args:
        severity: Severity score to validate

    Returns:
        True if severity is between 1 and 10 inclusive

    Example:
        >>> validate_severity(5)
        True
        >>> validate_severity(15)
        False
    """
    return 1 <= severity <= 10


def validate_prediction_score(score: int) -> bool:
    """
    Validate prediction score is within acceptable range.

    Args:
        score: Prediction score to validate

    Returns:
        True if score is between 0 and 100 inclusive

    Example:
        >>> validate_prediction_score(85)
        True
        >>> validate_prediction_score(150)
        False
    """
    return 0 <= score <= 100


def sanitize_log_message(message: str) -> str:
    """
    Sanitize log message to prevent log injection.

    Args:
        message: Log message to sanitize

    Returns:
        Sanitized log message with newlines and special chars removed

    Example:
        >>> sanitize_log_message("User logged in\\nADMIN")
        'User logged in ADMIN'
    """
    # Remove newlines and carriage returns to prevent log injection
    sanitized = message.replace('\n', ' ').replace('\r', ' ')

    # Remove ANSI escape codes
    sanitized = re.sub(r'\x1b\[[0-9;]*m', '', sanitized)

    return sanitized


def validate_pr_number(pr_number: int) -> bool:
    """
    Validate PR number is positive integer.

    Args:
        pr_number: Pull request number

    Returns:
        True if valid PR number

    Example:
        >>> validate_pr_number(123)
        True
        >>> validate_pr_number(-1)
        False
    """
    return pr_number > 0
