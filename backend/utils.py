"""
Utility functions for Crystal Ball CI/CD backend.

This module provides helper functions for data validation,
formatting, and common operations.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
import re


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def format_timestamp(dt: datetime) -> str:
    """
    Format datetime object to ISO 8601 string.

    Args:
        dt: Datetime object to format

    Returns:
        ISO 8601 formatted string
    """
    return dt.isoformat()


def sanitize_input(text: str, max_length: int = 1000) -> str:
    """
    Sanitize user input by removing potentially dangerous characters.

    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length

    Returns:
        Sanitized text
    """
    # Remove null bytes and control characters
    sanitized = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')

    # Truncate to max length
    return sanitized[:max_length]


def calculate_severity_average(omens: List[Dict[str, Any]]) -> float:
    """
    Calculate average severity from list of omens.

    Args:
        omens: List of omen dictionaries with 'severity' key

    Returns:
        Average severity score (0.0 if no omens)
    """
    if not omens:
        return 0.0

    total_severity = sum(omen.get('severity', 0) for omen in omens)
    return total_severity / len(omens)


def filter_omens_by_severity(
    omens: List[Dict[str, Any]],
    min_severity: int = 1,
    max_severity: int = 10
) -> List[Dict[str, Any]]:
    """
    Filter omens by severity range.

    Args:
        omens: List of omen dictionaries
        min_severity: Minimum severity (inclusive)
        max_severity: Maximum severity (inclusive)

    Returns:
        Filtered list of omens
    """
    return [
        omen for omen in omens
        if min_severity <= omen.get('severity', 0) <= max_severity
    ]
