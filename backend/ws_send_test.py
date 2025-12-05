#!/usr/bin/env python3
"""WebSocket client to send test prediction"""
import asyncio
import json
import websockets
from datetime import datetime

async def send_test():
    uri = "ws://localhost:8023/ws"
    
    prediction = {
        "id": "test-123",
        "timestamp": datetime.now().isoformat(),
        "pr_url": "https://github.com/test/repo/pull/123",
        "pr_number": 123,
        "repo": "test/repo",
        "prediction_score": 75,
        "mystical_message": "🔮 The Crystal Ball sees great potential in your code, young developer! However, three omens cloud the future...",
        "omens": [
            {
                "type": "minor",
                "title": "Missing Error Handling",
                "description": "The spirits detect unhandled exceptions in the authentication flow",
                "file": "src/auth.py",
                "severity": 4
            },
            {
                "type": "major",
                "title": "Performance Warning",
                "description": "Database queries may summon the demons of slowness",
                "file": "api/database.py",
                "severity": 7
            },
            {
                "type": "dark",
                "title": "Security Vulnerability",
                "description": "⚠️ SQL injection risk detected! The dark forces threaten your data!",
                "file": "api/users.py",
                "severity": 9
            }
        ],
        "recommendations": [
            "Wrap authentication calls in try-catch blocks",
            "Add database query caching layer",
            "Use parameterized queries immediately",
            "Implement input sanitization"
        ],
        "context": {
            "files_changed": 5,
            "lines_added": 250,
            "lines_removed": 80
        },
        "actual_result": None,
        "accurate": None
    }
    
    print("🔮 Connecting to WebSocket server...")
    try:
        async with websockets.connect(uri) as websocket:
            print("✅ Connected!")
            print(f"📤 Sending test prediction (Score: {prediction['prediction_score']}/100)")
            
            await websocket.send(json.dumps(prediction))
            
            print("✅ Prediction sent!")
            print("\n👁️  Check your browser at http://localhost:5175/")
            print("You should see:")
            print("  - Crystal Ball with score 75/100")
            print("  - 3 omens (1 dark, 1 major, 1 minor)")
            print("  - 4 recommendations")
            
            await asyncio.sleep(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(send_test())
