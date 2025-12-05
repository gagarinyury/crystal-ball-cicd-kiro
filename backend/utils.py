"""
Utility functions for Crystal Ball CI/CD.

This module provides helper functions for data validation and formatting.
"""

from typing import Optional, List
import re


def validate_email(email: str) -> bool:
    """
    Validate email address format.

    Args:
        email: Email address to validate

    Returns:
        True if email is valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_input(text: str) -> str:
    """
    Sanitize user input by removing potentially dangerous characters.

    Args:
        text: Input text to sanitize

    Returns:
        Sanitized text safe for display
    """
    # Remove HTML tags and special characters
    sanitized = re.sub(r'<[^>]+>', '', text)
    sanitized = re.sub(r'[<>&"\']', '', sanitized)
    return sanitized.strip()


def format_prediction_score(score: int) -> str:
    """
    Format prediction score with color indicator.

    Args:
        score: Prediction score (0-100)

    Returns:
        Formatted score string with emoji
    """
    if score >= 80:
        return f"🟢 {score}/100"
    elif score >= 60:
        return f"🟡 {score}/100"
    else:
        return f"🔴 {score}/100"


def get_severity_label(severity: int) -> str:
    """
    Get human-readable severity label.

    Args:
        severity: Severity level (1-10)

    Returns:
        Severity label (minor/major/dark)
    """
    if severity <= 3:
        return "minor"
    elif severity <= 7:
        return "major"
    else:
        return "dark"
