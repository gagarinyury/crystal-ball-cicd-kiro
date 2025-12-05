"""
Security utilities for Crystal Ball CI/CD.

Production-ready security functions with best practices.
"""

from typing import Optional
import secrets
import hashlib
import hmac


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.

    Args:
        length: Length of the token in bytes

    Returns:
        Hexadecimal token string

    Example:
        >>> token = generate_secure_token()
        >>> len(token) == 64  # 32 bytes = 64 hex chars
        True
    """
    return secrets.token_hex(length)


def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify HMAC-SHA256 signature for webhook security.

    Args:
        payload: Raw payload bytes
        signature: Signature to verify
        secret: Shared secret key

    Returns:
        True if signature is valid

    Example:
        >>> payload = b"test data"
        >>> secret = "secret_key"
        >>> sig = create_signature(payload, secret)
        >>> verify_signature(payload, sig, secret)
        True
    """
    expected_signature = create_signature(payload, secret)
    return hmac.compare_digest(signature, expected_signature)


def create_signature(payload: bytes, secret: str) -> str:
    """
    Create HMAC-SHA256 signature for webhook.

    Args:
        payload: Data to sign
        secret: Secret key

    Returns:
        HMAC signature as hex string
    """
    return hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()


def hash_sensitive_data(data: str) -> str:
    """
    Hash sensitive data using SHA-256.

    Args:
        data: Sensitive data to hash

    Returns:
        Hashed data as hex string
    """
    return hashlib.sha256(data.encode()).hexdigest()
# Updated for demo
