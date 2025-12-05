#!/usr/bin/env python3
"""Send test prediction directly via WebSocket manager"""
import asyncio
import json
from datetime import datetime
from websocket_manager import WebSocketManager
from models import Prediction, Omen, PredictionContext

async def send_test_prediction():
    # Create WebSocket manager
    ws_manager = WebSocketManager()
    
    # Create test prediction
    prediction = Prediction(
        pr_url="https://github.com/test/repo/pull/123",
        pr_number=123,
        repo="test/repo",
        prediction_score=75,
        mystical_message="🔮 The Crystal Ball sees potential in your code, but beware of dark omens lurking in the shadows...",
        omens=[
            Omen(
                type="minor",
                title="Missing Error Handling",
                description="The spirits detect unhandled exceptions in authentication.py",
                file="src/authentication.py",
                severity=4
            ),
            Omen(
                type="major",
                title="Performance Concern",
                description="Inefficient database queries detected. The ancient ones warn of slow response times.",
                file="api/database.py",
                severity=7
            ),
            Omen(
                type="dark",
                title="Security Vulnerability",
                description="⚠️ SQL injection vulnerability detected! This path leads to darkness.",
                file="api/users.py",
                severity=9
            )
        ],
        recommendations=[
            "Add try-catch blocks around authentication logic",
            "Implement database query caching",
            "Use parameterized queries to prevent SQL injection",
            "Add input validation for user-supplied data"
        ],
        context=PredictionContext(
            files_changed=5,
            lines_added=250,
            lines_removed=80
        )
    )
    
    # Convert to dict
    prediction_dict = json.loads(prediction.model_dump_json())
    
    print("🔮 Sending test prediction to all WebSocket clients...")
    print(f"Score: {prediction.prediction_score}/100")
    print(f"Omens: {len(prediction.omens)}")
    print(f"Recommendations: {len(prediction.recommendations)}")
    print()
    
    # Broadcast to all connected clients
    await ws_manager.broadcast(prediction_dict)
    
    print("✅ Prediction sent!")
    print("👁️  Check your frontend at http://localhost:5175/")

if __name__ == "__main__":
    asyncio.run(send_test_prediction())
