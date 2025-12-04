"""
Crystal Ball CI/CD - Main FastAPI Application

This is the main entry point for the Crystal Ball CI/CD backend server.
It orchestrates all components and provides HTTP and WebSocket endpoints.
"""

import os
import logging
import json
import re
from typing import Dict, Any
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import ValidationError

from github_handler import GitHubHandler
from ai_analyzer import AIAnalyzer
from prediction_engine import PredictionEngine
from websocket_manager import WebSocketManager


# Configure logging with sensitive data redaction
class SensitiveDataFilter(logging.Filter):
    """
    Filter to redact sensitive data from log messages.
    
    Redacts:
    - API keys (patterns like sk-*, ghp_*, etc.)
    - Tokens
    - Authorization headers
    
    Validates: Requirements 8.6, 9.5
    """
    
    SENSITIVE_PATTERNS = [
        (r'sk-[a-zA-Z0-9-_]+', '[REDACTED_API_KEY]'),
        (r'ghp_[a-zA-Z0-9]+', '[REDACTED_GITHUB_TOKEN]'),
        (r'github_pat_[a-zA-Z0-9_]+', '[REDACTED_GITHUB_TOKEN]'),
        (r'Bearer [a-zA-Z0-9\-._~+/]+=*', 'Bearer [REDACTED_TOKEN]'),
        (r'"token":\s*"[^"]+"', '"token": "[REDACTED]"'),
        (r'"api_key":\s*"[^"]+"', '"api_key": "[REDACTED]"'),
        (r'"secret":\s*"[^"]+"', '"secret": "[REDACTED]"'),
    ]
    
    def filter(self, record: logging.LogRecord) -> bool:
        """Redact sensitive data from log message."""
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            message = record.msg
            for pattern, replacement in self.SENSITIVE_PATTERNS:
                message = re.sub(pattern, replacement, message)
            record.msg = message
        return True


# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Add sensitive data filter to all loggers
for handler in logging.root.handlers:
    handler.addFilter(SensitiveDataFilter())

logger = logging.getLogger(__name__)


# Load environment variables
load_dotenv()

# Validate required environment variables
REQUIRED_ENV_VARS = {
    'GITHUB_TOKEN': 'GitHub personal access token',
    'ANTHROPIC_API_KEY': 'Anthropic API key for Claude',
    'GITHUB_WEBHOOK_SECRET': 'GitHub webhook secret for signature validation'
}

missing_vars = []
for var, description in REQUIRED_ENV_VARS.items():
    if not os.getenv(var):
        missing_vars.append(f"{var} ({description})")

if missing_vars:
    error_msg = "Missing required environment variables:\n" + "\n".join(f"  - {var}" for var in missing_vars)
    logger.error(error_msg)
    raise RuntimeError(error_msg)

logger.info("All required environment variables loaded successfully")

# Initialize FastAPI app
app = FastAPI(
    title="Crystal Ball CI/CD",
    description="AI-powered CI/CD monitoring with mystical predictions",
    version="1.0.0"
)

# Configure CORS for frontend
frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:5173')
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:5173", "http://localhost:5174", "http://localhost:5175"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS configured for frontend: {frontend_url}")

# Initialize all components
github_handler = GitHubHandler(
    github_token=os.getenv('GITHUB_TOKEN'),
    webhook_secret=os.getenv('GITHUB_WEBHOOK_SECRET')
)

ai_analyzer = AIAnalyzer(
    api_key=os.getenv('ANTHROPIC_API_KEY')
)

prediction_engine = PredictionEngine()

websocket_manager = WebSocketManager()

logger.info("All components initialized successfully")


# ============================================================================
# HTTP Endpoints
# ============================================================================

@app.post("/webhook/github")
async def github_webhook(request: Request):
    """
    GitHub webhook endpoint for receiving PR events.
    
    This endpoint:
    1. Validates the webhook signature
    2. Processes PR events (opened, synchronize)
    3. Fetches the PR diff
    4. Triggers AI analysis
    5. Enhances prediction with historical data
    6. Posts comment to PR
    7. Broadcasts to WebSocket clients
    
    Validates: Requirements 1.1, 1.2, 1.4, 1.5
    """
    try:
        # Get raw body for signature validation
        body = await request.body()
        signature = request.headers.get('X-Hub-Signature-256', '')
        
        # Validate webhook signature
        if not await github_handler.validate_signature(body, signature):
            logger.warning("Webhook signature validation failed")
            raise HTTPException(status_code=401, detail="Invalid signature")
        
        # Parse JSON payload
        try:
            payload = json.loads(body)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse webhook payload: {e}")
            raise HTTPException(status_code=400, detail="Invalid JSON payload")
        
        # Handle PR event
        try:
            pr_data = await github_handler.handle_pr_event(payload)
        except ValidationError as e:
            logger.error(f"Webhook payload validation failed: {e}")
            raise HTTPException(status_code=400, detail=f"Malformed payload: {str(e)}")
        
        # If event should be ignored, return success
        if pr_data is None:
            return {"status": "ignored", "message": "Event type not processed"}
        
        logger.info(f"Processing PR #{pr_data['pr_number']} from {pr_data['repo']}")
        
        # Fetch PR diff
        try:
            diff_data = await github_handler.fetch_pr_diff(pr_data['diff_url'])
        except Exception as e:
            logger.error(f"Failed to fetch PR diff: {e}")
            raise HTTPException(status_code=502, detail="Failed to fetch PR diff from GitHub")
        
        # Prepare context for AI analysis
        context = {
            'files_changed': diff_data['files_changed'],
            'lines_added': diff_data['lines_added'],
            'lines_removed': diff_data['lines_removed'],
            'repo': pr_data['repo'],
            'pr_number': pr_data['pr_number']
        }
        
        # Trigger AI analysis
        logger.info("Starting AI analysis of code diff")
        ai_prediction = await ai_analyzer.analyze_code_diff(diff_data['diff'], context)
        
        # Enhance prediction with historical data
        enhanced_prediction = prediction_engine.enhance_prediction(ai_prediction)
        
        # Add PR metadata to prediction
        enhanced_prediction['pr_url'] = pr_data['pr_url']
        enhanced_prediction['pr_number'] = pr_data['pr_number']
        enhanced_prediction['repo'] = pr_data['repo']
        enhanced_prediction['context'] = context
        
        # Store prediction in history
        prediction_engine.store_prediction(enhanced_prediction)
        
        # Post comment to PR
        comment_posted = await github_handler.post_comment(
            pr_data['comments_url'],
            enhanced_prediction
        )
        
        if not comment_posted:
            logger.warning("Failed to post comment to PR, but continuing")
        
        # Broadcast to WebSocket clients
        # Prepare message for frontend (exclude some backend-only fields)
        websocket_message = {
            'prediction_score': enhanced_prediction['prediction_score'],
            'omens': enhanced_prediction['omens'],
            'mystical_message': enhanced_prediction['mystical_message'],
            'recommendations': enhanced_prediction.get('recommendations', []),
            'timestamp': enhanced_prediction.get('timestamp', ''),
            'pr_number': enhanced_prediction['pr_number'],
            'repo': enhanced_prediction['repo']
        }
        
        await websocket_manager.broadcast(websocket_message)
        
        logger.info(
            f"Successfully processed PR #{pr_data['pr_number']}: "
            f"score={enhanced_prediction['prediction_score']}, "
            f"omens={len(enhanced_prediction['omens'])}"
        )
        
        return {
            "status": "success",
            "prediction_id": enhanced_prediction.get('id'),
            "prediction_score": enhanced_prediction['prediction_score'],
            "omens_count": len(enhanced_prediction['omens'])
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log unexpected errors with full context
        logger.error(
            f"Unexpected error processing webhook: {e}",
            exc_info=True,
            extra={
                'component': 'webhook_endpoint',
                'operation': 'process_webhook'
            }
        )
        raise HTTPException(status_code=500, detail="Internal server error")



# ============================================================================
# WebSocket Endpoints
# ============================================================================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time prediction updates.
    
    Accepts connections from frontend clients and maintains them
    for broadcasting predictions.
    
    Validates: Requirements 5.1, 5.3
    """
    await websocket_manager.connect(websocket)
    
    try:
        # Keep connection alive and handle incoming messages
        while True:
            # Wait for messages from client (mostly just to detect disconnection)
            data = await websocket.receive_text()
            
            # Echo back a simple acknowledgment if client sends anything
            if data:
                await websocket.send_json({
                    "type": "ack",
                    "message": "Connection active"
                })
                
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected normally")
        await websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        await websocket_manager.disconnect(websocket)



@app.get("/health")
async def health_check():
    """
    Health check endpoint with system metrics.
    
    Returns:
        - status: "alive"
        - accuracy_rate: Overall prediction accuracy percentage
        - predictions_made: Total number of predictions
        - active_connections: Number of active WebSocket connections
    
    Validates: Requirements 8.7, 10.5
    """
    accuracy_rate = prediction_engine.get_accuracy_rate()
    predictions_made = len(prediction_engine.history)
    active_connections = websocket_manager.get_connection_count()
    
    return {
        "status": "alive",
        "accuracy_rate": round(accuracy_rate, 2),
        "predictions_made": predictions_made,
        "active_connections": active_connections
    }


# ============================================================================
# Application Startup
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Log application startup."""
    logger.info("=" * 60)
    logger.info("Crystal Ball CI/CD Backend Starting")
    logger.info("=" * 60)
    logger.info(f"Frontend URL: {frontend_url}")
    logger.info(f"WebSocket endpoint: ws://localhost:{os.getenv('BACKEND_PORT', '8000')}/ws")
    logger.info(f"Webhook endpoint: http://localhost:{os.getenv('BACKEND_PORT', '8000')}/webhook/github")
    logger.info(f"Health endpoint: http://localhost:{os.getenv('BACKEND_PORT', '8000')}/health")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Log application shutdown."""
    logger.info("Crystal Ball CI/CD Backend Shutting Down")


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('BACKEND_PORT', '8000'))
    uvicorn.run(app, host="0.0.0.0", port=port)
