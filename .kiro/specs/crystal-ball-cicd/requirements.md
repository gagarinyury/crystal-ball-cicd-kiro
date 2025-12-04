# Requirements Document

## Introduction

Crystal Ball CI/CD is an AI-powered continuous integration and deployment monitoring system with a mystical user interface. The system analyzes GitHub pull requests in real-time, predicts potential deployment issues before they occur, and presents predictions through an engaging, fortune-teller themed dashboard. The system integrates with GitHub Actions, uses LLM-based code analysis, and provides actionable warnings categorized by severity.

## Glossary

- **Crystal Ball System**: The complete AI-powered CI/CD monitoring application
- **Omen**: A warning or prediction about potential code issues, categorized by severity (Minor, Major, Dark)
- **Prediction Score**: A numerical value (0-100%) indicating the likelihood of successful deployment
- **GitHub Webhook Handler**: The backend component that receives and processes GitHub events
- **AI Analyzer**: The component that uses LLM APIs to analyze code changes and generate predictions
- **Prediction Engine**: The component that combines AI analysis with historical data to enhance predictions
- **Dashboard**: The React-based frontend that displays predictions and omens
- **WebSocket Server**: The real-time communication channel between backend and frontend
- **PR Diff**: The code changes in a GitHub pull request
- **Historical Data**: Past predictions and their actual outcomes used for accuracy tracking

## Requirements

### Requirement 1

**User Story:** As a developer, I want to receive real-time predictions about my pull request's deployment success, so that I can identify and fix issues before merging.

#### Acceptance Criteria

1. WHEN a pull request is opened or updated THEN the Crystal Ball System SHALL receive the GitHub webhook event within 5 seconds
2. WHEN the Crystal Ball System receives a PR event THEN the Crystal Ball System SHALL fetch the complete PR diff from GitHub API
3. WHEN the PR diff is fetched THEN the Crystal Ball System SHALL extract changed files, lines added, and lines removed
4. WHEN code analysis completes THEN the Crystal Ball System SHALL post a formatted comment to the GitHub PR with predictions
5. WHEN the prediction is generated THEN the Crystal Ball System SHALL broadcast the prediction to all connected dashboard clients via WebSocket

### Requirement 2

**User Story:** As a developer, I want to see AI-generated predictions with specific warnings about my code changes, so that I understand what might go wrong and why.

#### Acceptance Criteria

1. WHEN the AI Analyzer receives a code diff THEN the AI Analyzer SHALL send the diff to the LLM API with structured prompt
2. WHEN the LLM processes the code diff THEN the AI Analyzer SHALL receive a prediction score between 0 and 100
3. WHEN the LLM identifies potential issues THEN the AI Analyzer SHALL generate omens with type, title, description, affected file, and severity (1-10)
4. WHEN omens are classified THEN the AI Analyzer SHALL assign minor type for severity 1-3, major type for severity 4-7, and dark type for severity 8-10
5. WHEN the analysis completes THEN the AI Analyzer SHALL return a mystical-themed message that is understandable without technical jargon
6. WHEN the AI Analyzer generates recommendations THEN the AI Analyzer SHALL provide actionable suggestions for improving code quality

### Requirement 3

**User Story:** As a developer, I want the system to learn from past predictions and actual outcomes, so that predictions become more accurate over time.

#### Acceptance Criteria

1. WHEN a prediction is made THEN the Prediction Engine SHALL store the prediction in memory as a Python dictionary with timestamp and details
2. WHEN a deployment outcome is known THEN the Prediction Engine SHALL record the actual result alongside the prediction in the history list
3. WHEN historical data exists THEN the Prediction Engine SHALL calculate overall prediction accuracy rate as a percentage
4. WHEN the same code pattern caused failures previously THEN the Prediction Engine SHALL increase the severity of related omens by up to 2 points
5. WHEN enhancing a prediction THEN the Prediction Engine SHALL annotate omens with historical failure counts if the count exceeds 3

### Requirement 4

**User Story:** As a developer, I want to view predictions through an engaging mystical dashboard, so that monitoring CI/CD becomes more intuitive and enjoyable.

#### Acceptance Criteria

1. WHEN the Dashboard loads THEN the Dashboard SHALL display a crystal ball visualization with floating animation
2. WHEN a new prediction arrives THEN the Dashboard SHALL animate the crystal ball with a gazing effect
3. WHEN displaying the prediction score THEN the Dashboard SHALL color-code the score (green for 80+, yellow for 60-79, red below 60)
4. WHEN omens exist THEN the Dashboard SHALL display each omen with appropriate icon (⚠️ minor, 🔥 major, ☠️ dark)
5. WHEN no omens are present THEN the Dashboard SHALL display a calm message indicating all is well
6. WHEN recommendations are available THEN the Dashboard SHALL display them in a mystical guidance section

### Requirement 5

**User Story:** As a developer, I want real-time updates on my dashboard without refreshing, so that I can monitor multiple PRs simultaneously.

#### Acceptance Criteria

1. WHEN the Dashboard connects to the backend THEN the WebSocket Server SHALL accept the connection and add it to active connections
2. WHEN a prediction is generated THEN the WebSocket Server SHALL broadcast the prediction to all connected clients
3. WHEN a WebSocket connection drops on the server THEN the WebSocket Server SHALL remove it from active connections
4. WHEN a WebSocket connection drops on the client THEN the Dashboard SHALL automatically attempt to reconnect with exponential backoff (1s, 2s, 4s, 8s, max 30s)
5. WHEN the Dashboard receives a prediction via WebSocket THEN the Dashboard SHALL update the crystal ball and omens feed immediately
6. WHEN the Dashboard displays connection status THEN the Dashboard SHALL show connected or disconnected state accurately

### Requirement 6

**User Story:** As a developer, I want to see historical predictions on the dashboard, so that I can track patterns and accuracy over time.

#### Acceptance Criteria

1. WHEN a new prediction is received THEN the Dashboard SHALL add it to the history list
2. WHEN the history list exceeds 10 items THEN the Dashboard SHALL keep only the 10 most recent predictions
3. WHEN displaying history THEN the Dashboard SHALL show prediction score and mystical message for each entry
4. WHEN the backend provides accuracy metrics THEN the Dashboard SHALL display the overall accuracy rate

### Requirement 7

**User Story:** As a system administrator, I want the backend to handle GitHub webhook security, so that only authentic GitHub events are processed.

#### Acceptance Criteria

1. WHEN the GitHub Webhook Handler receives a webhook request THEN the GitHub Webhook Handler SHALL validate the webhook signature using the configured secret
2. WHEN the webhook signature is invalid THEN the GitHub Webhook Handler SHALL reject the request with 401 status
3. WHEN the webhook event type is not PR-related THEN the GitHub Webhook Handler SHALL ignore the event gracefully
4. WHEN processing webhook events THEN the GitHub Webhook Handler SHALL log all events with timestamp and action type

### Requirement 8

**User Story:** As a developer, I want the system to handle errors gracefully, so that temporary failures do not break the monitoring workflow.

#### Acceptance Criteria

1. WHEN the GitHub API is unavailable THEN the Crystal Ball System SHALL retry the request up to 3 times with exponential backoff (1s, 2s, 4s)
2. WHEN the GitHub API rate limit is exceeded THEN the Crystal Ball System SHALL wait for the rate limit reset time before retrying
3. WHEN the LLM API fails THEN the AI Analyzer SHALL return a fallback prediction with 50% score and generic warning
4. WHEN the LLM API rate limit is exceeded THEN the AI Analyzer SHALL queue the request and retry after the appropriate delay
5. WHEN a WebSocket connection fails during broadcast THEN the WebSocket Server SHALL remove the failed connection and continue broadcasting to others
6. WHEN any component encounters an error THEN the Crystal Ball System SHALL log the error with full context for debugging
7. WHEN the backend health endpoint is queried THEN the Crystal Ball System SHALL return status, accuracy rate, and prediction count

### Requirement 9

**User Story:** As a developer, I want to configure the system with my GitHub token and AI API key, so that the system can access necessary services securely.

#### Acceptance Criteria

1. WHEN the Crystal Ball System starts THEN the Crystal Ball System SHALL load configuration from environment variables
2. WHEN the GITHUB_TOKEN is missing THEN the Crystal Ball System SHALL fail to start with clear error message
3. WHEN the ANTHROPIC_API_KEY is missing THEN the Crystal Ball System SHALL fail to start with clear error message
4. WHEN CORS is configured THEN the Crystal Ball System SHALL allow requests from the frontend origin
5. WHEN environment variables are loaded THEN the Crystal Ball System SHALL not log sensitive values

### Requirement 10

**User Story:** As a developer, I want to run the entire system locally on my Mac, so that I can develop and test without cloud deployment.

#### Acceptance Criteria

1. WHEN the backend starts with uvicorn THEN the Crystal Ball System SHALL listen on port 8000
2. WHEN the frontend starts with Vite THEN the Dashboard SHALL be accessible on port 5173
3. WHEN ngrok tunnels the backend THEN the GitHub Webhook Handler SHALL be accessible via public HTTPS URL
4. WHEN all components are running THEN the Crystal Ball System SHALL provide end-to-end functionality from GitHub webhook to dashboard display
5. WHEN the health endpoint is accessed THEN the Crystal Ball System SHALL respond with alive status

### Requirement 11

**User Story:** As a developer, I want the system to validate all JSON data correctly, so that malformed payloads do not cause crashes.

#### Acceptance Criteria

1. WHEN the GitHub Webhook Handler receives a webhook payload THEN the GitHub Webhook Handler SHALL parse the JSON and validate required fields exist
2. WHEN the GitHub webhook payload is malformed THEN the GitHub Webhook Handler SHALL reject the request with 400 status and error message
3. WHEN the AI Analyzer receives LLM response THEN the AI Analyzer SHALL parse the JSON and validate the response schema
4. WHEN the LLM response is malformed or missing required fields THEN the AI Analyzer SHALL return a fallback prediction
5. WHEN serializing prediction data for WebSocket THEN the Crystal Ball System SHALL ensure the data is valid JSON before sending
