#!/usr/bin/env python3
"""Send test webhook to local server"""
import requests
import json
import hmac
import hashlib

# Configuration
WEBHOOK_URL = "http://localhost:8023/webhook/github"
SECRET = "3699277dc5e28d6c2dddd0eb70ad9c8607ad97fef6ebe1ed2a3d8ec4639fc16d"

# Test payload - complete with all required fields
payload = {
    "action": "opened",
    "pull_request": {
        "number": 123,
        "url": "https://api.github.com/repos/test/repo/pulls/123",
        "title": "Test PR for Crystal Ball",
        "user": {"login": "testuser"},
        "diff_url": "https://github.com/test/repo/pull/123.diff",
        "comments_url": "https://api.github.com/repos/test/repo/issues/123/comments"
    },
    "repository": {
        "full_name": "test/repo"
    }
}

# Convert to JSON string
payload_str = json.dumps(payload, separators=(',', ':'))
payload_bytes = payload_str.encode('utf-8')

# Calculate signature
signature = 'sha256=' + hmac.new(
    SECRET.encode('utf-8'),
    payload_bytes,
    hashlib.sha256
).hexdigest()

print(f"🔮 Sending test webhook to Crystal Ball backend...")
print(f"URL: {WEBHOOK_URL}")
print(f"Signature: {signature[:30]}...")
print()

# Send request
headers = {
    'Content-Type': 'application/json',
    'X-GitHub-Event': 'pull_request',
    'X-Hub-Signature-256': signature
}

try:
    response = requests.post(WEBHOOK_URL, data=payload_bytes, headers=headers, timeout=30)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("\n✅ Webhook sent successfully!")
        print("🔮 The Crystal Ball is analyzing the PR...")
        print("👁️  Check your frontend at http://localhost:5175/ to see the prediction!")
    else:
        print(f"\n❌ Webhook failed: {response.status_code}")
        
except Exception as e:
    print(f"❌ Error sending webhook: {e}")
