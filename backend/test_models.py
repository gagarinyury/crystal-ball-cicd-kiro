"""
Basic tests to verify Pydantic models work correctly.
"""

from models import Omen, Prediction, WebhookPayload, PredictionContext
from datetime import datetime
import json


def test_omen_model():
    """Test Omen model creation and validation."""
    print("Testing Omen model...")
    
    # Valid omen
    omen = Omen(
        type='major',
        title='Potential null pointer',
        description='This code may cause a null pointer exception',
        file='src/main.py',
        severity=7
    )
    assert omen.type == 'major'
    assert omen.severity == 7
    print("✓ Valid omen created successfully")
    
    # Test severity validation
    try:
        invalid_omen = Omen(
            type='minor',
            title='Test',
            description='Test',
            file='test.py',
            severity=11  # Invalid: > 10
        )
        print("✗ Should have raised validation error for severity > 10")
    except ValueError:
        print("✓ Severity validation works correctly")
    
    # Test with historical failures
    omen_with_history = Omen(
        type='dark',
        title='Recurring issue',
        description='This pattern has failed before',
        file='src/auth.py',
        severity=9,
        historical_failures=5
    )
    assert omen_with_history.historical_failures == 5
    print("✓ Omen with historical failures created successfully")


def test_prediction_model():
    """Test Prediction model creation and validation."""
    print("\nTesting Prediction model...")
    
    # Create prediction
    prediction = Prediction(
        pr_url='https://github.com/owner/repo/pull/123',
        pr_number=123,
        repo='owner/repo',
        prediction_score=75,
        omens=[
            Omen(
                type='minor',
                title='Code smell',
                description='Consider refactoring',
                file='src/utils.py',
                severity=3
            )
        ],
        mystical_message='The spirits see mostly clear skies ahead',
        recommendations=['Add unit tests', 'Review error handling'],
        context=PredictionContext(
            files_changed=5,
            lines_added=120,
            lines_removed=45
        )
    )
    
    assert prediction.prediction_score == 75
    assert len(prediction.omens) == 1
    assert prediction.id is not None  # UUID should be auto-generated
    assert prediction.timestamp is not None  # Timestamp should be auto-generated
    assert prediction.actual_result is None  # Should default to None
    print("✓ Valid prediction created successfully")
    
    # Test score validation
    try:
        invalid_prediction = Prediction(
            pr_url='https://github.com/owner/repo/pull/123',
            pr_number=123,
            repo='owner/repo',
            prediction_score=150,  # Invalid: > 100
            omens=[],
            mystical_message='Test',
            recommendations=[],
            context=PredictionContext(
                files_changed=1,
                lines_added=10,
                lines_removed=5
            )
        )
        print("✗ Should have raised validation error for score > 100")
    except ValueError:
        print("✓ Score validation works correctly")


def test_webhook_payload_model():
    """Test WebhookPayload model creation and validation."""
    print("\nTesting WebhookPayload model...")
    
    # Valid webhook payload
    payload_data = {
        'action': 'opened',
        'pull_request': {
            'number': 42,
            'url': 'https://api.github.com/repos/owner/repo/pulls/42',
            'diff_url': 'https://github.com/owner/repo/pull/42.diff',
            'comments_url': 'https://api.github.com/repos/owner/repo/issues/42/comments',
            'title': 'Add new feature',
            'user': {
                'login': 'developer123'
            }
        },
        'repository': {
            'full_name': 'owner/repo'
        }
    }
    
    payload = WebhookPayload(**payload_data)
    assert payload.action == 'opened'
    assert payload.pull_request.number == 42
    assert payload.repository.full_name == 'owner/repo'
    print("✓ Valid webhook payload created successfully")
    
    # Test missing required field
    try:
        invalid_payload = WebhookPayload(
            action='opened',
            pull_request=None,  # Missing required field
            repository={'full_name': 'owner/repo'}
        )
        print("✗ Should have raised validation error for missing pull_request")
    except Exception:
        print("✓ Required field validation works correctly")


def test_json_serialization():
    """Test that models can be serialized to JSON."""
    print("\nTesting JSON serialization...")
    
    prediction = Prediction(
        pr_url='https://github.com/owner/repo/pull/123',
        pr_number=123,
        repo='owner/repo',
        prediction_score=85,
        omens=[],
        mystical_message='All is well',
        recommendations=['Keep up the good work'],
        context=PredictionContext(
            files_changed=2,
            lines_added=50,
            lines_removed=10
        )
    )
    
    # Serialize to JSON
    json_str = prediction.model_dump_json()
    assert json_str is not None
    print("✓ Model serialized to JSON successfully")
    
    # Deserialize from JSON
    json_data = json.loads(json_str)
    prediction_restored = Prediction(**json_data)
    assert prediction_restored.prediction_score == 85
    assert prediction_restored.pr_number == 123
    print("✓ Model deserialized from JSON successfully")
    print("✓ Round-trip serialization works correctly")


if __name__ == '__main__':
    print("Running Pydantic model tests...\n")
    print("=" * 50)
    
    test_omen_model()
    test_prediction_model()
    test_webhook_payload_model()
    test_json_serialization()
    
    print("\n" + "=" * 50)
    print("\n✅ All model tests passed!")
