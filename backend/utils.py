"""
Utility functions for Crystal Ball CI/CD system.

This module provides helper functions for data validation and formatting.
"""

from typing import Optional, Dict, Any
import re


def sanitize_input(user_input: str, max_length: int = 255) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        user_input: Raw user input string
        max_length: Maximum allowed length

    Returns:
        Sanitized string safe for processing
    """
    if not user_input:
        return ""

    # Remove potentially dangerous characters
    sanitized = re.sub(r'[<>\'\";&|`$]', '', user_input)

    # Trim to max length
    sanitized = sanitized[:max_length]

    return sanitized.strip()


def format_prediction_score(score: float) -> str:
    """
    Format prediction score with color indicator.

    Args:
        score: Prediction score (0-100)

    Returns:
        Formatted string with emoji indicator
    """
    if score >= 80:
        return f"🟢 {score:.1f}%"
    elif score >= 60:
        return f"🟡 {score:.1f}%"
    else:
        return f"🔴 {score:.1f}%"


def validate_webhook_payload(payload: Dict[str, Any]) -> bool:
    """
    Validate GitHub webhook payload structure.

    Args:
        payload: Webhook payload dictionary

    Returns:
        True if payload is valid, False otherwise
    """
    required_fields = ['action', 'pull_request', 'repository']

    for field in required_fields:
        if field not in payload:
            return False

    # Validate PR structure
    pr = payload.get('pull_request', {})
    if not all(key in pr for key in ['number', 'diff_url', 'html_url']):
        return False

    return True
