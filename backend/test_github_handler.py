"""
Tests for GitHub Webhook Handler.

Tests signature validation, payload parsing, and basic functionality.
"""

import pytest
import hmac
import hashlib
from github_handler import GitHubHandler


class TestGitHubHandler:
    """Test suite for GitHubHandler class."""
    
    @pytest.fixture
    def handler(self):
        """Create a GitHubHandler instance for testing."""
        return GitHubHandler(
            github_token="test_token_123",
            webhook_secret="test_secret"
        )
    
    @pytest.mark.asyncio
    async def test_validate_signature_valid(self, handler):
        """Test that valid signatures are accepted."""
        payload = b'{"test": "data"}'
        
        # Generate valid signature
        secret_bytes = handler.webhook_secret.encode('utf-8')
        signature_hash = hmac.new(
            secret_bytes,
            payload,
            hashlib.sha256
        ).hexdigest()
        signature = f"sha256={signature_hash}"
        
        result = await handler.validate_signature(payload, signature)
        assert result is True
    
    @pytest.mark.asyncio
    async def test_validate_signature_invalid(self, handler):
        """Test that invalid signatures are rejected."""
        payload = b'{"test": "data"}'
        signature = "sha256=invalid_signature_hash"
        
        result = await handler.validate_signature(payload, signature)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_signature_missing(self, handler):
        """Test that missing signatures are rejected."""
        payload = b'{"test": "data"}'
        
        result = await handler.validate_signature(payload, "")
        assert result is False
    
    @pytest.mark.asyncio
    async def test_validate_signature_wrong_format(self, handler):
        """Test that signatures with wrong format are rejected."""
        payload = b'{"test": "data"}'
        signature = "md5=somehash"  # Wrong algorithm prefix
        
        result = await handler.validate_signature(payload, signature)
        assert result is False
    
    @pytest.mark.asyncio
    async def test_handle_pr_event_opened(self, handler):
        """Test handling of PR opened event."""
        payload = {
            'action': 'opened',
            'pull_request': {
                'number': 123,
                'url': 'https://api.github.com/repos/owner/repo/pulls/123',
                'diff_url': 'https://github.com/owner/repo/pull/123.diff',
                'comments_url': 'https://api.github.com/repos/owner/repo/issues/123/comments',
                'title': 'Test PR',
                'user': {'login': 'testuser'}
            },
            'repository': {
                'full_name': 'owner/repo'
            }
        }
        
        result = await handler.handle_pr_event(payload)
        
        assert result is not None
        assert result['pr_number'] == 123
        assert result['repo'] == 'owner/repo'
        assert result['title'] == 'Test PR'
        assert 'diff_url' in result
        assert 'comments_url' in result
    
    @pytest.mark.asyncio
    async def test_handle_pr_event_synchronize(self, handler):
        """Test handling of PR synchronize event."""
        payload = {
            'action': 'synchronize',
            'pull_request': {
                'number': 456,
                'url': 'https://api.github.com/repos/owner/repo/pulls/456',
                'diff_url': 'https://github.com/owner/repo/pull/456.diff',
                'comments_url': 'https://api.github.com/repos/owner/repo/issues/456/comments',
                'title': 'Updated PR',
                'user': {'login': 'testuser'}
            },
            'repository': {
                'full_name': 'owner/repo'
            }
        }
        
        result = await handler.handle_pr_event(payload)
        
        assert result is not None
        assert result['pr_number'] == 456
    
    @pytest.mark.asyncio
    async def test_handle_pr_event_ignored_action(self, handler):
        """Test that non-relevant PR events are ignored."""
        payload = {
            'action': 'closed',
            'pull_request': {
                'number': 789,
                'url': 'https://api.github.com/repos/owner/repo/pulls/789',
                'diff_url': 'https://github.com/owner/repo/pull/789.diff',
                'comments_url': 'https://api.github.com/repos/owner/repo/issues/789/comments',
                'title': 'Closed PR',
                'user': {'login': 'testuser'}
            },
            'repository': {
                'full_name': 'owner/repo'
            }
        }
        
        result = await handler.handle_pr_event(payload)
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_handle_pr_event_malformed_payload(self, handler):
        """Test that malformed payloads raise ValidationError."""
        from pydantic import ValidationError
        
        payload = {
            'action': 'opened',
            # Missing pull_request field
            'repository': {
                'full_name': 'owner/repo'
            }
        }
        
        with pytest.raises(ValidationError):
            await handler.handle_pr_event(payload)
    
    def test_parse_diff_stats(self, handler):
        """Test diff statistics parsing."""
        diff = """diff --git a/file1.py b/file1.py
index abc123..def456 100644
--- a/file1.py
+++ b/file1.py
@@ -1,3 +1,4 @@
+# New line added
 def hello():
     print("hello")
-    print("old line")
+    print("new line")
diff --git a/file2.py b/file2.py
index 111222..333444 100644
--- a/file2.py
+++ b/file2.py
@@ -1,2 +1,3 @@
 def world():
+    print("added")
     pass
"""
        
        stats = handler._parse_diff_stats(diff)
        
        assert stats['files_changed'] == 2
        assert stats['lines_added'] == 3
        assert stats['lines_removed'] == 1
    
    def test_format_prediction_comment(self, handler):
        """Test prediction comment formatting."""
        prediction = {
            'prediction_score': 75,
            'mystical_message': 'The spirits sense potential...',
            'omens': [
                {
                    'type': 'minor',
                    'title': 'Code Smell Detected',
                    'description': 'Consider refactoring this section',
                    'file': 'src/main.py',
                    'severity': 3
                }
            ],
            'recommendations': [
                'Add more tests',
                'Review error handling'
            ]
        }
        
        comment = handler._format_prediction_comment(prediction)
        
        assert '75%' in comment
        assert 'The spirits sense potential...' in comment
        assert 'Code Smell Detected' in comment
        assert 'src/main.py' in comment
        assert 'Add more tests' in comment
        assert '⚠️' in comment  # Minor omen icon
