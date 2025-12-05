"""
Unit tests for utility functions.
"""

import pytest
from utils import sanitize_input, format_prediction_score, validate_webhook_payload


class TestSanitizeInput:
    """Tests for sanitize_input function."""

    def test_removes_dangerous_characters(self):
        """Test that dangerous characters are removed."""
        malicious = "<script>alert('xss')</script>"
        result = sanitize_input(malicious)
        assert '<' not in result
        assert '>' not in result
        assert 'script' in result  # Text remains

    def test_respects_max_length(self):
        """Test that input is truncated to max length."""
        long_input = "a" * 300
        result = sanitize_input(long_input, max_length=100)
        assert len(result) == 100

    def test_handles_empty_input(self):
        """Test that empty input returns empty string."""
        assert sanitize_input("") == ""
        assert sanitize_input(None) == ""


class TestFormatPredictionScore:
    """Tests for format_prediction_score function."""

    def test_green_for_high_score(self):
        """Test green indicator for scores >= 80."""
        result = format_prediction_score(85.5)
        assert "🟢" in result
        assert "85.5" in result

    def test_yellow_for_medium_score(self):
        """Test yellow indicator for scores 60-79."""
        result = format_prediction_score(70.0)
        assert "🟡" in result

    def test_red_for_low_score(self):
        """Test red indicator for scores < 60."""
        result = format_prediction_score(45.3)
        assert "🔴" in result


class TestValidateWebhookPayload:
    """Tests for validate_webhook_payload function."""

    def test_valid_payload(self):
        """Test that valid payload passes validation."""
        payload = {
            'action': 'opened',
            'pull_request': {
                'number': 123,
                'diff_url': 'https://github.com/test/repo/pull/123.diff',
                'html_url': 'https://github.com/test/repo/pull/123'
            },
            'repository': {'name': 'test-repo'}
        }
        assert validate_webhook_payload(payload) is True

    def test_missing_required_fields(self):
        """Test that payload with missing fields fails."""
        payload = {'action': 'opened'}
        assert validate_webhook_payload(payload) is False

    def test_invalid_pr_structure(self):
        """Test that invalid PR structure fails."""
        payload = {
            'action': 'opened',
            'pull_request': {'number': 123},  # Missing diff_url and html_url
            'repository': {'name': 'test-repo'}
        }
        assert validate_webhook_payload(payload) is False
