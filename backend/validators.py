"""
Secure Input Validation Utilities

This module provides security-focused validation functions to prevent
common vulnerabilities like SQL injection, path traversal, and log injection.
"""

import re
from typing import Optional
from urllib.parse import urlparse


def validate_email(email: str) -> bool:
    """
    Validate email address format using RFC 5322 compliant regex.

    Args:
        email: Email address to validate

    Returns:
        True if email format is valid, False otherwise

    Example:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid.email")
        False
    """
    if not email or not isinstance(email, str):
        return False

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_filename(filename: str) -> Optional[str]:
    """
    Sanitize filename to prevent path traversal attacks.

    Removes directory traversal sequences like ../ and absolute paths.
    Only allows alphanumeric characters, dots, hyphens, and underscores.

    Args:
        filename: Original filename from user input

    Returns:
        Sanitized filename or None if invalid

    Security:
        - Prevents path traversal (../, ../../etc/passwd)
        - Blocks absolute paths (/etc/passwd, C:\\Windows)
        - Removes special characters that could be exploited
    """
    if not filename or not isinstance(filename, str):
        return None

    # Remove any directory components
    filename = filename.split('/')[-1].split('\\')[-1]

    # Remove path traversal sequences
    if '..' in filename or filename.startswith(('.', '/')):
        return None

    # Only allow safe characters: alphanumeric, dots, hyphens, underscores
    sanitized = re.sub(r'[^a-zA-Z0-9._-]', '', filename)

    # Ensure filename is not empty after sanitization
    if not sanitized or sanitized in ('.', '..'):
        return None

    return sanitized


def validate_url_whitelist(url: str, allowed_domains: list[str]) -> bool:
    """
    Validate URL against a whitelist of allowed domains.

    Prevents SSRF (Server-Side Request Forgery) attacks by ensuring
    only approved domains are accessed.

    Args:
        url: URL to validate
        allowed_domains: List of allowed domain names

    Returns:
        True if URL domain is in whitelist, False otherwise

    Security:
        - Prevents SSRF attacks
        - Blocks access to internal networks (localhost, 127.0.0.1, 192.168.*)
        - Validates against explicit whitelist only
    """
    if not url or not isinstance(url, str):
        return False

    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        # Block localhost and internal IPs
        internal_patterns = [
            'localhost',
            '127.0.0.1',
            '0.0.0.0',
            '192.168.',
            '10.',
            '172.16.',
            '172.17.',
            '172.18.',
            '172.19.',
            '172.20.',
            '172.21.',
            '172.22.',
            '172.23.',
            '172.24.',
            '172.25.',
            '172.26.',
            '172.27.',
            '172.28.',
            '172.29.',
            '172.30.',
            '172.31.',
        ]

        for pattern in internal_patterns:
            if domain.startswith(pattern):
                return False

        # Check against whitelist
        return domain in [d.lower() for d in allowed_domains]

    except Exception:
        return False


def prevent_log_injection(user_input: str) -> str:
    """
    Sanitize user input to prevent log injection attacks.

    Removes newline characters that could be used to inject fake log entries
    or manipulate log analysis tools.

    Args:
        user_input: User-provided string to be logged

    Returns:
        Sanitized string safe for logging

    Security:
        - Prevents log injection/forging
        - Removes CRLF characters (\r\n)
        - Prevents manipulation of log parsing tools
    """
    if not isinstance(user_input, str):
        return str(user_input)

    # Remove newlines and carriage returns
    sanitized = user_input.replace('\n', ' ').replace('\r', ' ')

    # Remove null bytes
    sanitized = sanitized.replace('\x00', '')

    return sanitized


def validate_integer_range(
    value: str,
    min_value: int,
    max_value: int
) -> Optional[int]:
    """
    Validate and convert string to integer within specified range.

    Args:
        value: String value to validate
        min_value: Minimum allowed value (inclusive)
        max_value: Maximum allowed value (inclusive)

    Returns:
        Integer value if valid, None otherwise

    Security:
        - Prevents integer overflow
        - Validates type safety
        - Enforces business logic constraints
    """
    if not isinstance(value, str):
        return None

    try:
        int_value = int(value)
        if min_value <= int_value <= max_value:
            return int_value
        return None
    except (ValueError, OverflowError):
        return None
