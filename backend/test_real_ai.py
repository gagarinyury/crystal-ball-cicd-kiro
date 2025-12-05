#!/usr/bin/env python3
"""Test real AI analysis with Claude API"""
import asyncio
import os
from dotenv import load_dotenv
from ai_analyzer import AIAnalyzer

async def test_real_analysis():
    # Load .env file (override system env vars)
    load_dotenv('../.env', override=True)

    # Get API key from environment
    api_key = os.getenv('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in environment")
        return

    print(f"🔑 Using API key: {api_key[:25]}...")

    # Create analyzer
    analyzer = AIAnalyzer(api_key)
    print(f"✅ Using model: {analyzer.model}")
    print()

    # Test diff - adding a simple function without error handling
    test_diff = """diff --git a/api/users.py b/api/users.py
index 1234567..abcdefg 100644
--- a/api/users.py
+++ b/api/users.py
@@ -10,6 +10,15 @@ from database import db

 app = Flask(__name__)

+def get_user_by_id(user_id):
+    \"\"\"Get user from database by ID\"\"\"
+    query = f"SELECT * FROM users WHERE id = {user_id}"
+    result = db.execute(query)
+    return result.fetchone()
+
+@app.route('/user/<user_id>')
+def user_profile(user_id):
+    user = get_user_by_id(user_id)
+    return jsonify(user)
+
 @app.route('/health')
 def health():
     return {'status': 'ok'}
"""

    # Context
    context = {
        'repo': 'test/demo-app',
        'files_changed': 1,
        'lines_added': 12,
        'lines_removed': 0
    }

    print("🔮 Analyzing code diff with Claude AI...")
    print(f"📝 Files changed: {context['files_changed']}")
    print(f"➕ Lines added: {context['lines_added']}")
    print()

    # Analyze
    result = await analyzer.analyze_code_diff(test_diff, context)

    print("=" * 60)
    print("🎯 ANALYSIS RESULTS")
    print("=" * 60)
    print()
    print(f"📊 Prediction Score: {result['prediction_score']}/100")
    print()
    print(f"🔮 Mystical Message:")
    print(f"   {result['mystical_message']}")
    print()

    if result['omens']:
        print(f"⚠️  Omens Found: {len(result['omens'])}")
        print()
        for i, omen in enumerate(result['omens'], 1):
            severity_emoji = "🟡" if omen['severity'] <= 3 else "🟠" if omen['severity'] <= 7 else "🔴"
            print(f"{i}. {severity_emoji} [{omen['type'].upper()}] {omen['title']}")
            print(f"   File: {omen['file']}")
            print(f"   Severity: {omen['severity']}/10")
            print(f"   {omen['description']}")
            print()
    else:
        print("✅ No omens detected!")
        print()

    if result.get('recommendations'):
        print(f"💡 Recommendations: {len(result['recommendations'])}")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"   {i}. {rec}")
        print()

    print("=" * 60)
    print("✅ Analysis complete!")

if __name__ == "__main__":
    asyncio.run(test_real_analysis())
