"""
Prediction Engine for Crystal Ball CI/CD system.

This module manages historical prediction data and enhances predictions
based on past patterns and outcomes.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from uuid import uuid4
from models import Prediction

logger = logging.getLogger(__name__)


class PredictionEngine:
    """
    Manages prediction history and enhances predictions with historical data.
    
    Responsibilities:
    - Store predictions in memory
    - Track historical outcomes
    - Calculate accuracy metrics
    - Enhance predictions with historical patterns
    - Identify recurring failure patterns
    """
    
    def __init__(self):
        """
        Initialize Prediction Engine with empty history.
        
        Validates: Requirements 3.1
        """
        self.history: List[Dict[str, Any]] = []
        self.pattern_failures: Dict[str, int] = {}
        logger.info("PredictionEngine initialized with empty history")
    
    def store_prediction(self, prediction: Dict[str, Any]) -> None:
        """
        Store a prediction in memory.
        
        Adds UUID and timestamp if not present, then stores the prediction
        in the history list.
        
        Args:
            prediction: Prediction dictionary with all required fields
        
        Validates: Requirements 3.1
        """
        # Add UUID if not present
        if 'id' not in prediction:
            prediction['id'] = str(uuid4())
        
        # Add timestamp if not present
        if 'timestamp' not in prediction:
            prediction['timestamp'] = datetime.now().isoformat()
        
        # Store in history
        self.history.append(prediction)
        
        logger.info(
            f"Stored prediction {prediction['id']}: "
            f"score={prediction.get('prediction_score', 'unknown')}, "
            f"omens={len(prediction.get('omens', []))}"
        )
    
    def learn_from_outcome(self, prediction_id: str, actual_result: bool) -> None:
        """
        Record the actual deployment outcome for a prediction.
        
        Updates the prediction in history with the actual result and determines
        if the prediction was accurate. Also tracks pattern failures for omens
        that were associated with failed deployments.
        
        Args:
            prediction_id: UUID of the prediction to update
            actual_result: True if deployment succeeded, False if it failed
        
        Validates: Requirements 3.2, 3.3
        """
        # Find the prediction in history
        prediction = None
        for pred in self.history:
            if pred.get('id') == prediction_id:
                prediction = pred
                break
        
        if not prediction:
            logger.warning(f"Prediction {prediction_id} not found in history")
            return
        
        # Record the actual result
        prediction['actual_result'] = actual_result
        
        # Determine if prediction was accurate
        # A prediction is accurate if:
        # - High score (>= 70) and deployment succeeded
        # - Low score (< 70) and deployment failed
        prediction_score = prediction.get('prediction_score', 50)
        prediction['accurate'] = (
            (prediction_score >= 70 and actual_result) or
            (prediction_score < 70 and not actual_result)
        )
        
        logger.info(
            f"Recorded outcome for prediction {prediction_id}: "
            f"actual_result={actual_result}, accurate={prediction['accurate']}"
        )
        
        # Track pattern failures if deployment failed
        if not actual_result:
            omens = prediction.get('omens', [])
            for omen in omens:
                omen_type = omen.get('type', 'unknown')
                file = omen.get('file', 'unknown')
                pattern_key = f"{omen_type}:{file}"
                
                # Increment failure count for this pattern
                self.pattern_failures[pattern_key] = (
                    self.pattern_failures.get(pattern_key, 0) + 1
                )
                
                logger.debug(
                    f"Incremented failure count for pattern {pattern_key}: "
                    f"{self.pattern_failures[pattern_key]}"
                )
    
    def get_accuracy_rate(self) -> float:
        """
        Calculate overall prediction accuracy rate.
        
        Returns the percentage of predictions that were accurate among
        those that have recorded outcomes.
        
        Returns:
            Accuracy rate as a percentage (0.0-100.0), or 0.0 if no outcomes recorded
        
        Validates: Requirements 3.3
        """
        # Count predictions with outcomes
        predictions_with_outcomes = [
            pred for pred in self.history
            if pred.get('actual_result') is not None
        ]
        
        if not predictions_with_outcomes:
            logger.debug("No predictions with outcomes yet")
            return 0.0
        
        # Count accurate predictions
        accurate_predictions = [
            pred for pred in predictions_with_outcomes
            if pred.get('accurate', False)
        ]
        
        # Calculate accuracy rate
        accuracy_rate = (len(accurate_predictions) / len(predictions_with_outcomes)) * 100
        
        logger.info(
            f"Accuracy rate: {accuracy_rate:.1f}% "
            f"({len(accurate_predictions)}/{len(predictions_with_outcomes)})"
        )
        
        return accuracy_rate
    
    def get_pattern_failures(self, omen_type: str, file: str) -> int:
        """
        Get failure count for a specific pattern.
        
        Args:
            omen_type: Type of omen (minor, major, dark)
            file: File path associated with the omen
        
        Returns:
            Number of times this pattern has been associated with failures
        """
        pattern_key = f"{omen_type}:{file}"
        return self.pattern_failures.get(pattern_key, 0)
    
    def enhance_prediction(self, ai_prediction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance prediction with historical data.
        
        This method:
        1. Increases severity for recurring patterns (max +2, cap at 10)
        2. Annotates omens with failure counts if > 3
        3. Recalculates prediction score based on enhanced severities
        
        Args:
            ai_prediction: Raw prediction from AI Analyzer
        
        Returns:
            Enhanced prediction with updated severities and annotations
        
        Validates: Requirements 3.4, 3.5
        """
        enhanced_prediction = ai_prediction.copy()
        omens = enhanced_prediction.get('omens', [])
        
        if not omens:
            logger.debug("No omens to enhance")
            return enhanced_prediction
        
        # Track if any enhancements were made
        enhancements_made = False
        original_severities = []
        enhanced_severities = []
        
        # Enhance each omen based on historical data
        for omen in omens:
            omen_type = omen.get('type', 'unknown')
            file = omen.get('file', 'unknown')
            original_severity = omen.get('severity', 5)
            original_severities.append(original_severity)
            
            # Get failure count for this pattern
            failure_count = self.get_pattern_failures(omen_type, file)
            
            # Increase severity for recurring patterns
            if failure_count > 0:
                # Increase by min(2, failure_count), capped at 10
                severity_increase = min(2, failure_count)
                new_severity = min(10, original_severity + severity_increase)
                omen['severity'] = new_severity
                enhanced_severities.append(new_severity)
                
                if new_severity != original_severity:
                    enhancements_made = True
                    logger.debug(
                        f"Enhanced omen severity: {original_severity} -> {new_severity} "
                        f"(pattern {omen_type}:{file} has {failure_count} failures)"
                    )
                
                # Annotate with failure count if > 3
                if failure_count > 3:
                    omen['historical_failures'] = failure_count
                    original_description = omen.get('description', '')
                    omen['description'] = (
                        f"{original_description} "
                        f"(⚠️ This pattern has failed {failure_count} times previously)"
                    )
                    logger.debug(f"Annotated omen with {failure_count} historical failures")
            else:
                enhanced_severities.append(original_severity)
        
        # Recalculate prediction score based on enhanced severities
        if enhancements_made and enhanced_severities:
            # Calculate average severity increase
            avg_original = sum(original_severities) / len(original_severities)
            avg_enhanced = sum(enhanced_severities) / len(enhanced_severities)
            severity_increase_ratio = avg_enhanced / avg_original if avg_original > 0 else 1.0
            
            # Adjust prediction score (decrease by severity increase ratio)
            original_score = enhanced_prediction.get('prediction_score', 50)
            # Reduce score proportionally to severity increase, but not below 0
            score_reduction = int((severity_increase_ratio - 1.0) * 20)
            new_score = max(0, original_score - score_reduction)
            enhanced_prediction['prediction_score'] = new_score
            
            logger.info(
                f"Enhanced prediction: score {original_score} -> {new_score}, "
                f"avg severity {avg_original:.1f} -> {avg_enhanced:.1f}"
            )
        
        return enhanced_prediction
