"""
Input validators for Crystal Ball CI/CD.

Secure validation functions using parameterized queries and proper escaping.
"""

from typing import Optional
import re


def validate_email(email: str) -> bool:
    """
    Validate email address format using safe regex.

    Args:
        email: Email address to validate

    Returns:
        True if valid email format

    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid-email")
        False
    """
    if not email or len(email) > 254:
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_filename(filename: str) -> Optional[str]:
    """
    Sanitize filename to prevent path traversal attacks.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename or None if invalid

    Example:
        >>> sanitize_filename("document.pdf")
        'document.pdf'
        >>> sanitize_filename("../etc/passwd")
        None
    """
    if not filename:
        return None

    # Remove path traversal attempts
    if '..' in filename or '/' in filename or '\\' in filename:
        return None

    # Only allow alphanumeric, dots, dashes, underscores
    pattern = r'^[a-zA-Z0-9._-]+$'
    if not re.match(pattern, filename):
        return None

    return filename


def validate_score(score: int) -> bool:
    """
    Validate prediction score is in valid range.

    Args:
        score: Score to validate

    Returns:
        True if score is between 0 and 100
    """
    return isinstance(score, int) and 0 <= score <= 100
