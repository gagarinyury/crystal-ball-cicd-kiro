"""
Tests for AI Analyzer module.

This module contains unit tests and property-based tests for the AIAnalyzer class.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from ai_analyzer import AIAnalyzer
from anthropic import APIError, RateLimitError


class TestAIAnalyzer:
    """Unit tests for AIAnalyzer class."""
    
    @pytest.fixture
    def analyzer(self):
        """Create AIAnalyzer instance for testing."""
        return AIAnalyzer(api_key="test_api_key")
    
    def test_initialization(self, analyzer):
        """Test that AIAnalyzer initializes correctly."""
        assert analyzer.client is not None
        assert analyzer.model == "claude-3-5-sonnet-20241022"
    
    def test_classify_omen_type_minor(self, analyzer):
        """Test omen classification for minor severity (1-3)."""
        assert analyzer.classify_omen_type(1) == 'minor'
        assert analyzer.classify_omen_type(2) == 'minor'
        assert analyzer.classify_omen_type(3) == 'minor'
    
    def test_classify_omen_type_major(self, analyzer):
        """Test omen classification for major severity (4-7)."""
        assert analyzer.classify_omen_type(4) == 'major'
        assert analyzer.classify_omen_type(5) == 'major'
        assert analyzer.classify_omen_type(6) == 'major'
        assert analyzer.classify_omen_type(7) == 'major'
    
    def test_classify_omen_type_dark(self, analyzer):
        """Test omen classification for dark severity (8-10)."""
        assert analyzer.classify_omen_type(8) == 'dark'
        assert analyzer.classify_omen_type(9) == 'dark'
        assert analyzer.classify_omen_type(10) == 'dark'
    
    def test_classify_omen_type_out_of_range(self, analyzer):
        """Test omen classification for out-of-range severity."""
        # Should default to 'major' for invalid values
        assert analyzer.classify_omen_type(0) == 'major'
        assert analyzer.classify_omen_type(11) == 'major'
        assert analyzer.classify_omen_type(-1) == 'major'
    
    def test_create_fallback_prediction(self, analyzer):
        """Test fallback prediction generation."""
        fallback = analyzer.create_fallback_prediction()
        
        # Validate structure
        assert fallback['prediction_score'] == 50
        assert len(fallback['omens']) == 1
        assert fallback['omens'][0]['type'] == 'major'
        assert fallback['omens'][0]['severity'] == 5
        assert 'mystical_message' in fallback
        assert 'recommendations' in fallback
        assert len(fallback['recommendations']) > 0
    
    def test_construct_prompt(self, analyzer):
        """Test prompt construction."""
        diff = "diff --git a/test.py b/test.py\n+print('hello')"
        context = {
            'files_changed': 1,
            'lines_added': 1,
            'lines_removed': 0,
            'repo': 'owner/repo'
        }
        
        prompt = analyzer._construct_prompt(diff, context)
        
        # Verify prompt contains key elements
        assert 'mystical code oracle' in prompt
        assert diff in prompt
        assert 'Files changed: 1' in prompt
        assert 'Lines added: 1' in prompt
        assert 'Repository: owner/repo' in prompt
        assert 'prediction_score' in prompt
        assert 'omens' in prompt
    
    def test_validate_response_schema_valid(self, analyzer):
        """Test response validation with valid response."""
        valid_response = {
            'prediction_score': 75,
            'omens': [
                {
                    'title': 'Test warning',
                    'description': 'Test description',
                    'file': 'test.py',
                    'severity': 5
                }
            ],
            'mystical_message': 'The spirits are pleased',
            'recommendations': ['Test recommendation']
        }
        
        assert analyzer._validate_response_schema(valid_response) is True
    
    def test_validate_response_schema_missing_field(self, analyzer):
        """Test response validation with missing required field."""
        invalid_response = {
            'prediction_score': 75,
            'omens': []
            # Missing mystical_message
        }
        
        assert analyzer._validate_response_schema(invalid_response) is False
    
    def test_validate_response_schema_invalid_score(self, analyzer):
        """Test response validation with invalid score."""
        invalid_response = {
            'prediction_score': 150,  # Out of range
            'omens': [],
            'mystical_message': 'Test'
        }
        
        assert analyzer._validate_response_schema(invalid_response) is False
    
    def test_validate_response_schema_invalid_omen(self, analyzer):
        """Test response validation with invalid omen."""
        invalid_response = {
            'prediction_score': 75,
            'omens': [
                {
                    'title': 'Test',
                    # Missing description, file, severity
                }
            ],
            'mystical_message': 'Test'
        }
        
        assert analyzer._validate_response_schema(invalid_response) is False
    
    def test_validate_response_schema_adds_empty_recommendations(self, analyzer):
        """Test that validation adds empty recommendations if missing."""
        response = {
            'prediction_score': 75,
            'omens': [],
            'mystical_message': 'Test'
            # No recommendations
        }
        
        assert analyzer._validate_response_schema(response) is True
        assert response['recommendations'] == []
    
    @pytest.mark.asyncio
    async def test_analyze_code_diff_success(self, analyzer):
        """Test successful code diff analysis."""
        diff = "diff --git a/test.py b/test.py\n+print('hello')"
        context = {
            'files_changed': 1,
            'lines_added': 1,
            'lines_removed': 0,
            'repo': 'owner/repo'
        }
        
        # Mock the Anthropic API response
        mock_response = {
            'prediction_score': 85,
            'omens': [
                {
                    'title': 'Minor style issue',
                    'description': 'Consider using logging instead of print',
                    'file': 'test.py',
                    'severity': 2
                }
            ],
            'mystical_message': 'The stars align favorably',
            'recommendations': ['Use logging module']
        }
        
        mock_message = Mock()
        mock_message.content = [Mock(text=json.dumps(mock_response))]
        
        with patch.object(analyzer.client.messages, 'create', return_value=mock_message):
            result = await analyzer.analyze_code_diff(diff, context)
        
        assert result['prediction_score'] == 85
        assert len(result['omens']) == 1
        assert result['omens'][0]['type'] == 'minor'  # Should be classified
        assert result['mystical_message'] == 'The stars align favorably'
    
    @pytest.mark.asyncio
    async def test_analyze_code_diff_json_parse_error(self, analyzer):
        """Test handling of malformed JSON response."""
        diff = "test diff"
        context = {'files_changed': 1, 'lines_added': 1, 'lines_removed': 0, 'repo': 'test'}
        
        # Mock response with invalid JSON
        mock_message = Mock()
        mock_message.content = [Mock(text="This is not valid JSON")]
        
        with patch.object(analyzer.client.messages, 'create', return_value=mock_message):
            result = await analyzer.analyze_code_diff(diff, context)
        
        # Should return fallback
        assert result['prediction_score'] == 50
        assert result['omens'][0]['type'] == 'major'
    
    @pytest.mark.asyncio
    async def test_analyze_code_diff_invalid_schema(self, analyzer):
        """Test handling of response with invalid schema."""
        diff = "test diff"
        context = {'files_changed': 1, 'lines_added': 1, 'lines_removed': 0, 'repo': 'test'}
        
        # Mock response with missing required fields
        mock_response = {
            'prediction_score': 75
            # Missing omens and mystical_message
        }
        
        mock_message = Mock()
        mock_message.content = [Mock(text=json.dumps(mock_response))]
        
        with patch.object(analyzer.client.messages, 'create', return_value=mock_message):
            result = await analyzer.analyze_code_diff(diff, context)
        
        # Should return fallback
        assert result['prediction_score'] == 50
    
    @pytest.mark.asyncio
    async def test_analyze_code_diff_rate_limit_error(self, analyzer):
        """Test handling of rate limit errors."""
        diff = "test diff"
        context = {'files_changed': 1, 'lines_added': 1, 'lines_removed': 0, 'repo': 'test'}
        
        # Mock rate limit error - create a proper mock response
        mock_response = Mock()
        mock_response.status_code = 429
        mock_error = RateLimitError("Rate limit exceeded", response=mock_response, body={})
        
        with patch.object(analyzer.client.messages, 'create', side_effect=mock_error):
            result = await analyzer.analyze_code_diff(diff, context)
        
        # Should return fallback
        assert result['prediction_score'] == 50
        assert result['omens'][0]['title'] == 'Analysis Unavailable'
    
    @pytest.mark.asyncio
    async def test_analyze_code_diff_api_error(self, analyzer):
        """Test handling of API errors."""
        diff = "test diff"
        context = {'files_changed': 1, 'lines_added': 1, 'lines_removed': 0, 'repo': 'test'}
        
        # Mock API error - create a proper mock request
        mock_request = Mock()
        mock_error = APIError("API error", request=mock_request, body={})
        
        with patch.object(analyzer.client.messages, 'create', side_effect=mock_error):
            result = await analyzer.analyze_code_diff(diff, context)
        
        # Should return fallback
        assert result['prediction_score'] == 50
    
    @pytest.mark.asyncio
    async def test_analyze_code_diff_classifies_all_omens(self, analyzer):
        """Test that all omens get classified by severity."""
        diff = "test diff"
        context = {'files_changed': 1, 'lines_added': 1, 'lines_removed': 0, 'repo': 'test'}
        
        # Mock response with multiple omens of different severities
        mock_response = {
            'prediction_score': 60,
            'omens': [
                {'title': 'Minor', 'description': 'Test', 'file': 'a.py', 'severity': 2},
                {'title': 'Major', 'description': 'Test', 'file': 'b.py', 'severity': 5},
                {'title': 'Dark', 'description': 'Test', 'file': 'c.py', 'severity': 9}
            ],
            'mystical_message': 'Mixed omens',
            'recommendations': []
        }
        
        mock_message = Mock()
        mock_message.content = [Mock(text=json.dumps(mock_response))]
        
        with patch.object(analyzer.client.messages, 'create', return_value=mock_message):
            result = await analyzer.analyze_code_diff(diff, context)
        
        assert result['omens'][0]['type'] == 'minor'
        assert result['omens'][1]['type'] == 'major'
        assert result['omens'][2]['type'] == 'dark'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
