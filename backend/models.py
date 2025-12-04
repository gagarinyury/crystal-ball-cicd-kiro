"""
Data models for Crystal Ball CI/CD system.

This module defines Pydantic models for:
- Omen: Individual warnings/predictions about code issues
- Prediction: Complete prediction with score, omens, and metadata
- WebhookPayload: GitHub webhook event validation
"""

from datetime import datetime
from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator
from uuid import uuid4


class Omen(BaseModel):
    """
    An omen represents a warning or prediction about potential code issues.
    
    Attributes:
        type: Severity category (minor, major, or dark)
        title: Brief warning title
        description: Detailed explanation of the issue
        file: Path to the affected file
        severity: Numeric severity from 1-10
        historical_failures: Optional count of past failures for this pattern
    """
    type: Literal['minor', 'major', 'dark']
    title: str
    description: str
    file: str
    severity: int = Field(ge=1, le=10)
    historical_failures: Optional[int] = None
    
    @field_validator('severity')
    @classmethod
    def validate_severity_range(cls, v: int) -> int:
        """Ensure severity is between 1 and 10."""
        if not 1 <= v <= 10:
            raise ValueError('Severity must be between 1 and 10')
        return v


class PredictionContext(BaseModel):
    """
    Context information about the PR being analyzed.
    
    Attributes:
        files_changed: Number of files modified in the PR
        lines_added: Number of lines added
        lines_removed: Number of lines removed
    """
    files_changed: int = Field(ge=0)
    lines_added: int = Field(ge=0)
    lines_removed: int = Field(ge=0)


class Prediction(BaseModel):
    """
    Complete prediction for a pull request.
    
    Attributes:
        id: Unique identifier (UUID)
        timestamp: When the prediction was made
        pr_url: GitHub PR URL
        pr_number: PR number
        repo: Repository full name (owner/repo)
        prediction_score: Success likelihood (0-100)
        omens: List of warnings/issues found
        mystical_message: Fortune-teller style summary
        recommendations: Actionable suggestions
        context: PR metadata (files changed, lines added/removed)
        actual_result: Actual deployment outcome (None until known)
        accurate: Whether prediction was accurate (None until known)
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=datetime.now)
    pr_url: str
    pr_number: int
    repo: str
    prediction_score: int = Field(ge=0, le=100)
    omens: List[Omen]
    mystical_message: str
    recommendations: List[str]
    context: PredictionContext
    actual_result: Optional[bool] = None
    accurate: Optional[bool] = None
    
    @field_validator('prediction_score')
    @classmethod
    def validate_score_range(cls, v: int) -> int:
        """Ensure prediction score is between 0 and 100."""
        if not 0 <= v <= 100:
            raise ValueError('Prediction score must be between 0 and 100')
        return v
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class GitHubUser(BaseModel):
    """GitHub user information from webhook payload."""
    login: str


class GitHubPullRequest(BaseModel):
    """
    GitHub pull request information from webhook payload.
    
    Attributes:
        number: PR number
        url: API URL for the PR
        diff_url: URL to fetch the diff
        comments_url: URL to post comments
        title: PR title
        user: User who created the PR
    """
    number: int
    url: str
    diff_url: str
    comments_url: str
    title: str
    user: GitHubUser


class GitHubRepository(BaseModel):
    """GitHub repository information from webhook payload."""
    full_name: str


class WebhookPayload(BaseModel):
    """
    GitHub webhook payload for pull request events.
    
    Validates the structure of incoming webhook events to ensure
    all required fields are present.
    
    Attributes:
        action: The action that triggered the webhook (opened, synchronize, closed, etc.)
        pull_request: PR details
        repository: Repository details
    """
    action: str
    pull_request: GitHubPullRequest
    repository: GitHubRepository
    
    @field_validator('action')
    @classmethod
    def validate_action(cls, v: str) -> str:
        """Validate that action is a non-empty string."""
        if not v or not v.strip():
            raise ValueError('Action must be a non-empty string')
        return v
