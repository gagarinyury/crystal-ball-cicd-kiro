# Implementation Plan

- [x] 1. Set up project structure and configuration
  - Create backend directory with Python virtual environment
  - Create frontend directory with Vite + React
  - Set up .env file with environment variables (GITHUB_TOKEN, ANTHROPIC_API_KEY, GITHUB_WEBHOOK_SECRET)
  - Create requirements.txt for backend dependencies
  - Create .gitignore to exclude .env, venv, node_modules
  - _Requirements: 9.1, 9.2, 9.3, 10.1, 10.2_

- [x] 2. Implement data models and core types
  - [x] 2.1 Create Pydantic models for Prediction, Omen, and WebhookPayload
    - Define Prediction model with all required fields (id, timestamp, pr_url, prediction_score, omens, etc.)
    - Define Omen model with type, title, description, file, severity
    - Define GitHub webhook payload model for validation
    - _Requirements: 11.1, 11.5_

  - [-] 2.2 Write property test for Prediction serialization round-trip
    - **Property 44: Prediction Serialization Round-Trip**
    - **Validates: Requirements 11.5**

- [x] 3. Implement GitHub Webhook Handler
  - [x] 3.1 Create GitHubHandler class with signature validation
    - Implement HMAC-SHA256 signature validation using webhook secret
    - Implement validate_signature method
    - _Requirements: 7.1, 7.2_

  - [x] 3.2 Implement webhook payload parsing and filtering
    - Parse JSON webhook payloads
    - Filter for PR events (opened, synchronize)
    - Validate required fields exist
    - Return 400 for malformed payloads
    - _Requirements: 1.2, 7.3, 11.1, 11.2_

  - [x] 3.3 Implement PR diff fetching with retry logic
    - Use httpx async client to fetch diff from GitHub API
    - Implement exponential backoff retry (1s, 2s, 4s)
    - Handle rate limiting by checking headers
    - Extract files_changed, lines_added, lines_removed from diff
    - _Requirements: 1.3, 8.1, 8.2_

  - [x] 3.4 Implement PR comment posting
    - Format prediction as GitHub comment with markdown
    - Post comment to PR using GitHub API
    - Handle API errors gracefully
    - _Requirements: 1.4_

  - [ ] 3.5 Write property test for webhook signature validation
    - **Property 28: Webhook Signature Validation**
    - **Validates: Requirements 7.1**

  - [ ] 3.6 Write property test for invalid signature rejection
    - **Property 29: Invalid Signature Rejection**
    - **Validates: Requirements 7.2**

  - [ ] 3.7 Write property test for diff parsing completeness
    - **Property 2: Diff Parsing Completeness**
    - **Validates: Requirements 1.3**

- [x] 4. Implement AI Analyzer
  - [x] 4.1 Create AIAnalyzer class with Anthropic client
    - Initialize Anthropic client with API key
    - Implement structured prompt construction
    - _Requirements: 2.1_

  - [x] 4.2 Implement code diff analysis with LLM
    - Send diff to Claude API with structured prompt
    - Parse JSON response from LLM
    - Validate response schema (prediction_score, omens, mystical_message)
    - _Requirements: 2.1, 2.2, 11.3_

  - [x] 4.3 Implement omen classification logic
    - Map severity 1-3 to "minor"
    - Map severity 4-7 to "major"
    - Map severity 8-10 to "dark"
    - _Requirements: 2.4_

  - [x] 4.4 Implement fallback prediction for API failures
    - Return fallback with 50% score and generic warning
    - Handle malformed LLM responses
    - Handle rate limiting with queueing
    - _Requirements: 8.3, 8.4, 11.4_

  - [ ] 4.5 Write property test for prediction score range
    - **Property 6: Prediction Score Range**
    - **Validates: Requirements 2.2**

  - [ ] 4.6 Write property test for omen classification correctness
    - **Property 8: Omen Classification Correctness**
    - **Validates: Requirements 2.4**

  - [ ] 4.7 Write property test for omen structure completeness
    - **Property 7: Omen Structure Completeness**
    - **Validates: Requirements 2.3**

- [x] 5. Implement Prediction Engine
  - [x] 5.1 Create PredictionEngine class with in-memory storage
    - Initialize empty history list and pattern_failures dict
    - Implement store_prediction method
    - Add UUID and timestamp to predictions
    - _Requirements: 3.1_

  - [x] 5.2 Implement outcome recording and accuracy calculation
    - Implement learn_from_outcome method
    - Calculate accuracy as (accurate / total) * 100
    - Track pattern failures by type:file
    - _Requirements: 3.2, 3.3_

  - [x] 5.3 Implement prediction enhancement with historical data
    - Increase severity for recurring patterns (max +2, cap at 10)
    - Annotate omens with failure counts if > 3
    - Recalculate prediction score based on enhanced severities
    - _Requirements: 3.4, 3.5_

  - [ ] 5.4 Write property test for accuracy calculation correctness
    - **Property 11: Accuracy Calculation Correctness**
    - **Validates: Requirements 3.3**

  - [ ] 5.5 Write property test for historical severity enhancement
    - **Property 12: Historical Severity Enhancement**
    - **Validates: Requirements 3.4**

  - [ ] 5.6 Write property test for historical annotation
    - **Property 13: Historical Annotation**
    - **Validates: Requirements 3.5**

- [x] 6. Implement WebSocket Manager
  - [x] 6.1 Create WebSocketManager class
    - Initialize empty active_connections list
    - Implement connect method to accept and register connections
    - Implement disconnect method to remove connections
    - _Requirements: 5.1, 5.3_

  - [x] 6.2 Implement broadcast functionality
    - Send prediction to all active connections
    - Handle connection failures during broadcast
    - Remove failed connections and continue broadcasting
    - _Requirements: 5.2, 8.5_

  - [ ] 6.3 Write property test for broadcast to all clients
    - **Property 19: Broadcast to All Clients**
    - **Validates: Requirements 5.2**

- [x] 7. Implement FastAPI main application
  - [x] 7.1 Create main.py with FastAPI app initialization
    - Initialize FastAPI app
    - Configure CORS for frontend origin
    - Load environment variables with validation
    - Initialize all components (GitHubHandler, AIAnalyzer, PredictionEngine, WebSocketManager)
    - _Requirements: 9.1, 9.4_

  - [x] 7.2 Implement webhook endpoint
    - POST /webhook/github endpoint
    - Validate signature
    - Process PR event
    - Trigger AI analysis
    - Enhance prediction
    - Post comment to PR
    - Broadcast to WebSocket clients
    - _Requirements: 1.1, 1.2, 1.4, 1.5_

  - [x] 7.3 Implement WebSocket endpoint
    - WS /ws endpoint
    - Accept connections
    - Handle disconnections
    - _Requirements: 5.1, 5.3_

  - [x] 7.4 Implement health check endpoint
    - GET /health endpoint
    - Return status, accuracy_rate, predictions_made
    - _Requirements: 8.7, 10.5_

  - [x] 7.5 Implement error logging with sensitive data redaction
    - Configure structured JSON logging
    - Redact API keys and tokens from logs
    - Log all errors with full context
    - _Requirements: 8.6, 9.5_

  - [ ] 7.6 Write property test for health endpoint response
    - **Property 38: Health Endpoint Response**
    - **Validates: Requirements 8.7**

  - [ ] 7.7 Write property test for sensitive data protection
    - **Property 39: Sensitive Data Protection**
    - **Validates: Requirements 9.5**

- [x] 8. Checkpoint - Ensure backend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [x] 9. Set up React frontend with Vite
  - [x] 9.1 Initialize Vite React project
    - Create frontend directory
    - Run npm create vite with React template
    - Install dependencies
    - _Requirements: 10.2_

  - [x] 9.2 Create base App component structure
    - Set up App.jsx with state management
    - Add connection status display
    - Add header with mystical styling
    - _Requirements: 4.1_

- [x] 10. Implement WebSocket client hook
  - [x] 10.1 Create useWebSocket custom hook
    - Establish WebSocket connection to backend
    - Track connection status (connected/disconnected)
    - Handle incoming messages
    - _Requirements: 5.1, 5.5, 5.6_

  - [x] 10.2 Implement auto-reconnect with exponential backoff
    - Detect connection drops
    - Implement backoff sequence: 1s, 2s, 4s, 8s, 16s, max 30s
    - Reset backoff on successful connection
    - _Requirements: 5.4_

  - [ ] 10.3 Write property test for reconnection backoff sequence
    - **Property 21: Client Reconnection Backoff**
    - **Validates: Requirements 5.4**

- [x] 11. Implement Crystal Ball component
  - [x] 11.1 Create CrystalBall.jsx component
    - Display animated crystal ball orb with floating animation
    - Show prediction score in center
    - Display mystical message below orb
    - _Requirements: 4.1_

  - [x] 11.2 Implement score color coding
    - Green for score >= 80
    - Yellow for 60 <= score < 80
    - Red for score < 60
    - _Requirements: 4.3_

  - [x] 11.3 Implement gazing animation trigger
    - Trigger animation when new prediction arrives
    - Use CSS animations for pulse and glow effects
    - _Requirements: 4.2_

  - [x] 11.4 Create CrystalBall.css with mystical styling
    - Radial gradient background
    - Floating animation keyframes
    - Pulse animation for gazing effect
    - Swirling mist animation
    - _Requirements: 4.1, 4.2_

  - [ ] 11.5 Write property test for score color coding
    - **Property 15: Score Color Coding**
    - **Validates: Requirements 4.3**

- [x] 12. Implement Omens Feed component
  - [x] 12.1 Create OmensFeed.jsx component
    - Display list of omens with cards
    - Show omen icon, title, description, file, severity
    - Handle empty state with calm message
    - _Requirements: 4.4, 4.5_

  - [x] 12.2 Implement omen icon mapping
    - ⚠️ for minor omens
    - 🔥 for major omens
    - ☠️ for dark omens
    - _Requirements: 4.4_

  - [x] 12.3 Create OmensFeed.css with mystical card styling
    - Different colors for minor/major/dark omens
    - Severity badge styling
    - Card hover effects
    - _Requirements: 4.4_

  - [ ] 12.4 Write property test for omen icon mapping
    - **Property 16: Omen Icon Mapping**
    - **Validates: Requirements 4.4**

- [x] 13. Implement History and Recommendations components
  - [x] 13.1 Create History.jsx component
    - Display recent predictions list (max 10)
    - Show prediction score and mystical message for each
    - Maintain chronological order (newest first)
    - _Requirements: 6.1, 6.2, 6.3_

  - [x] 13.2 Implement history size constraint
    - Keep only 10 most recent predictions
    - Remove oldest when adding 11th
    - _Requirements: 6.2_

  - [x] 13.3 Create Recommendations component
    - Display recommendations in mystical guidance section
    - Show list of actionable suggestions
    - _Requirements: 4.6_

  - [ ] 13.4 Write property test for history size constraint
    - **Property 25: History Size Constraint**
    - **Validates: Requirements 6.2**

- [x] 14. Wire up App component with all child components
  - [x] 14.1 Integrate WebSocket hook in App
    - Use useWebSocket hook
    - Manage prediction state
    - Manage history state
    - _Requirements: 5.5, 6.1_

  - [x] 14.2 Connect all child components
    - Pass prediction to CrystalBall
    - Pass omens to OmensFeed
    - Pass recommendations to Recommendations
    - Pass history to History
    - _Requirements: 4.1, 4.4, 4.6, 6.3_

  - [x] 14.3 Create App.css with mystical theme
    - Dark purple/blue gradient background
    - Mystical glow effects
    - Responsive layout
    - _Requirements: 4.1_

- [x] 15. Checkpoint - Ensure frontend tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 16. End-to-end integration and testing
  - [x] 16.1 Test local backend startup
    - Start backend with uvicorn
    - Verify health endpoint responds
    - Check logs for proper initialization
    - _Requirements: 10.1, 10.5_

  - [-] 16.2 Test local frontend startup
    - Start frontend with npm run dev
    - Verify dashboard loads
    - Check WebSocket connection establishes
    - _Requirements: 10.2_

  - [ ] 16.3 Test WebSocket communication
    - Verify frontend connects to backend WebSocket
    - Test connection status display
    - Test reconnection on backend restart
    - _Requirements: 5.1, 5.4, 5.6_

  - [ ] 16.4 Set up ngrok tunnel for webhook testing
    - Start ngrok tunnel to backend
    - Configure GitHub webhook with ngrok URL
    - Test webhook signature validation
    - _Requirements: 10.3_

  - [ ] 16.5 Test end-to-end flow with real PR
    - Create test PR in GitHub repository
    - Verify webhook received and processed
    - Verify AI analysis completes
    - Verify prediction posted to PR as comment
    - Verify prediction appears on dashboard
    - _Requirements: 10.4_

- [ ] 17. Implement Configuration Service for production
  - [ ] 17.1 Create config.py with typed configuration
    - Define Config class with properties for all environment variables
    - Load DATABASE_URL, RATE_LIMIT_PER_MINUTE, and other new config
    - Implement validation method to check required config on startup
    - Provide default values for optional configuration
    - _Requirements: 12.1, 12.2, 13.1, 14.1_

  - [ ] 17.2 Update .env.example with new variables
    - Add DATABASE_URL with PostgreSQL connection string example
    - Add RATE_LIMIT_PER_MINUTE with default value
    - Add VITE_WS_URL for frontend WebSocket configuration
    - Document each variable with comments
    - _Requirements: 12.1, 13.1, 14.1_

- [ ] 18. Implement PostgreSQL database layer
  - [ ] 18.1 Create database schema and migrations
    - Create predictions table with all required fields
    - Create omens table with foreign key to predictions
    - Add indexes for timestamp, repo, and pr_number
    - Create migration script for initial schema
    - _Requirements: 13.1, 13.2_

  - [ ] 18.2 Create DatabaseService class
    - Initialize asyncpg connection pool
    - Implement connect method with retry logic and exponential backoff
    - Implement disconnect method for cleanup
    - Handle connection failures gracefully
    - _Requirements: 13.1, 13.5_

  - [ ] 18.3 Implement prediction storage methods
    - Implement save_prediction to insert prediction and omens
    - Implement get_predictions to retrieve recent predictions
    - Implement update_outcome to record actual deployment results
    - Ensure all fields are properly serialized/deserialized
    - _Requirements: 13.2, 13.3, 13.4_

  - [ ] 18.4 Implement accuracy metrics calculation
    - Implement get_accuracy_metrics to calculate from database
    - Query predictions with outcomes
    - Calculate accuracy rate as percentage
    - Return total predictions, predictions with outcomes, accurate count
    - _Requirements: 13.4_

  - [ ] 18.5 Implement health check for database
    - Implement health_check method to verify connectivity
    - Execute simple query to test connection
    - Return boolean status
    - _Requirements: 16.1_

  - [ ] 18.6 Write property test for database round-trip
    - **Property 45: Database Prediction Round-Trip**
    - **Validates: Requirements 13.2**

  - [ ] 18.7 Write property test for historical data ordering
    - **Property 46: Historical Data Ordering**
    - **Validates: Requirements 13.4**

- [ ] 19. Implement rate limiting
  - [ ] 19.1 Create RateLimiter class
    - Initialize with requests_per_minute threshold from config
    - Use in-memory dict to track requests per IP with timestamps
    - Implement sliding window algorithm
    - _Requirements: 14.1_

  - [ ] 19.2 Implement rate limit checking
    - Implement check_rate_limit method
    - Return tuple of (is_allowed, retry_after_seconds)
    - Calculate retry time based on oldest request in window
    - _Requirements: 14.2, 14.4_

  - [ ] 19.3 Implement request recording and cleanup
    - Implement record_request to add timestamp for IP
    - Implement cleanup_expired to remove old entries
    - Schedule periodic cleanup task
    - _Requirements: 14.1, 14.3_

  - [ ] 19.4 Add rate limiting middleware to webhook endpoint
    - Apply rate limiter to POST /webhook/github endpoint
    - Return 429 status when limit exceeded
    - Include Retry-After header in response
    - Log rate limit events with IP and timestamp
    - _Requirements: 14.2, 14.4, 14.5_

  - [ ] 19.5 Write property test for rate limiter tracking
    - **Property 47: Rate Limiter Request Tracking**
    - **Validates: Requirements 14.1**

  - [ ] 19.6 Write property test for rate limited response headers
    - **Property 48: Rate Limited Response Headers**
    - **Validates: Requirements 14.4**

  - [ ] 19.7 Write property test for rate limit logging
    - **Property 49: Rate Limit Logging**
    - **Validates: Requirements 14.5**

- [ ] 20. Improve diff parsing for renamed and binary files
  - [ ] 20.1 Enhance GitHubHandler diff parsing
    - Detect renamed files using "rename from/to" markers in diff
    - Detect binary files using "Binary files differ" marker
    - Update context to include files_renamed and binary_files counts
    - Exclude binary files from lines_added and lines_removed
    - _Requirements: 15.1, 15.2, 15.3_

  - [ ] 20.2 Handle edge cases in diff parsing
    - Handle files that are both renamed and modified
    - Handle empty diffs gracefully
    - Handle malformed diff content without crashing
    - Add comprehensive error handling
    - _Requirements: 15.4, 15.5_

  - [ ]* 20.3 Write property test for renamed file detection
    - **Property 50: Renamed File Detection**
    - **Validates: Requirements 15.1**

  - [ ]* 20.4 Write property test for binary file exclusion
    - **Property 51: Binary File Exclusion**
    - **Validates: Requirements 15.2**

  - [ ]* 20.5 Write property test for diff statistics accuracy
    - **Property 52: Diff Statistics Accuracy**
    - **Validates: Requirements 15.3**

- [ ] 21. Implement comprehensive health checks
  - [ ] 21.1 Enhance health endpoint with component checks
    - Check database connectivity using DatabaseService.health_check
    - Check WebSocket server status and active connection count
    - Check GitHub API accessibility with test request
    - Check LLM API accessibility with test request
    - _Requirements: 16.1, 16.2, 16.3, 16.4_

  - [ ] 21.2 Implement health check response logic
    - Return 503 status if any component is unhealthy
    - Return 200 status if all components are healthy
    - Include detailed status for each component in response
    - Include accuracy metrics and prediction count
    - _Requirements: 16.5, 16.6_

  - [ ]* 21.3 Write property test for health check database status
    - **Property 53: Health Check Database Status**
    - **Validates: Requirements 16.1**

  - [ ]* 21.4 Write property test for health check WebSocket status
    - **Property 54: Health Check WebSocket Status**
    - **Validates: Requirements 16.2**

  - [ ]* 21.5 Write property test for health check GitHub API status
    - **Property 55: Health Check GitHub API Status**
    - **Validates: Requirements 16.3**

  - [ ]* 21.6 Write property test for health check LLM API status
    - **Property 56: Health Check LLM API Status**
    - **Validates: Requirements 16.4**

  - [ ]* 21.7 Write property test for unhealthy component status code
    - **Property 57: Unhealthy Component Status Code**
    - **Validates: Requirements 16.5**

- [ ] 22. Configure frontend WebSocket URL from environment
  - [ ] 22.1 Update useWebSocket hook to read from environment
    - Read WebSocket URL from import.meta.env.VITE_WS_URL
    - Use default localhost URL if not set
    - Remove hardcoded IP addresses from source code
    - _Requirements: 12.1, 12.2, 12.3_

  - [ ] 22.2 Update vite.config.js for environment variables
    - Ensure VITE_WS_URL is properly loaded
    - Add development default in config
    - Document environment variable usage
    - _Requirements: 12.1, 12.4_

- [ ] 23. Update main application to wire new components
  - [ ] 23.1 Initialize DatabaseService in main.py
    - Create DatabaseService instance with connection string from config
    - Connect to database on startup
    - Disconnect on shutdown
    - Handle connection failures gracefully
    - _Requirements: 13.1, 13.5_

  - [ ] 23.2 Replace in-memory storage with database
    - Update PredictionEngine to use DatabaseService
    - Store predictions in database instead of memory
    - Load historical data from database on startup
    - Update accuracy calculation to use database
    - _Requirements: 13.2, 13.3, 13.4_

  - [ ] 23.3 Apply rate limiting to webhook endpoint
    - Initialize RateLimiter with config
    - Add rate limiting middleware to webhook endpoint
    - Handle rate limit responses properly
    - _Requirements: 14.1, 14.2, 14.4_

  - [ ] 23.4 Update health endpoint with comprehensive checks
    - Add database health check
    - Add WebSocket health check
    - Add GitHub API health check
    - Add LLM API health check
    - Return appropriate status codes
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5, 16.6_

- [ ] 24. Checkpoint - Ensure all production features work
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 25. Update documentation for production deployment
  - [ ] 25.1 Update README.md with production setup
    - Document PostgreSQL setup and configuration
    - Document rate limiting configuration
    - Document environment variables for production
    - Add deployment instructions
    - _Requirements: 13.1, 14.1_

  - [ ] 25.2 Create database migration guide
    - Document how to run initial schema migration
    - Document backup and restore procedures
    - Add troubleshooting for database issues
    - _Requirements: 13.1_

  - [ ] 25.3 Update .env.example with all production variables
    - Include DATABASE_URL example
    - Include RATE_LIMIT_PER_MINUTE
    - Include VITE_WS_URL for frontend
    - Add comments explaining each variable
    - _Requirements: 12.1, 13.1, 14.1_

