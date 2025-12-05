# Design Document

## Overview

Crystal Ball CI/CD is a real-time AI-powered monitoring system that predicts deployment success for GitHub pull requests. The system consists of four main layers:

1. **Backend (Python FastAPI)**: Handles GitHub webhooks, orchestrates AI analysis, manages WebSocket connections, and provides rate limiting
2. **AI Analysis Layer**: Uses Anthropic Claude API to analyze code diffs and generate predictions with mystical-themed messaging
3. **Persistent Storage Layer (PostgreSQL)**: Stores predictions and historical data for long-term analysis and system resilience
4. **Frontend (React + Vite)**: Provides an engaging mystical dashboard with real-time updates via WebSocket and configurable backend connection

The system is designed for production deployment with persistent storage, rate limiting, improved diff parsing, comprehensive health checks, and environment-based configuration.

## Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        GitHub                                │
│                    (Webhook Events)                          │
└────────────────────────┬────────────────────────────────────┘
                         │ HTTPS (via ngrok)
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  GitHub Webhook Handler                              │   │
│  │  - Signature validation                              │   │
│  │  - Event parsing & filtering                         │   │
│  │  - PR diff fetching                                  │   │
│  └──────────────┬───────────────────────────────────────┘   │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  AI Analyzer                                         │   │
│  │  - LLM prompt construction                           │   │
│  │  - Anthropic API integration                         │   │
│  │  - Omen classification                               │   │
│  └──────────────┬───────────────────────────────────────┘   │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Prediction Engine                                   │   │
│  │  - Historical data storage                           │   │
│  │  - Pattern matching                                  │   │
│  │  - Prediction enhancement                            │   │
│  └──────────────┬───────────────────────────────────────┘   │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  WebSocket Server                                    │   │
│  │  - Connection management                             │   │
│  │  - Broadcast to clients                              │   │
│  └──────────────┬───────────────────────────────────────┘   │
└─────────────────┼────────────────────────────────────────────┘
                  │ WebSocket
                  ▼
┌─────────────────────────────────────────────────────────────┐
│                   React Frontend                             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  WebSocket Client                                    │   │
│  │  - Auto-reconnect logic                              │   │
│  │  - Connection status tracking                        │   │
│  └──────────────┬───────────────────────────────────────┘   │
│                 │                                            │
│                 ▼                                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Crystal Ball Component                              │   │
│  │  - Animated visualization                            │   │
│  │  - Score display with color coding                   │   │
│  │  - Mystical message rendering                        │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Omens Feed Component                                │   │
│  │  - Omen cards with severity                          │   │
│  │  - Icon mapping (⚠️🔥☠️)                              │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  History Component                                   │   │
│  │  - Recent predictions list (max 10)                  │   │
│  │  - Accuracy metrics display                          │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Backend:**
- FastAPI (async web framework)
- Uvicorn (ASGI server)
- httpx (async HTTP client for GitHub API)
- anthropic (Claude API client)
- python-dotenv (environment configuration)
- WebSockets (built into FastAPI)
- asyncpg (async PostgreSQL driver)
- slowapi (rate limiting middleware)

**Frontend:**
- React 18
- Vite (build tool & dev server)
- Native WebSocket API
- CSS3 animations

**Database:**
- PostgreSQL 14+ (persistent storage)

**Infrastructure:**
- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- ngrok (webhook tunneling for development)

## Components and Interfaces

### Backend Components

#### 1. GitHub Webhook Handler (`github_handler.py`)

**Responsibilities:**
- Validate GitHub webhook signatures using HMAC-SHA256
- Parse and filter PR events (opened, synchronize)
- Fetch PR diffs from GitHub API
- Post prediction comments back to PRs
- Handle GitHub API rate limits and retries

**Interface:**
```python
class GitHubHandler:
    def __init__(self, github_token: str, webhook_secret: str):
        """Initialize with GitHub credentials"""
        
    async def validate_signature(self, payload: bytes, signature: str) -> bool:
        """Validate webhook signature using HMAC-SHA256"""
        
    async def handle_pr_event(self, payload: dict) -> Optional[dict]:
        """
        Process PR webhook event
        Returns: {
            'pr_url': str,
            'diff': str,
            'context': {
                'files_changed': int,
                'lines_added': int,
                'lines_removed': int,
                'pr_number': int,
                'repo': str
            }
        }
        """
        
    async def fetch_pr_diff(self, diff_url: str) -> str:
        """Fetch PR diff with retry logic"""
        
    async def post_comment(self, pr_url: str, message: str) -> bool:
        """Post prediction comment to PR"""
```

#### 2. AI Analyzer (`ai_analyzer.py`)

**Responsibilities:**
- Construct structured prompts for LLM
- Call Anthropic Claude API
- Parse and validate LLM responses
- Classify omens by severity thresholds
- Generate fallback predictions on API failures

**Interface:**
```python
class AIAnalyzer:
    def __init__(self, api_key: str):
        """Initialize Anthropic client"""
        
    async def analyze_code_diff(self, diff: str, context: dict) -> dict:
        """
        Analyze code diff using LLM
        Returns: {
            'prediction_score': int (0-100),
            'omens': [
                {
                    'type': 'minor' | 'major' | 'dark',
                    'title': str,
                    'description': str,
                    'file': str,
                    'severity': int (1-10)
                }
            ],
            'mystical_message': str,
            'recommendations': [str]
        }
        """
        
    def classify_omen_type(self, severity: int) -> str:
        """Map severity (1-10) to omen type"""
        
    def create_fallback_prediction(self) -> dict:
        """Generate fallback when LLM fails"""
```

#### 3. Prediction Engine (`prediction_engine.py`)

**Responsibilities:**
- Store predictions in memory (Python list)
- Track historical outcomes
- Calculate accuracy metrics
- Enhance predictions with historical patterns
- Identify recurring failure patterns

**Interface:**
```python
class PredictionEngine:
    def __init__(self):
        """Initialize with empty history"""
        
    def store_prediction(self, prediction: dict) -> None:
        """Add prediction to history"""
        
    def learn_from_outcome(self, prediction_id: str, actual_result: bool) -> None:
        """Record actual deployment outcome"""
        
    def get_accuracy_rate(self) -> float:
        """Calculate overall accuracy percentage"""
        
    def enhance_prediction(self, ai_prediction: dict) -> dict:
        """
        Enhance prediction with historical data
        - Increase severity for recurring patterns
        - Annotate with failure counts
        - Recalculate prediction score
        """
        
    def get_pattern_failures(self, omen_type: str, file: str) -> int:
        """Get failure count for specific pattern"""
```

#### 4. WebSocket Manager (`websocket_manager.py`)

**Responsibilities:**
- Accept WebSocket connections
- Maintain active connection list
- Broadcast predictions to all clients
- Handle connection failures gracefully

**Interface:**
```python
class WebSocketManager:
    def __init__(self):
        """Initialize with empty connection list"""
        
    async def connect(self, websocket: WebSocket) -> None:
        """Accept and register new connection"""
        
    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove connection from active list"""
        
    async def broadcast(self, message: dict) -> None:
        """Send message to all connected clients"""
        
    def get_connection_count(self) -> int:
        """Return number of active connections"""
```

#### 5. Database Service (`database.py`)

**Responsibilities:**
- Manage PostgreSQL connection pool
- Store and retrieve predictions
- Load historical data on startup
- Handle database migrations
- Implement retry logic for connection failures

**Interface:**
```python
class DatabaseService:
    def __init__(self, connection_string: str):
        """Initialize connection pool"""
        
    async def connect(self) -> None:
        """Establish database connection with retry logic"""
        
    async def disconnect(self) -> None:
        """Close database connection pool"""
        
    async def save_prediction(self, prediction: dict) -> str:
        """
        Save prediction to database
        Returns: prediction_id (UUID)
        """
        
    async def get_predictions(self, limit: int = 100) -> List[dict]:
        """Retrieve recent predictions ordered by timestamp"""
        
    async def update_outcome(self, prediction_id: str, actual_result: bool) -> None:
        """Update prediction with actual deployment outcome"""
        
    async def get_accuracy_metrics(self) -> dict:
        """
        Calculate accuracy metrics from database
        Returns: {
            'total_predictions': int,
            'predictions_with_outcomes': int,
            'accurate_predictions': int,
            'accuracy_rate': float
        }
        """
        
    async def health_check(self) -> bool:
        """Verify database connectivity"""
```

#### 6. Rate Limiter (`rate_limiter.py`)

**Responsibilities:**
- Track request counts per IP address
- Implement sliding window rate limiting
- Reject requests exceeding limits
- Provide rate limit headers in responses

**Interface:**
```python
class RateLimiter:
    def __init__(self, requests_per_minute: int = 10):
        """Initialize with rate limit threshold"""
        
    async def check_rate_limit(self, ip_address: str) -> tuple[bool, Optional[int]]:
        """
        Check if IP is within rate limit
        Returns: (is_allowed, retry_after_seconds)
        """
        
    async def record_request(self, ip_address: str) -> None:
        """Record request for IP address"""
        
    async def cleanup_expired(self) -> None:
        """Remove expired entries from tracking"""
```

#### 7. Configuration Service (`config.py`)

**Responsibilities:**
- Load and validate environment variables
- Provide typed configuration access
- Handle environment-specific settings
- Validate required configuration on startup

**Interface:**
```python
class Config:
    def __init__(self):
        """Load and validate configuration from environment"""
        
    @property
    def github_token(self) -> str:
        """GitHub API token"""
        
    @property
    def anthropic_api_key(self) -> str:
        """Anthropic API key"""
        
    @property
    def webhook_secret(self) -> str:
        """GitHub webhook secret"""
        
    @property
    def database_url(self) -> str:
        """PostgreSQL connection string"""
        
    @property
    def frontend_url(self) -> str:
        """Frontend URL for CORS"""
        
    @property
    def rate_limit_per_minute(self) -> int:
        """Rate limit threshold"""
        
    def validate(self) -> None:
        """Validate all required config is present"""
```

#### 8. Main Application (`main.py`)

**Responsibilities:**
- Initialize FastAPI app
- Configure CORS for frontend
- Wire up all components
- Define HTTP and WebSocket endpoints
- Handle application lifecycle
- Apply rate limiting middleware

**Endpoints:**
- `POST /webhook/github` - Receive GitHub webhooks (rate limited)
- `GET /health` - Comprehensive health check with component status
- `WS /ws` - WebSocket connection for real-time updates

### Frontend Components

#### 1. WebSocket Client Hook (`useWebSocket.js`)

**Responsibilities:**
- Establish WebSocket connection
- Implement auto-reconnect with exponential backoff
- Track connection status
- Handle incoming messages

**Interface:**
```javascript
function useWebSocket(url) {
    // Returns: {
    //   connected: boolean,
    //   lastMessage: object | null,
    //   reconnectAttempt: number
    // }
}
```

#### 2. Crystal Ball Component (`CrystalBall.jsx`)

**Responsibilities:**
- Display animated crystal ball orb
- Show prediction score with color coding
- Trigger gazing animation on new predictions
- Render mystical message

**Props:**
```javascript
{
    prediction: {
        prediction_score: number,
        mystical_message: string
    } | null
}
```

#### 3. Omens Feed Component (`OmensFeed.jsx`)

**Responsibilities:**
- Display list of omens
- Map omen types to icons
- Show severity badges
- Handle empty state

**Props:**
```javascript
{
    omens: Array<{
        type: 'minor' | 'major' | 'dark',
        title: string,
        description: string,
        file: string,
        severity: number
    }>
}
```

#### 4. History Component (`History.jsx`)

**Responsibilities:**
- Display recent predictions (max 10)
- Show prediction scores and messages
- Maintain chronological order

**Props:**
```javascript
{
    history: Array<{
        prediction_score: number,
        mystical_message: string,
        timestamp: string
    }>
}
```

#### 5. App Component (`App.jsx`)

**Responsibilities:**
- Manage WebSocket connection
- Maintain prediction history state
- Coordinate child components
- Display connection status

## Data Models

### Database Schema

**predictions table:**
```sql
CREATE TABLE predictions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    pr_url TEXT NOT NULL,
    pr_number INTEGER NOT NULL,
    repo TEXT NOT NULL,
    prediction_score INTEGER NOT NULL CHECK (prediction_score >= 0 AND prediction_score <= 100),
    mystical_message TEXT NOT NULL,
    recommendations JSONB NOT NULL DEFAULT '[]',
    files_changed INTEGER NOT NULL,
    lines_added INTEGER NOT NULL,
    lines_removed INTEGER NOT NULL,
    files_renamed INTEGER DEFAULT 0,
    binary_files INTEGER DEFAULT 0,
    actual_result BOOLEAN,
    accurate BOOLEAN,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_predictions_timestamp ON predictions(timestamp DESC);
CREATE INDEX idx_predictions_repo ON predictions(repo);
CREATE INDEX idx_predictions_pr_number ON predictions(pr_number);
```

**omens table:**
```sql
CREATE TABLE omens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    prediction_id UUID NOT NULL REFERENCES predictions(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN ('minor', 'major', 'dark')),
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    file TEXT NOT NULL,
    severity INTEGER NOT NULL CHECK (severity >= 1 AND severity <= 10),
    historical_failures INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_omens_prediction_id ON omens(prediction_id);
CREATE INDEX idx_omens_type ON omens(type);
```

### Prediction Model

```python
{
    'id': str,  # UUID
    'timestamp': datetime,
    'pr_url': str,
    'pr_number': int,
    'repo': str,
    'prediction_score': int,  # 0-100
    'omens': [Omen],
    'mystical_message': str,
    'recommendations': [str],
    'context': {
        'files_changed': int,
        'lines_added': int,
        'lines_removed': int,
        'files_renamed': int,
        'binary_files': int
    },
    'actual_result': Optional[bool],  # None until outcome known
    'accurate': Optional[bool]  # None until outcome known
}
```

### Omen Model

```python
{
    'type': str,  # 'minor' | 'major' | 'dark'
    'title': str,
    'description': str,
    'file': str,
    'severity': int,  # 1-10
    'historical_failures': Optional[int]  # Added by Prediction Engine
}
```

### GitHub Webhook Payload (Relevant Fields)

```python
{
    'action': str,  # 'opened' | 'synchronize' | 'closed'
    'pull_request': {
        'number': int,
        'url': str,
        'diff_url': str,
        'comments_url': str,
        'title': str,
        'user': {
            'login': str
        }
    },
    'repository': {
        'full_name': str
    }
}
```

### WebSocket Message Format

```javascript
{
    prediction_score: number,
    omens: Array<{
        type: string,
        title: string,
        description: string,
        file: string,
        severity: number
    }>,
    mystical_message: string,
    recommendations: Array<string>,
    timestamp: string
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: PR Event Processing Completeness

*For any* GitHub PR event (opened or synchronized), the system should fetch the PR diff from the GitHub API.

**Validates: Requirements 1.2**

### Property 2: Diff Parsing Completeness

*For any* valid PR diff, the system should extract files_changed, lines_added, and lines_removed as non-negative integers.

**Validates: Requirements 1.3**

### Property 3: Analysis Completion Triggers Comment

*For any* completed code analysis, the system should post a formatted comment to the GitHub PR.

**Validates: Requirements 1.4**

### Property 4: Prediction Broadcast

*For any* generated prediction, the system should broadcast it to all connected WebSocket clients.

**Validates: Requirements 1.5**

### Property 5: LLM API Invocation

*For any* code diff received by the AI Analyzer, the system should send it to the LLM API with a structured prompt.

**Validates: Requirements 2.1**

### Property 6: Prediction Score Range

*For any* LLM response, the prediction score should be between 0 and 100 (inclusive).

**Validates: Requirements 2.2**

### Property 7: Omen Structure Completeness

*For any* omen generated by the AI Analyzer, it should contain type, title, description, file, and severity fields.

**Validates: Requirements 2.3**

### Property 8: Omen Classification Correctness

*For any* severity value, the omen type should be: minor if severity is 1-3, major if severity is 4-7, dark if severity is 8-10.

**Validates: Requirements 2.4**

### Property 9: Prediction Storage

*For any* prediction made, the Prediction Engine should store it in memory with timestamp, prediction details, and all required fields.

**Validates: Requirements 3.1**

### Property 10: Outcome Recording

*For any* deployment outcome recorded, the corresponding prediction in history should be updated with the actual result.

**Validates: Requirements 3.2**

### Property 11: Accuracy Calculation Correctness

*For any* history with recorded outcomes, the accuracy rate should equal (number of accurate predictions / total predictions with outcomes) * 100.

**Validates: Requirements 3.3**

### Property 12: Historical Severity Enhancement

*For any* omen with a pattern that has caused failures previously, the severity should be increased by min(2, failure_count) points (not exceeding 10).

**Validates: Requirements 3.4**

### Property 13: Historical Annotation

*For any* omen with more than 3 historical failures, the description should be annotated with the failure count.

**Validates: Requirements 3.5**

### Property 14: Crystal Ball Animation Trigger

*For any* new prediction received by the Dashboard, the crystal ball should trigger the gazing animation.

**Validates: Requirements 4.2**

### Property 15: Score Color Coding

*For any* prediction score, the color should be: green if score >= 80, yellow if 60 <= score < 80, red if score < 60.

**Validates: Requirements 4.3**

### Property 16: Omen Icon Mapping

*For any* omen displayed, the icon should be: ⚠️ for minor, 🔥 for major, ☠️ for dark.

**Validates: Requirements 4.4**

### Property 17: Recommendations Display

*For any* non-empty recommendations array, the Dashboard should display the mystical guidance section.

**Validates: Requirements 4.6**

### Property 18: WebSocket Connection Registration

*For any* WebSocket connection attempt, the server should accept it and add it to the active connections list.

**Validates: Requirements 5.1**

### Property 19: Broadcast to All Clients

*For any* prediction generated, the WebSocket server should send it to all active connections.

**Validates: Requirements 5.2**

### Property 20: Connection Cleanup

*For any* WebSocket connection that drops, the server should remove it from the active connections list.

**Validates: Requirements 5.3**

### Property 21: Client Reconnection Backoff

*For any* WebSocket disconnect on the client, the Dashboard should attempt reconnection with exponential backoff: 1s, 2s, 4s, 8s, capped at 30s.

**Validates: Requirements 5.4**

### Property 22: UI Update on Prediction

*For any* prediction received via WebSocket, the Dashboard should update the crystal ball and omens feed state.

**Validates: Requirements 5.5**

### Property 23: Connection Status Accuracy

*For any* WebSocket connection state, the displayed status should match the actual connection state (connected/disconnected).

**Validates: Requirements 5.6**

### Property 24: History Addition

*For any* new prediction received, the Dashboard should add it to the history list.

**Validates: Requirements 6.1**

### Property 25: History Size Constraint

*For any* history list state, the length should never exceed 10 items.

**Validates: Requirements 6.2**

### Property 26: History Entry Completeness

*For any* history entry displayed, it should contain prediction_score and mystical_message fields.

**Validates: Requirements 6.3**

### Property 27: Accuracy Display

*For any* accuracy metric received from the backend, the Dashboard should display it.

**Validates: Requirements 6.4**

### Property 28: Webhook Signature Validation

*For any* webhook request received, the GitHub Webhook Handler should validate the signature using HMAC-SHA256.

**Validates: Requirements 7.1**

### Property 29: Invalid Signature Rejection

*For any* webhook request with invalid signature, the handler should return 401 status.

**Validates: Requirements 7.2**

### Property 30: Non-PR Event Filtering

*For any* webhook event that is not PR-related (opened/synchronize), the handler should ignore it without error.

**Validates: Requirements 7.3**

### Property 31: Event Logging

*For any* webhook event processed, the system should log it with timestamp and action type.

**Validates: Requirements 7.4**

### Property 32: GitHub API Retry Logic

*For any* GitHub API failure, the system should retry up to 3 times with exponential backoff (1s, 2s, 4s).

**Validates: Requirements 8.1**

### Property 33: GitHub Rate Limit Handling

*For any* GitHub API rate limit response, the system should wait for the reset time before retrying.

**Validates: Requirements 8.2**

### Property 34: LLM Fallback Prediction

*For any* LLM API failure, the AI Analyzer should return a fallback prediction with 50% score and a generic warning omen.

**Validates: Requirements 8.3**

### Property 35: LLM Rate Limit Queueing

*For any* LLM API rate limit response, the system should queue the request for retry after the appropriate delay.

**Validates: Requirements 8.4**

### Property 36: Broadcast Error Isolation

*For any* WebSocket connection that fails during broadcast, the server should remove it and continue broadcasting to remaining connections.

**Validates: Requirements 8.5**

### Property 37: Error Logging

*For any* error encountered, the system should log it with full context (component, operation, error details).

**Validates: Requirements 8.6**

### Property 38: Health Endpoint Response

*For any* health endpoint query, the response should contain status, accuracy_rate, and predictions_made fields.

**Validates: Requirements 8.7**

### Property 39: Sensitive Data Protection

*For any* log entry, it should not contain sensitive values (API keys, tokens).

**Validates: Requirements 9.5**

### Property 40: Webhook Payload Validation

*For any* webhook payload received, the handler should validate that required fields (action, pull_request) exist.

**Validates: Requirements 11.1**

### Property 41: Malformed Payload Rejection

*For any* malformed JSON webhook payload, the handler should return 400 status with error message.

**Validates: Requirements 11.2**

### Property 42: LLM Response Validation

*For any* LLM response, the AI Analyzer should validate that it contains prediction_score, omens, and mystical_message fields.

**Validates: Requirements 11.3**

### Property 43: Malformed LLM Response Fallback

*For any* LLM response missing required fields, the AI Analyzer should return a fallback prediction.

**Validates: Requirements 11.4**

### Property 44: Prediction Serialization Round-Trip

*For any* prediction object, serializing to JSON and deserializing should produce an equivalent object with all fields preserved.

**Validates: Requirements 11.5**

### Property 45: Database Prediction Round-Trip

*For any* prediction, saving it to the database and then retrieving it should produce an equivalent prediction with all fields preserved.

**Validates: Requirements 13.2**

### Property 46: Historical Data Ordering

*For any* set of predictions with different timestamps, querying historical data should return them ordered by timestamp descending (newest first).

**Validates: Requirements 13.4**

### Property 47: Rate Limiter Request Tracking

*For any* sequence of requests from an IP address, the rate limiter should accurately track the request count within the sliding time window.

**Validates: Requirements 14.1**

### Property 48: Rate Limited Response Headers

*For any* request that is rate limited, the response should include a Retry-After header with the appropriate wait time.

**Validates: Requirements 14.4**

### Property 49: Rate Limit Logging

*For any* rate-limited request, the system should create a log entry containing the IP address and timestamp.

**Validates: Requirements 14.5**

### Property 50: Renamed File Detection

*For any* PR diff containing renamed files, the system should correctly detect the rename operation and count it as one file changed.

**Validates: Requirements 15.1**

### Property 51: Binary File Exclusion

*For any* PR diff containing binary files, the system should identify them and exclude them from line count calculations (lines_added and lines_removed should not include binary file changes).

**Validates: Requirements 15.2**

### Property 52: Diff Statistics Accuracy

*For any* valid PR diff, the extracted statistics (files_changed, lines_added, lines_removed, files_renamed, binary_files) should accurately reflect the diff content.

**Validates: Requirements 15.3**

### Property 53: Health Check Database Status

*For any* health check request, the response should include database connectivity status.

**Validates: Requirements 16.1**

### Property 54: Health Check WebSocket Status

*For any* health check request, the response should include WebSocket server status and active connection count.

**Validates: Requirements 16.2**

### Property 55: Health Check GitHub API Status

*For any* health check request, the response should include GitHub API accessibility and rate limit status.

**Validates: Requirements 16.3**

### Property 56: Health Check LLM API Status

*For any* health check request, the response should include LLM API service status.

**Validates: Requirements 16.4**

### Property 57: Unhealthy Component Status Code

*For any* health check where at least one component is unhealthy, the response status code should be 503 and include details of failing components.

**Validates: Requirements 16.5**

## Error Handling

### GitHub API Errors

**Retry Strategy:**
- Exponential backoff: 1s, 2s, 4s
- Maximum 3 retry attempts
- Log each retry attempt with context

**Rate Limiting:**
- Parse `X-RateLimit-Remaining` and `X-RateLimit-Reset` headers
- If rate limit exceeded, wait until reset time
- Log rate limit events for monitoring

**Network Errors:**
- Catch `httpx.RequestError` for connection failures
- Retry with backoff
- Return error to caller after max retries

### LLM API Errors

**Fallback Prediction:**
```python
{
    'prediction_score': 50,
    'omens': [{
        'type': 'major',
        'title': 'Analysis Unavailable',
        'description': 'The mystical oracle is temporarily unavailable. Please review changes manually.',
        'file': 'unknown',
        'severity': 5
    }],
    'mystical_message': 'The spirits are silent... Proceed with caution.',
    'recommendations': ['Review changes carefully', 'Run tests locally']
}
```

**Rate Limiting:**
- Parse rate limit headers from Anthropic API
- Queue requests when rate limited
- Implement simple in-memory queue with retry logic

**Validation Errors:**
- If LLM returns invalid JSON, use fallback
- If required fields missing, use fallback
- Log all validation failures

### WebSocket Errors

**Server-Side:**
- Catch exceptions during broadcast
- Remove failed connections from active list
- Continue broadcasting to remaining clients
- Log connection failures

**Client-Side:**
- Detect connection close events
- Implement exponential backoff: 1s, 2s, 4s, 8s, 16s, 30s (max)
- Reset backoff on successful connection
- Display connection status to user

### JSON Parsing Errors

**Webhook Payloads:**
- Validate JSON structure before processing
- Check for required fields (action, pull_request)
- Return 400 with clear error message
- Log malformed payloads for debugging

**LLM Responses:**
- Wrap JSON parsing in try-catch
- Validate schema after parsing
- Use fallback prediction on failure
- Log parsing errors

### Configuration Errors

**Startup Validation:**
- Check for required environment variables
- Fail fast with clear error messages
- Don't start server if config invalid
- Example: "GITHUB_TOKEN environment variable is required"

## Testing Strategy

### Unit Testing

**Framework:** pytest for Python, Vitest for JavaScript

**Backend Unit Tests:**
- `test_github_handler.py`: Test signature validation, payload parsing, diff extraction
- `test_ai_analyzer.py`: Test omen classification, fallback generation, prompt construction
- `test_prediction_engine.py`: Test accuracy calculation, pattern tracking, enhancement logic
- `test_websocket_manager.py`: Test connection management, broadcast logic

**Frontend Unit Tests:**
- `CrystalBall.test.jsx`: Test color coding logic, animation triggers
- `OmensFeed.test.jsx`: Test icon mapping, empty state
- `History.test.jsx`: Test size constraint, entry display
- `useWebSocket.test.js`: Test reconnection backoff logic

**Key Unit Test Examples:**
- Test omen classification with boundary values (3, 4, 7, 8)
- Test accuracy calculation with various history scenarios
- Test history size constraint (adding 11th item)
- Test color coding with boundary scores (60, 80)

### Property-Based Testing

**Framework:** Hypothesis for Python, fast-check for JavaScript

**Configuration:**
- Minimum 100 iterations per property test
- Use shrinking to find minimal failing examples
- Tag each test with property number from design doc

**Python Property Tests:**

1. **Property 8: Omen Classification** - Generate random severity values (1-10), verify correct type assignment
2. **Property 11: Accuracy Calculation** - Generate random histories with outcomes, verify accuracy formula
3. **Property 12: Severity Enhancement** - Generate random omens with failure counts, verify severity increase (max +2, cap at 10)
4. **Property 15: Score Color Coding** - Generate random scores (0-100), verify correct color
5. **Property 25: History Size Constraint** - Generate random prediction sequences, verify history never exceeds 10
6. **Property 44: Prediction Serialization** - Generate random predictions, verify round-trip (serialize → deserialize → equal)

**JavaScript Property Tests:**

1. **Property 16: Omen Icon Mapping** - Generate random omen types, verify correct icon
2. **Property 21: Reconnection Backoff** - Generate random disconnect sequences, verify backoff sequence
3. **Property 25: History Size** - Generate random prediction additions, verify max 10 items

**Test Tagging Format:**
```python
# Feature: crystal-ball-cicd, Property 8: Omen Classification Correctness
@given(st.integers(min_value=1, max_value=10))
def test_omen_classification(severity):
    ...
```

### Integration Testing

**End-to-End Flow:**
1. Send mock GitHub webhook
2. Verify diff fetching (mock GitHub API)
3. Verify LLM call (mock Anthropic API)
4. Verify prediction enhancement
5. Verify WebSocket broadcast
6. Verify PR comment posting

**WebSocket Integration:**
- Test multiple client connections
- Test broadcast to all clients
- Test connection cleanup on disconnect
- Test client reconnection

**Error Scenarios:**
- Test GitHub API failure with retries
- Test LLM API failure with fallback
- Test malformed webhook payloads
- Test malformed LLM responses

### Manual Testing

**Local Setup:**
1. Start backend: `uvicorn main:app --reload`
2. Start frontend: `npm run dev`
3. Start ngrok: `ngrok http 8000`
4. Configure GitHub webhook with ngrok URL

**Test Scenarios:**
- Create PR with small changes (expect high score)
- Create PR with large changes (expect medium score)
- Create PR with security issues (expect low score, dark omens)
- Test WebSocket reconnection (stop/start backend)
- Test multiple browser tabs (multiple WebSocket clients)

**Validation:**
- Check GitHub PR comments appear
- Check dashboard updates in real-time
- Check history accumulates correctly
- Check accuracy metrics update
- Check error handling (disconnect backend, check reconnection)


## Implementation Notes

### LLM Prompt Engineering

**Prompt Structure:**
```
You are a mystical code oracle analyzing pull request changes.

Code Diff:
{diff}

Context:
- Files changed: {files_changed}
- Lines added: {lines_added}
- Lines removed: {lines_removed}
- Repository: {repo}

Analyze this diff and predict potential deployment issues.

Return ONLY valid JSON (no markdown, no code blocks) with this exact structure:
{
    "prediction_score": <number 0-100, where 100 = certain success>,
    "omens": [
        {
            "type": "minor|major|dark",
            "title": "<brief warning>",
            "description": "<detailed explanation in mystical but clear language>",
            "file": "<affected file path>",
            "severity": <number 1-10>
        }
    ],
    "mystical_message": "<fortune teller style summary, avoid technical jargon>",
    "recommendations": ["<actionable suggestion>", ...]
}

Guidelines:
- Use mystical language but keep it understandable
- Severity 1-3: minor issues (code smells, style)
- Severity 4-7: major issues (potential bugs, breaking changes)
- Severity 8-10: dark omens (security, critical failures)
- Empty omens array if no issues found
- Mystical message should be encouraging for high scores, cautionary for low scores
```

### WebSocket Reconnection Logic

**Client-Side Implementation:**
```javascript
class WebSocketClient {
    constructor(url) {
        this.url = url;
        this.ws = null;
        this.reconnectAttempt = 0;
        this.maxBackoff = 30000; // 30 seconds
        this.backoffSequence = [1000, 2000, 4000, 8000, 16000];
    }
    
    connect() {
        this.ws = new WebSocket(this.url);
        
        this.ws.onopen = () => {
            console.log('Connected');
            this.reconnectAttempt = 0; // Reset on success
        };
        
        this.ws.onclose = () => {
            console.log('Disconnected');
            this.scheduleReconnect();
        };
        
        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }
    
    scheduleReconnect() {
        const delay = this.reconnectAttempt < this.backoffSequence.length
            ? this.backoffSequence[this.reconnectAttempt]
            : this.maxBackoff;
            
        console.log(`Reconnecting in ${delay}ms...`);
        
        setTimeout(() => {
            this.reconnectAttempt++;
            this.connect();
        }, delay);
    }
}
```

### GitHub Webhook Signature Validation

**Implementation:**
```python
import hmac
import hashlib

def validate_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Validate GitHub webhook signature using HMAC-SHA256
    
    Args:
        payload: Raw request body bytes
        signature: X-Hub-Signature-256 header value (format: "sha256=<hash>")
        secret: Webhook secret from environment
    
    Returns:
        True if signature is valid, False otherwise
    """
    if not signature or not signature.startswith('sha256='):
        return False
    
    expected_signature = signature.split('=')[1]
    
    mac = hmac.new(
        secret.encode('utf-8'),
        msg=payload,
        digestmod=hashlib.sha256
    )
    
    computed_signature = mac.hexdigest()
    
    return hmac.compare_digest(computed_signature, expected_signature)
```

### In-Memory Data Storage

**Prediction Engine Storage:**
```python
class PredictionEngine:
    def __init__(self):
        # List of prediction dictionaries
        self.history: List[dict] = []
        
        # Pattern failure tracking: "type:file" -> count
        self.pattern_failures: Dict[str, int] = defaultdict(int)
        
        # Maximum history size (optional, for memory management)
        self.max_history = 1000
    
    def store_prediction(self, prediction: dict) -> None:
        """Store prediction with UUID and timestamp"""
        prediction['id'] = str(uuid.uuid4())
        prediction['timestamp'] = datetime.now().isoformat()
        prediction['actual_result'] = None
        prediction['accurate'] = None
        
        self.history.append(prediction)
        
        # Trim history if too large
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
```

### Environment Configuration

**Required Environment Variables:**
```bash
# .env file
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx
GITHUB_WEBHOOK_SECRET=your_webhook_secret_here

# Optional
FRONTEND_URL=http://localhost:5173
LOG_LEVEL=INFO
```

**Loading Configuration:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

# Validate required variables
required_vars = ['GITHUB_TOKEN', 'ANTHROPIC_API_KEY', 'GITHUB_WEBHOOK_SECRET']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# Load configuration
config = {
    'github_token': os.getenv('GITHUB_TOKEN'),
    'anthropic_api_key': os.getenv('ANTHROPIC_API_KEY'),
    'webhook_secret': os.getenv('GITHUB_WEBHOOK_SECRET'),
    'frontend_url': os.getenv('FRONTEND_URL', 'http://localhost:5173'),
    'log_level': os.getenv('LOG_LEVEL', 'INFO')
}
```

### CORS Configuration

**FastAPI CORS Setup:**
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://127.0.0.1:5173"   # Alternative localhost
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Logging Configuration

**Structured Logging:**
```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            'timestamp': datetime.now().isoformat(),
            'level': record.levelname,
            'component': record.name,
            'message': record.getMessage(),
        }
        
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Redact sensitive data
        message = log_data['message']
        if 'token' in message.lower() or 'key' in message.lower():
            log_data['message'] = '[REDACTED]'
        
        return json.dumps(log_data)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    handlers=[
        logging.StreamHandler()
    ]
)

for handler in logging.root.handlers:
    handler.setFormatter(JSONFormatter())
```

## Deployment

### Local Development Setup

**Prerequisites:**
- Python 3.11+
- Node.js 18+
- ngrok account (free tier)

**Backend Setup:**
```bash
# Create project directory
mkdir crystal-ball-ci
cd crystal-ball-ci

# Create backend directory
mkdir backend
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux

# Install dependencies
pip install fastapi uvicorn anthropic httpx websockets python-dotenv

# Create requirements.txt
pip freeze > requirements.txt

# Create .env file
cat > .env << EOF
GITHUB_TOKEN=your_token_here
ANTHROPIC_API_KEY=your_key_here
GITHUB_WEBHOOK_SECRET=your_secret_here
EOF
```

**Frontend Setup:**
```bash
# From project root
mkdir frontend
cd frontend

# Create Vite React app
npm create vite@latest . -- --template react

# Install dependencies
npm install

# Start dev server (test)
npm run dev
```

**Running the System:**

Terminal 1 - Backend:
```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

Terminal 3 - ngrok:
```bash
ngrok http 8000
# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
```

**GitHub Webhook Configuration:**
1. Go to your test repository settings
2. Navigate to Webhooks → Add webhook
3. Payload URL: `https://abc123.ngrok.io/webhook/github`
4. Content type: `application/json`
5. Secret: (same as GITHUB_WEBHOOK_SECRET in .env)
6. Events: Select "Pull requests"
7. Active: ✓

### Testing the System

**Create Test PR:**
```bash
# In your test repository
git checkout -b test-prediction
echo "console.log('test');" > test.js
git add test.js
git commit -m "Add test file"
git push origin test-prediction

# Create PR via GitHub UI
```

**Expected Behavior:**
1. GitHub sends webhook to ngrok URL
2. Backend receives webhook, fetches diff
3. AI Analyzer calls Claude API
4. Prediction Engine enhances prediction
5. Backend posts comment to PR
6. Backend broadcasts to WebSocket clients
7. Dashboard updates in real-time

**Verification:**
- Check backend logs for webhook receipt
- Check PR for Crystal Ball comment
- Check dashboard for prediction display
- Check browser console for WebSocket messages

### Performance Considerations

**Backend:**
- FastAPI is async, handles concurrent requests well
- LLM API calls are the bottleneck (~2-5 seconds)
- In-memory storage is fast but limited by RAM
- For production, consider Redis for history storage

**Frontend:**
- React renders are fast for small data
- WebSocket updates are near-instant
- CSS animations use GPU acceleration
- History limited to 10 items for performance

**Scalability:**
- MVP handles ~10 concurrent PRs comfortably
- LLM API rate limits are the main constraint
- For higher load, implement request queueing
- Consider caching LLM responses for similar diffs

### Security Considerations

**Webhook Security:**
- Always validate GitHub signatures
- Use HTTPS for webhook endpoint (ngrok provides this)
- Don't log webhook payloads (may contain sensitive code)

**API Keys:**
- Store in environment variables, never in code
- Use .env file for local development
- Add .env to .gitignore
- Rotate keys regularly

**CORS:**
- Restrict to specific frontend origins
- Don't use wildcard (*) in production
- Validate origin headers

**Logging:**
- Redact sensitive data (tokens, keys)
- Don't log full diffs (may contain secrets)
- Use structured logging for easier filtering

## Future Enhancements

**Beyond MVP:**
1. **Persistent Storage**: Replace in-memory storage with PostgreSQL or Redis
2. **User Authentication**: Add login system for multi-user support
3. **Multiple Repositories**: Support monitoring multiple repos simultaneously
4. **Custom Rules**: Allow users to define custom omen patterns
5. **Slack/Discord Integration**: Send predictions to team chat
6. **Historical Analytics**: Visualize accuracy trends over time
7. **A/B Testing**: Compare different LLM models or prompts
8. **Caching**: Cache LLM responses for similar diffs
9. **Batch Processing**: Handle multiple PRs in parallel
10. **Mobile App**: Native mobile dashboard

**Technical Debt to Address:**
- Add database migrations
- Implement proper authentication/authorization
- Add comprehensive error monitoring (Sentry)
- Set up CI/CD pipeline
- Add performance monitoring
- Implement rate limiting on endpoints
- Add request/response validation with Pydantic models
- Improve test coverage to >80%

