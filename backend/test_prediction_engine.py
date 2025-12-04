"""
Tests for PredictionEngine class.

Tests cover:
- Prediction storage with UUID and timestamp generation
- Outcome recording and accuracy calculation
- Pattern failure tracking
- Prediction enhancement with historical data
"""

from prediction_engine import PredictionEngine
from datetime import datetime
import time


def test_store_prediction():
    """Test storing predictions with auto-generated UUID and timestamp."""
    print("Testing prediction storage...")
    
    engine = PredictionEngine()
    
    # Create a prediction without ID or timestamp
    prediction = {
        'pr_url': 'https://github.com/owner/repo/pull/1',
        'pr_number': 1,
        'repo': 'owner/repo',
        'prediction_score': 85,
        'omens': [],
        'mystical_message': 'The stars align!',
        'recommendations': []
    }
    
    # Store prediction
    engine.store_prediction(prediction)
    
    # Verify it was stored
    assert len(engine.history) == 1
    stored = engine.history[0]
    
    # Verify UUID was added
    assert 'id' in stored
    assert stored['id'] is not None
    assert len(stored['id']) > 0
    print(f"✓ UUID generated: {stored['id']}")
    
    # Verify timestamp was added
    assert 'timestamp' in stored
    assert stored['timestamp'] is not None
    print(f"✓ Timestamp generated: {stored['timestamp']}")
    
    # Verify original data preserved
    assert stored['prediction_score'] == 85
    assert stored['pr_number'] == 1
    print("✓ Prediction stored successfully with auto-generated fields")


def test_store_multiple_predictions():
    """Test storing multiple predictions."""
    print("\nTesting multiple prediction storage...")
    
    engine = PredictionEngine()
    
    # Store 3 predictions
    for i in range(3):
        prediction = {
            'pr_url': f'https://github.com/owner/repo/pull/{i+1}',
            'pr_number': i + 1,
            'repo': 'owner/repo',
            'prediction_score': 70 + i * 10,
            'omens': [],
            'mystical_message': f'Prediction {i+1}',
            'recommendations': []
        }
        engine.store_prediction(prediction)
    
    assert len(engine.history) == 3
    
    # Verify all have unique IDs
    ids = [pred['id'] for pred in engine.history]
    assert len(ids) == len(set(ids))  # All unique
    print("✓ Multiple predictions stored with unique IDs")


def test_learn_from_outcome_success():
    """Test recording successful deployment outcome."""
    print("\nTesting outcome recording (success)...")
    
    engine = PredictionEngine()
    
    # Store a prediction with high score
    prediction = {
        'pr_url': 'https://github.com/owner/repo/pull/1',
        'pr_number': 1,
        'repo': 'owner/repo',
        'prediction_score': 85,
        'omens': [],
        'mystical_message': 'Success predicted',
        'recommendations': []
    }
    engine.store_prediction(prediction)
    pred_id = engine.history[0]['id']
    
    # Record successful outcome
    engine.learn_from_outcome(pred_id, actual_result=True)
    
    # Verify outcome recorded
    stored = engine.history[0]
    assert stored['actual_result'] is True
    assert stored['accurate'] is True  # High score + success = accurate
    print("✓ Successful outcome recorded correctly")
    print(f"  Score: {stored['prediction_score']}, Result: Success, Accurate: True")


def test_learn_from_outcome_failure():
    """Test recording failed deployment outcome."""
    print("\nTesting outcome recording (failure)...")
    
    engine = PredictionEngine()
    
    # Store a prediction with low score
    prediction = {
        'pr_url': 'https://github.com/owner/repo/pull/2',
        'pr_number': 2,
        'repo': 'owner/repo',
        'prediction_score': 45,
        'omens': [
            {
                'type': 'major',
                'title': 'Potential bug',
                'description': 'This looks risky',
                'file': 'src/main.py',
                'severity': 7
            }
        ],
        'mystical_message': 'Danger ahead',
        'recommendations': []
    }
    engine.store_prediction(prediction)
    pred_id = engine.history[0]['id']
    
    # Record failed outcome
    engine.learn_from_outcome(pred_id, actual_result=False)
    
    # Verify outcome recorded
    stored = engine.history[0]
    assert stored['actual_result'] is False
    assert stored['accurate'] is True  # Low score + failure = accurate
    print("✓ Failed outcome recorded correctly")
    print(f"  Score: {stored['prediction_score']}, Result: Failure, Accurate: True")
    
    # Verify pattern failure tracked
    assert 'major:src/main.py' in engine.pattern_failures
    assert engine.pattern_failures['major:src/main.py'] == 1
    print("✓ Pattern failure tracked: major:src/main.py = 1")


def test_accuracy_calculation():
    """Test accuracy rate calculation."""
    print("\nTesting accuracy calculation...")
    
    engine = PredictionEngine()
    
    # No outcomes yet
    assert engine.get_accuracy_rate() == 0.0
    print("✓ Accuracy is 0% with no outcomes")
    
    # Add predictions with outcomes
    # Prediction 1: High score, success -> accurate
    pred1 = {
        'pr_number': 1, 'repo': 'test/repo', 'pr_url': 'url1',
        'prediction_score': 85, 'omens': [],
        'mystical_message': 'msg', 'recommendations': []
    }
    engine.store_prediction(pred1)
    engine.learn_from_outcome(engine.history[0]['id'], True)
    
    # Prediction 2: Low score, failure -> accurate
    pred2 = {
        'pr_number': 2, 'repo': 'test/repo', 'pr_url': 'url2',
        'prediction_score': 40, 'omens': [],
        'mystical_message': 'msg', 'recommendations': []
    }
    engine.store_prediction(pred2)
    engine.learn_from_outcome(engine.history[1]['id'], False)
    
    # Prediction 3: High score, failure -> inaccurate
    pred3 = {
        'pr_number': 3, 'repo': 'test/repo', 'pr_url': 'url3',
        'prediction_score': 90, 'omens': [],
        'mystical_message': 'msg', 'recommendations': []
    }
    engine.store_prediction(pred3)
    engine.learn_from_outcome(engine.history[2]['id'], False)
    
    # Prediction 4: No outcome yet
    pred4 = {
        'pr_number': 4, 'repo': 'test/repo', 'pr_url': 'url4',
        'prediction_score': 75, 'omens': [],
        'mystical_message': 'msg', 'recommendations': []
    }
    engine.store_prediction(pred4)
    
    # Calculate accuracy: 2 accurate out of 3 with outcomes = 66.67%
    accuracy = engine.get_accuracy_rate()
    assert 66.0 <= accuracy <= 67.0
    print(f"✓ Accuracy calculated correctly: {accuracy:.1f}% (2/3 accurate)")


def test_pattern_failure_tracking():
    """Test tracking of pattern failures."""
    print("\nTesting pattern failure tracking...")
    
    engine = PredictionEngine()
    
    # Create prediction with multiple omens
    prediction = {
        'pr_number': 1, 'repo': 'test/repo', 'pr_url': 'url',
        'prediction_score': 50,
        'omens': [
            {'type': 'minor', 'title': 'Issue 1', 'description': 'desc',
             'file': 'src/utils.py', 'severity': 3},
            {'type': 'major', 'title': 'Issue 2', 'description': 'desc',
             'file': 'src/main.py', 'severity': 6},
            {'type': 'dark', 'title': 'Issue 3', 'description': 'desc',
             'file': 'src/auth.py', 'severity': 9}
        ],
        'mystical_message': 'msg', 'recommendations': []
    }
    engine.store_prediction(prediction)
    engine.learn_from_outcome(engine.history[0]['id'], False)
    
    # Verify all patterns tracked
    assert engine.pattern_failures['minor:src/utils.py'] == 1
    assert engine.pattern_failures['major:src/main.py'] == 1
    assert engine.pattern_failures['dark:src/auth.py'] == 1
    print("✓ All omen patterns tracked on failure")
    
    # Add another failure for same file
    prediction2 = {
        'pr_number': 2, 'repo': 'test/repo', 'pr_url': 'url2',
        'prediction_score': 55,
        'omens': [
            {'type': 'major', 'title': 'Issue', 'description': 'desc',
             'file': 'src/main.py', 'severity': 7}
        ],
        'mystical_message': 'msg', 'recommendations': []
    }
    engine.store_prediction(prediction2)
    engine.learn_from_outcome(engine.history[1]['id'], False)
    
    # Verify count incremented
    assert engine.pattern_failures['major:src/main.py'] == 2
    print("✓ Pattern failure count incremented correctly")


def test_enhance_prediction_no_history():
    """Test enhancing prediction with no historical data."""
    print("\nTesting prediction enhancement (no history)...")
    
    engine = PredictionEngine()
    
    ai_prediction = {
        'prediction_score': 75,
        'omens': [
            {'type': 'minor', 'title': 'Issue', 'description': 'desc',
             'file': 'src/test.py', 'severity': 3}
        ],
        'mystical_message': 'msg',
        'recommendations': []
    }
    
    enhanced = engine.enhance_prediction(ai_prediction)
    
    # Should be unchanged (no historical data)
    assert enhanced['prediction_score'] == 75
    assert enhanced['omens'][0]['severity'] == 3
    assert 'historical_failures' not in enhanced['omens'][0]
    print("✓ Prediction unchanged when no historical data exists")


def test_enhance_prediction_with_history():
    """Test enhancing prediction with historical failure data."""
    print("\nTesting prediction enhancement (with history)...")
    
    engine = PredictionEngine()
    
    # Build up failure history for a pattern
    for i in range(5):
        pred = {
            'pr_number': i, 'repo': 'test/repo', 'pr_url': f'url{i}',
            'prediction_score': 60,
            'omens': [
                {'type': 'major', 'title': 'Bug', 'description': 'desc',
                 'file': 'src/buggy.py', 'severity': 6}
            ],
            'mystical_message': 'msg', 'recommendations': []
        }
        engine.store_prediction(pred)
        engine.learn_from_outcome(engine.history[i]['id'], False)
    
    # Verify pattern has 5 failures
    assert engine.pattern_failures['major:src/buggy.py'] == 5
    print("✓ Built up 5 failures for pattern major:src/buggy.py")
    
    # Now enhance a new prediction with same pattern
    ai_prediction = {
        'prediction_score': 80,
        'omens': [
            {'type': 'major', 'title': 'Potential Bug', 'description': 'This looks risky',
             'file': 'src/buggy.py', 'severity': 6}
        ],
        'mystical_message': 'Mostly clear',
        'recommendations': []
    }
    
    enhanced = engine.enhance_prediction(ai_prediction)
    
    # Severity should be increased (max +2)
    assert enhanced['omens'][0]['severity'] == 8  # 6 + 2
    print(f"✓ Severity enhanced: 6 -> {enhanced['omens'][0]['severity']}")
    
    # Should have historical_failures annotation (> 3)
    assert enhanced['omens'][0]['historical_failures'] == 5
    assert '5 times previously' in enhanced['omens'][0]['description']
    print("✓ Historical failure annotation added")
    
    # Score should be reduced
    assert enhanced['prediction_score'] < 80
    print(f"✓ Prediction score reduced: 80 -> {enhanced['prediction_score']}")


def test_enhance_prediction_severity_cap():
    """Test that severity enhancement is capped at 10."""
    print("\nTesting severity cap at 10...")
    
    engine = PredictionEngine()
    
    # Build up failures
    for i in range(10):
        pred = {
            'pr_number': i, 'repo': 'test/repo', 'pr_url': f'url{i}',
            'prediction_score': 50,
            'omens': [
                {'type': 'dark', 'title': 'Critical', 'description': 'desc',
                 'file': 'src/critical.py', 'severity': 9}
            ],
            'mystical_message': 'msg', 'recommendations': []
        }
        engine.store_prediction(pred)
        engine.learn_from_outcome(engine.history[i]['id'], False)
    
    # Enhance prediction with severity 9
    ai_prediction = {
        'prediction_score': 70,
        'omens': [
            {'type': 'dark', 'title': 'Critical Issue', 'description': 'desc',
             'file': 'src/critical.py', 'severity': 9}
        ],
        'mystical_message': 'msg',
        'recommendations': []
    }
    
    enhanced = engine.enhance_prediction(ai_prediction)
    
    # Should be capped at 10 (9 + 2 would be 11, but capped)
    assert enhanced['omens'][0]['severity'] == 10
    print("✓ Severity capped at 10 (9 + 2 -> 10)")


def test_get_pattern_failures():
    """Test getting failure count for specific patterns."""
    print("\nTesting get_pattern_failures...")
    
    engine = PredictionEngine()
    
    # No failures initially
    assert engine.get_pattern_failures('major', 'src/test.py') == 0
    print("✓ Returns 0 for unknown pattern")
    
    # Add some failures
    engine.pattern_failures['major:src/test.py'] = 3
    engine.pattern_failures['dark:src/auth.py'] = 7
    
    assert engine.get_pattern_failures('major', 'src/test.py') == 3
    assert engine.get_pattern_failures('dark', 'src/auth.py') == 7
    print("✓ Returns correct failure counts")


if __name__ == '__main__':
    print("Running PredictionEngine tests...\n")
    print("=" * 60)
    
    test_store_prediction()
    test_store_multiple_predictions()
    test_learn_from_outcome_success()
    test_learn_from_outcome_failure()
    test_accuracy_calculation()
    test_pattern_failure_tracking()
    test_enhance_prediction_no_history()
    test_enhance_prediction_with_history()
    test_enhance_prediction_severity_cap()
    test_get_pattern_failures()
    
    print("\n" + "=" * 60)
    print("\n✅ All PredictionEngine tests passed!")
