"""
GitHub Webhook Handler for Crystal Ball CI/CD system.

This module handles:
- Webhook signature validation using HMAC-SHA256
- PR event parsing and filtering
- PR diff fetching with retry logic
- Posting prediction comments to PRs
"""

import hmac
import hashlib
import logging
from typing import Optional, Dict, Any
import httpx
import asyncio
from models import WebhookPayload
from pydantic import ValidationError

logger = logging.getLogger(__name__)


class GitHubHandler:
    """
    Handles GitHub webhook events and API interactions.
    
    Responsibilities:
    - Validate webhook signatures for security
    - Parse and filter PR events
    - Fetch PR diffs from GitHub API
    - Post prediction comments to PRs
    - Handle rate limiting and retries
    """
    
    def __init__(self, github_token: str, webhook_secret: str):
        """
        Initialize GitHub handler with credentials.
        
        Args:
            github_token: GitHub personal access token with repo permissions
            webhook_secret: Secret for validating webhook signatures
        """
        self.github_token = github_token
        self.webhook_secret = webhook_secret
        self.headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'Crystal-Ball-CICD'
        }
        
    async def validate_signature(self, payload: bytes, signature: str) -> bool:
        """
        Validate GitHub webhook signature using HMAC-SHA256.
        
        GitHub sends a signature in the X-Hub-Signature-256 header formatted as:
        "sha256=<hex_digest>"
        
        Args:
            payload: Raw request body as bytes
            signature: Signature from X-Hub-Signature-256 header
            
        Returns:
            True if signature is valid, False otherwise
            
        Validates: Requirements 7.1
        """
        if not signature:
            logger.warning("No signature provided in webhook request")
            return False
            
        # Extract the hash from "sha256=<hash>" format
        if not signature.startswith('sha256='):
            logger.warning(f"Invalid signature format: {signature[:20]}...")
            return False
            
        received_hash = signature[7:]  # Remove "sha256=" prefix
        
        # Calculate expected signature
        secret_bytes = self.webhook_secret.encode('utf-8')
        expected_signature = hmac.new(
            secret_bytes,
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Use constant-time comparison to prevent timing attacks
        is_valid = hmac.compare_digest(expected_signature, received_hash)
        
        if not is_valid:
            logger.warning("Webhook signature validation failed")
        else:
            logger.info("Webhook signature validated successfully")
            
        return is_valid

    async def handle_pr_event(self, payload: dict) -> Optional[Dict[str, Any]]:
        """
        Process GitHub PR webhook event.
        
        Filters for PR events (opened, synchronize) and extracts relevant information.
        
        Args:
            payload: Parsed JSON webhook payload
            
        Returns:
            Dictionary with PR information if event should be processed:
            {
                'pr_url': str,
                'diff_url': str,
                'pr_number': int,
                'repo': str,
                'title': str,
                'comments_url': str
            }
            Returns None if event should be ignored.
            
        Raises:
            ValidationError: If payload is malformed or missing required fields
            
        Validates: Requirements 1.2, 7.3, 11.1, 11.2
        """
        try:
            # Validate payload structure using Pydantic model
            webhook_data = WebhookPayload(**payload)
            
            # Log the event
            action = webhook_data.action
            pr_number = webhook_data.pull_request.number
            repo = webhook_data.repository.full_name
            
            logger.info(
                f"Received webhook event: action={action}, "
                f"pr={pr_number}, repo={repo}"
            )
            
            # Filter for PR events we care about (opened, synchronize)
            if action not in ['opened', 'synchronize']:
                logger.info(f"Ignoring PR event with action: {action}")
                return None
                
            # Extract relevant information
            pr_data = {
                'pr_url': webhook_data.pull_request.url,
                'diff_url': webhook_data.pull_request.diff_url,
                'pr_number': webhook_data.pull_request.number,
                'repo': webhook_data.repository.full_name,
                'title': webhook_data.pull_request.title,
                'comments_url': webhook_data.pull_request.comments_url
            }
            
            logger.info(f"Processing PR #{pr_number} in {repo}")
            return pr_data
            
        except ValidationError as e:
            logger.error(f"Webhook payload validation failed: {e}")
            raise
        except KeyError as e:
            logger.error(f"Missing required field in webhook payload: {e}")
            raise ValidationError(f"Missing required field: {e}")
        except Exception as e:
            logger.error(f"Unexpected error processing webhook: {e}")
            raise

    async def fetch_pr_diff(self, diff_url: str, max_retries: int = 3) -> Dict[str, Any]:
        """
        Fetch PR diff from GitHub API with retry logic.
        
        Implements exponential backoff retry (1s, 2s, 4s) and handles rate limiting.
        Parses the diff to extract files_changed, lines_added, and lines_removed.
        
        Args:
            diff_url: URL to fetch the diff from
            max_retries: Maximum number of retry attempts (default: 3)
            
        Returns:
            Dictionary containing:
            {
                'diff': str,  # Raw diff content
                'files_changed': int,
                'lines_added': int,
                'lines_removed': int
            }
            
        Raises:
            httpx.RequestError: If all retries fail
            
        Validates: Requirements 1.3, 8.1, 8.2
        """
        retry_delays = [1, 2, 4]  # Exponential backoff in seconds
        
        for attempt in range(max_retries):
            try:
                async with httpx.AsyncClient(follow_redirects=True) as client:
                    # Request diff in plain text format
                    headers = {
                        **self.headers,
                        'Accept': 'application/vnd.github.v3.diff'
                    }

                    logger.info(f"Fetching PR diff (attempt {attempt + 1}/{max_retries})")
                    response = await client.get(
                        diff_url,
                        headers=headers,
                        timeout=30.0
                    )
                    
                    # Check for rate limiting
                    if response.status_code == 403:
                        rate_limit_remaining = response.headers.get('X-RateLimit-Remaining', '0')
                        rate_limit_reset = response.headers.get('X-RateLimit-Reset', '0')
                        
                        if rate_limit_remaining == '0':
                            reset_time = int(rate_limit_reset)
                            import time
                            wait_time = max(0, reset_time - int(time.time()))
                            
                            logger.warning(
                                f"GitHub API rate limit exceeded. "
                                f"Waiting {wait_time} seconds until reset."
                            )
                            
                            await asyncio.sleep(wait_time)
                            continue
                    
                    response.raise_for_status()
                    diff_content = response.text
                    
                    # Parse diff to extract statistics
                    stats = self._parse_diff_stats(diff_content)
                    
                    logger.info(
                        f"Successfully fetched diff: "
                        f"{stats['files_changed']} files, "
                        f"+{stats['lines_added']} -{stats['lines_removed']}"
                    )
                    
                    return {
                        'diff': diff_content,
                        **stats
                    }
                    
            except httpx.RequestError as e:
                logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries}): {e}")
                
                # If this was the last attempt, raise the error
                if attempt == max_retries - 1:
                    logger.error(f"Failed to fetch PR diff after {max_retries} attempts")
                    raise
                
                # Wait before retrying (exponential backoff)
                delay = retry_delays[attempt]
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
                
            except Exception as e:
                logger.error(f"Unexpected error fetching PR diff: {e}")
                raise
        
        # This should never be reached due to the raise in the loop
        raise httpx.RequestError("Failed to fetch PR diff")
    
    def _parse_diff_stats(self, diff: str) -> Dict[str, int]:
        """
        Parse diff content to extract statistics.
        
        Args:
            diff: Raw diff content
            
        Returns:
            Dictionary with files_changed, lines_added, lines_removed
        """
        files_changed = 0
        lines_added = 0
        lines_removed = 0
        
        for line in diff.split('\n'):
            # Count file changes (lines starting with "diff --git")
            if line.startswith('diff --git'):
                files_changed += 1
            # Count added lines (lines starting with "+", but not "+++")
            elif line.startswith('+') and not line.startswith('+++'):
                lines_added += 1
            # Count removed lines (lines starting with "-", but not "---")
            elif line.startswith('-') and not line.startswith('---'):
                lines_removed += 1
        
        return {
            'files_changed': files_changed,
            'lines_added': lines_added,
            'lines_removed': lines_removed
        }

    async def post_comment(self, comments_url: str, prediction: Dict[str, Any]) -> bool:
        """
        Post prediction as a formatted comment to the GitHub PR.
        
        Formats the prediction with mystical styling using markdown and posts
        it to the PR via GitHub API.
        
        Args:
            comments_url: URL to post comments to (from PR webhook payload)
            prediction: Prediction dictionary with score, omens, message, etc.
            
        Returns:
            True if comment was posted successfully, False otherwise
            
        Validates: Requirements 1.4
        """
        try:
            # Format prediction as markdown comment
            comment_body = self._format_prediction_comment(prediction)
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    comments_url,
                    headers=self.headers,
                    json={'body': comment_body},
                    timeout=30.0
                )
                
                response.raise_for_status()
                logger.info(f"Successfully posted prediction comment to PR")
                return True
                
        except httpx.HTTPStatusError as e:
            logger.error(f"Failed to post comment (HTTP {e.response.status_code}): {e}")
            return False
        except httpx.RequestError as e:
            logger.error(f"Failed to post comment (network error): {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error posting comment: {e}")
            return False
    
    def _format_prediction_comment(self, prediction: Dict[str, Any]) -> str:
        """
        Format prediction as a mystical-themed markdown comment.
        
        Args:
            prediction: Prediction dictionary
            
        Returns:
            Formatted markdown string
        """
        score = prediction.get('prediction_score', 0)
        message = prediction.get('mystical_message', 'The spirits are silent...')
        omens = prediction.get('omens', [])
        recommendations = prediction.get('recommendations', [])
        
        # Determine emoji based on score
        if score >= 80:
            emoji = '🔮✨'
            verdict = 'The stars align favorably!'
        elif score >= 60:
            emoji = '🔮⚠️'
            verdict = 'The spirits whisper caution...'
        else:
            emoji = '🔮☠️'
            verdict = 'Dark omens cloud the path ahead!'
        
        # Build comment
        lines = [
            f'## {emoji} Crystal Ball Prediction {emoji}',
            '',
            f'**Prediction Score:** {score}% chance of successful deployment',
            '',
            f'### {verdict}',
            '',
            f'_{message}_',
            ''
        ]
        
        # Add omens if present
        if omens:
            lines.append('### 🌙 Omens Revealed')
            lines.append('')
            
            for omen in omens:
                omen_type = omen.get('type', 'minor')
                title = omen.get('title', 'Unknown')
                description = omen.get('description', '')
                file = omen.get('file', 'unknown')
                severity = omen.get('severity', 1)
                
                # Map type to icon
                icon_map = {
                    'minor': '⚠️',
                    'major': '🔥',
                    'dark': '☠️'
                }
                icon = icon_map.get(omen_type, '⚠️')
                
                lines.append(f'#### {icon} {title} (Severity: {severity}/10)')
                lines.append(f'**File:** `{file}`')
                lines.append(f'{description}')
                lines.append('')
        else:
            lines.append('### ✨ No Omens Detected')
            lines.append('_The path appears clear..._')
            lines.append('')
        
        # Add recommendations if present
        if recommendations:
            lines.append('### 📜 Mystical Guidance')
            lines.append('')
            for rec in recommendations:
                lines.append(f'- {rec}')
            lines.append('')
        
        lines.append('---')
        lines.append('_🔮 Powered by Crystal Ball CI/CD_')
        
        return '\n'.join(lines)
