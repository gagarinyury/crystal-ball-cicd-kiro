"""
Tests to verify Requirements 11.1 and 11.5 are satisfied by the Pydantic models.

Requirement 11.1: WHEN the GitHub Webhook Handler receives a webhook payload 
                  THEN the GitHub Webhook Handler SHALL parse the JSON and 
                  validate required fields exist

Requirement 11.5: WHEN serializing prediction data for WebSocket THEN the 
                  Crystal Ball System SHALL ensure the data is valid JSON 
                  before sending
"""

from models import WebhookPayload, Prediction, Omen, PredictionContext
import json
from pydantic import ValidationError


def test_requirement_11_1_valid_webhook_payload():
    """
    Test Requirement 11.1: Valid webhook payload with all required fields.
    """
    print("Testing Requirement 11.1 - Valid webhook payload...")
    
    payload_json = """
    {
        "action": "opened",
        "pull_request": {
            "number": 42,
            "url": "https://api.github.com/repos/owner/repo/pulls/42",
            "diff_url": "https://github.com/owner/repo/pull/42.diff",
            "comments_url": "https://api.github.com/repos/owner/repo/issues/42/comments",
            "title": "Add new feature",
            "user": {
                "login": "developer123"
            }
        },
        "repository": {
            "full_name": "owner/repo"
        }
    }
    """
    
    # Parse JSON
    payload_data = json.loads(payload_json)
    
    # Validate with Pydantic model
    try:
        webhook = WebhookPayload(**payload_data)
        print(f"✓ Valid payload parsed successfully")
        print(f"  - Action: {webhook.action}")
        print(f"  - PR Number: {webhook.pull_request.number}")
        print(f"  - Repository: {webhook.repository.full_name}")
        return True
    except ValidationError as e:
        print(f"✗ Validation failed: {e}")
        return False


def test_requirement_11_1_missing_action():
    """
    Test Requirement 11.1: Webhook payload missing 'action' field should fail.
    """
    print("\nTesting Requirement 11.1 - Missing 'action' field...")
    
    payload_json = """
    {
        "pull_request": {
            "number": 42,
            "url": "https://api.github.com/repos/owner/repo/pulls/42",
            "diff_url": "https://github.com/owner/repo/pull/42.diff",
            "comments_url": "https://api.github.com/repos/owner/repo/issues/42/comments",
            "title": "Add new feature",
            "user": {
                "login": "developer123"
            }
        },
        "repository": {
            "full_name": "owner/repo"
        }
    }
    """
    
    payload_data = json.loads(payload_json)
    
    try:
        webhook = WebhookPayload(**payload_data)
        print(f"✗ Should have failed validation for missing 'action'")
        return False
    except ValidationError as e:
        print(f"✓ Correctly rejected payload with missing 'action' field")
        return True


def test_requirement_11_1_missing_pull_request():
    """
    Test Requirement 11.1: Webhook payload missing 'pull_request' field should fail.
    """
    print("\nTesting Requirement 11.1 - Missing 'pull_request' field...")
    
    payload_json = """
    {
        "action": "opened",
        "repository": {
            "full_name": "owner/repo"
        }
    }
    """
    
    payload_data = json.loads(payload_json)
    
    try:
        webhook = WebhookPayload(**payload_data)
        print(f"✗ Should have failed validation for missing 'pull_request'")
        return False
    except ValidationError as e:
        print(f"✓ Correctly rejected payload with missing 'pull_request' field")
        return True


def test_requirement_11_1_missing_repository():
    """
    Test Requirement 11.1: Webhook payload missing 'repository' field should fail.
    """
    print("\nTesting Requirement 11.1 - Missing 'repository' field...")
    
    payload_json = """
    {
        "action": "opened",
        "pull_request": {
            "number": 42,
            "url": "https://api.github.com/repos/owner/repo/pulls/42",
            "diff_url": "https://github.com/owner/repo/pull/42.diff",
            "comments_url": "https://api.github.com/repos/owner/repo/issues/42/comments",
            "title": "Add new feature",
            "user": {
                "login": "developer123"
            }
        }
    }
    """
    
    payload_data = json.loads(payload_json)
    
    try:
        webhook = WebhookPayload(**payload_data)
        print(f"✗ Should have failed validation for missing 'repository'")
        return False
    except ValidationError as e:
        print(f"✓ Correctly rejected payload with missing 'repository' field")
        return True


def test_requirement_11_5_prediction_serialization():
    """
    Test Requirement 11.5: Prediction can be serialized to valid JSON.
    """
    print("\nTesting Requirement 11.5 - Prediction serialization to JSON...")
    
    # Create a prediction
    prediction = Prediction(
        pr_url='https://github.com/owner/repo/pull/123',
        pr_number=123,
        repo='owner/repo',
        prediction_score=75,
        omens=[
            Omen(
                type='minor',
                title='Code smell detected',
                description='Consider refactoring this method',
                file='src/utils.py',
                severity=3
            ),
            Omen(
                type='major',
                title='Potential bug',
                description='Null pointer exception possible',
                file='src/main.py',
                severity=7
            )
        ],
        mystical_message='The spirits see mostly clear skies ahead, but beware of shadows',
        recommendations=['Add unit tests', 'Review error handling'],
        context=PredictionContext(
            files_changed=5,
            lines_added=120,
            lines_removed=45
        )
    )
    
    # Serialize to JSON
    try:
        json_str = prediction.model_dump_json()
        print(f"✓ Prediction serialized to JSON successfully")
        
        # Verify it's valid JSON by parsing it
        parsed = json.loads(json_str)
        print(f"✓ Serialized JSON is valid and parseable")
        
        # Verify key fields are present
        assert 'id' in parsed
        assert 'timestamp' in parsed
        assert 'prediction_score' in parsed
        assert 'omens' in parsed
        assert 'mystical_message' in parsed
        print(f"✓ All required fields present in serialized JSON")
        
        return True
    except Exception as e:
        print(f"✗ Serialization failed: {e}")
        return False


def test_requirement_11_5_round_trip():
    """
    Test Requirement 11.5: Prediction can be serialized and deserialized (round-trip).
    """
    print("\nTesting Requirement 11.5 - Round-trip serialization...")
    
    # Create a prediction
    original = Prediction(
        pr_url='https://github.com/owner/repo/pull/456',
        pr_number=456,
        repo='owner/repo',
        prediction_score=92,
        omens=[],
        mystical_message='The path ahead is clear and bright',
        recommendations=['Keep up the good work'],
        context=PredictionContext(
            files_changed=2,
            lines_added=50,
            lines_removed=10
        )
    )
    
    try:
        # Serialize to JSON
        json_str = original.model_dump_json()
        
        # Deserialize back to object
        json_data = json.loads(json_str)
        restored = Prediction(**json_data)
        
        # Verify key fields match
        assert restored.pr_number == original.pr_number
        assert restored.prediction_score == original.prediction_score
        assert restored.mystical_message == original.mystical_message
        assert len(restored.omens) == len(original.omens)
        
        print(f"✓ Round-trip serialization successful")
        print(f"  - Original score: {original.prediction_score}")
        print(f"  - Restored score: {restored.prediction_score}")
        print(f"  - Match: {original.prediction_score == restored.prediction_score}")
        
        return True
    except Exception as e:
        print(f"✗ Round-trip failed: {e}")
        return False


if __name__ == '__main__':
    print("=" * 70)
    print("Testing Requirements 11.1 and 11.5")
    print("=" * 70)
    
    results = []
    
    # Test Requirement 11.1
    print("\n--- REQUIREMENT 11.1: Webhook Payload Validation ---")
    results.append(test_requirement_11_1_valid_webhook_payload())
    results.append(test_requirement_11_1_missing_action())
    results.append(test_requirement_11_1_missing_pull_request())
    results.append(test_requirement_11_1_missing_repository())
    
    # Test Requirement 11.5
    print("\n--- REQUIREMENT 11.5: Prediction JSON Serialization ---")
    results.append(test_requirement_11_5_prediction_serialization())
    results.append(test_requirement_11_5_round_trip())
    
    print("\n" + "=" * 70)
    if all(results):
        print("✅ All tests passed! Requirements 11.1 and 11.5 are satisfied.")
    else:
        print("❌ Some tests failed!")
    print("=" * 70)
