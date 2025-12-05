"""
AI Analyzer for Crystal Ball CI/CD system.

This module uses Anthropic's Claude API to analyze code diffs and generate
predictions about deployment success with mystical-themed messaging.
"""

import json
import logging
from typing import Dict, Any, Optional
from anthropic import Anthropic, APIError, RateLimitError

logger = logging.getLogger(__name__)


class AIAnalyzer:
    """
    AI-powered code diff analyzer using Anthropic Claude.
    
    This class handles:
    - Constructing structured prompts for LLM analysis
    - Calling the Anthropic API
    - Parsing and validating LLM responses
    - Classifying omens by severity
    - Generating fallback predictions on failures
    """
    
    def __init__(self, api_key: str):
        """
        Initialize the AI Analyzer with Anthropic client.
        
        Args:
            api_key: Anthropic API key for authentication
        """
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-3-5-haiku-20241022"  # Claude 3.5 Haiku
        logger.info("AIAnalyzer initialized with Anthropic client")
    
    def _construct_prompt(self, diff: str, context: Dict[str, Any]) -> str:
        """
        Construct structured prompt for LLM analysis.
        
        Args:
            diff: The code diff to analyze
            context: PR context (files_changed, lines_added, lines_removed, repo)
        
        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a STRICT security-focused code oracle. Your role is to be a HARSH critic and find EVERY possible issue.

Code Diff:
{diff}

Context:
- Files changed: {context.get('files_changed', 0)}
- Lines added: {context.get('lines_added', 0)}
- Lines removed: {context.get('lines_removed', 0)}
- Repository: {context.get('repo', 'unknown')}

CRITICAL MISSION: Analyze this diff with EXTREME SKEPTICISM. Be a tough critic - assume code is guilty until proven innocent.

MANDATORY SECURITY CHECKS (severity 8-10 = DARK OMENS):
🔴 Code Injection: eval(), exec(), compile() usage
🔴 Deserialization: pickle.loads(), yaml.load() without safe_load
🔴 Command Injection: os.system(), subprocess with shell=True, string concatenation in commands
🔴 SQL Injection: String concatenation/f-strings in SQL queries (use parameterized queries!)
🔴 Hardcoded Secrets: API keys, passwords, tokens, connection strings in code
🔴 Path Traversal: File operations without path validation, user input in file paths
🔴 XSS/Injection: Missing input sanitization, unescaped output
🔴 Exposed Debug: Debug endpoints, environment variable dumps, stack traces to users

ADDITIONAL CHECKS (severity 4-7 = MAJOR):
⚠️ Missing error handling, unvalidated inputs
⚠️ Race conditions, concurrency issues
⚠️ Breaking API changes without versioning
⚠️ Memory leaks, resource exhaustion
⚠️ Missing authentication/authorization
⚠️ Logging sensitive data

SCORING RULES - BE HARSH:
- ANY security vulnerability = score MUST be 40 or below
- Multiple critical issues = score 20 or below
- Hardcoded secrets = automatic 15 score
- Command/SQL injection = automatic 10 score
- No issues at all = 95-100 (rare!)
- Minor issues only = 75-90

Return ONLY valid JSON (no markdown, no code blocks):
{{
    "prediction_score": <number 0-100>,
    "omens": [
        {{
            "type": "minor|major|dark",
            "title": "<specific technical issue>",
            "description": "<explain the danger and impact in mystical but clear language>",
            "file": "<exact file path>",
            "severity": <number 1-10>
        }}
    ],
    "mystical_message": "<mystical fortune teller summary - encouraging if truly safe, DIRE WARNINGS if dangerous>",
    "recommendations": ["<specific fix, be technical and actionable>", ...]
}}

BE THOROUGH. FIND EVERYTHING. NO CODE IS PERFECT."""
        
        return prompt
    
    def classify_omen_type(self, severity: int) -> str:
        """
        Map severity (1-10) to omen type.
        
        Args:
            severity: Numeric severity from 1-10
        
        Returns:
            Omen type: 'minor', 'major', or 'dark'
        
        Validates: Requirements 2.4
        """
        if 1 <= severity <= 3:
            return 'minor'
        elif 4 <= severity <= 7:
            return 'major'
        elif 8 <= severity <= 10:
            return 'dark'
        else:
            # Default to major for out-of-range values
            logger.warning(f"Severity {severity} out of range, defaulting to 'major'")
            return 'major'
    
    def create_fallback_prediction(self) -> Dict[str, Any]:
        """
        Generate fallback prediction when LLM fails.
        
        Returns a safe default prediction with 50% score and generic warning.
        
        Returns:
            Fallback prediction dictionary
        
        Validates: Requirements 8.3, 11.4
        """
        logger.warning("Creating fallback prediction due to LLM failure")
        return {
            'prediction_score': 50,
            'omens': [{
                'type': 'major',
                'title': 'Analysis Unavailable',
                'description': 'The mystical oracle is temporarily unavailable. Please review changes manually.',
                'file': 'unknown',
                'severity': 5
            }],
            'mystical_message': 'The spirits are silent... Proceed with caution.',
            'recommendations': ['Review changes carefully', 'Run tests locally']
        }
    
    async def analyze_code_diff(self, diff: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze code diff using LLM and return prediction.
        
        This method:
        1. Constructs a structured prompt
        2. Calls the Anthropic API
        3. Parses and validates the JSON response
        4. Classifies omens by severity
        5. Returns fallback on any failure
        
        Args:
            diff: The code diff to analyze
            context: PR context with files_changed, lines_added, lines_removed, repo
        
        Returns:
            Prediction dictionary with:
                - prediction_score: int (0-100)
                - omens: list of omen dictionaries
                - mystical_message: str
                - recommendations: list of strings
        
        Validates: Requirements 2.1, 2.2, 11.3
        """
        try:
            # Construct the prompt
            prompt = self._construct_prompt(diff, context)
            logger.info(f"Analyzing diff for repo: {context.get('repo', 'unknown')}")
            
            # Call Anthropic API
            message = self.client.messages.create(
                model=self.model,
                max_tokens=2048,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Extract response text
            response_text = message.content[0].text
            logger.debug(f"LLM response received: {len(response_text)} characters")
            
            # Parse JSON response
            try:
                prediction = json.loads(response_text)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                return self.create_fallback_prediction()
            
            # Validate response schema
            if not self._validate_response_schema(prediction):
                logger.error("LLM response missing required fields")
                return self.create_fallback_prediction()
            
            # Classify omens by severity
            for omen in prediction.get('omens', []):
                severity = omen.get('severity', 5)
                omen['type'] = self.classify_omen_type(severity)
            
            logger.info(f"Analysis complete: score={prediction['prediction_score']}, omens={len(prediction['omens'])}")
            return prediction
            
        except RateLimitError as e:
            logger.error(f"Anthropic API rate limit exceeded: {e}")
            # In a production system, we would queue this request
            # For now, return fallback
            return self.create_fallback_prediction()
            
        except APIError as e:
            logger.error(f"Anthropic API error: {e}")
            return self.create_fallback_prediction()
            
        except Exception as e:
            logger.error(f"Unexpected error during analysis: {e}", exc_info=True)
            return self.create_fallback_prediction()
    
    def _validate_response_schema(self, response: Dict[str, Any]) -> bool:
        """
        Validate that LLM response contains all required fields.
        
        Args:
            response: Parsed JSON response from LLM
        
        Returns:
            True if valid, False otherwise
        
        Validates: Requirements 11.3
        """
        required_fields = ['prediction_score', 'omens', 'mystical_message']
        
        # Check required fields exist
        for field in required_fields:
            if field not in response:
                logger.error(f"Missing required field: {field}")
                return False
        
        # Validate prediction_score is in range
        score = response.get('prediction_score')
        if not isinstance(score, int) or not (0 <= score <= 100):
            logger.error(f"Invalid prediction_score: {score}")
            return False
        
        # Validate omens is a list
        omens = response.get('omens')
        if not isinstance(omens, list):
            logger.error(f"Omens must be a list, got: {type(omens)}")
            return False
        
        # Validate each omen has required fields
        for i, omen in enumerate(omens):
            required_omen_fields = ['title', 'description', 'file', 'severity']
            for field in required_omen_fields:
                if field not in omen:
                    logger.error(f"Omen {i} missing required field: {field}")
                    return False
            
            # Validate severity is in range
            severity = omen.get('severity')
            if not isinstance(severity, int) or not (1 <= severity <= 10):
                logger.error(f"Omen {i} has invalid severity: {severity}")
                return False
        
        # Validate mystical_message is a string
        if not isinstance(response.get('mystical_message'), str):
            logger.error("mystical_message must be a string")
            return False
        
        # Recommendations is optional, but if present must be a list
        if 'recommendations' in response:
            if not isinstance(response['recommendations'], list):
                logger.error("recommendations must be a list")
                return False
        else:
            # Add empty recommendations if not provided
            response['recommendations'] = []
        
        return True
