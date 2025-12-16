"""
Error Detector for Belevita ROI Dashboard
Detects errors using multiple methods: phrase matching and behavioral patterns.
"""

import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Set
from collections import Counter

# Import settings
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.settings import (
    ERROR_WEIGHTS,
    ERROR_THRESHOLDS,
    SHORT_CONVERSATION_THRESHOLD,
    RAPID_ABANDONMENT_THRESHOLD,
    STUCK_SESSION_THRESHOLD
)


class ErrorDetector:
    """
    Detects errors in conversations using multiple methods.
    """

    def __init__(self, error_phrases_path: str = "config/error_phrases.json"):
        """
        Initialize error detector with phrase lists.

        Args:
            error_phrases_path: Path to JSON file containing error phrases
        """
        self.error_phrases = self.load_error_phrases(error_phrases_path)
        self.weights = ERROR_WEIGHTS
        self.thresholds = ERROR_THRESHOLDS

    def load_error_phrases(self, path: str) -> Dict[str, List[str]]:
        """
        Load error phrases from JSON file.

        Args:
            path: Path to error phrases JSON file

        Returns:
            Dictionary of phrase categories
        """
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def detect_phrase_errors(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Method 1: Detect errors based on specific phrases in messages.

        Args:
            session: Session dictionary with messages

        Returns:
            Dictionary with phrase detection results
        """
        messages = session.get('messages', [])

        if not messages:
            return {
                'score': 0,
                'matched_phrases': [],
                'categories': {},
                'total_matches': 0
            }

        matched_phrases = []
        categories = {
            'error_indicators': 0,
            'frustration_indicators': 0,
            'escalation_phrases': 0
        }

        # Search for phrases in all messages
        for msg in messages:
            message_data = msg.get('message', {})
            content = message_data.get('content', '').lower()

            if not content:
                continue

            # Check each category of phrases
            for category, phrases in self.error_phrases.items():
                for phrase in phrases:
                    if phrase.lower() in content:
                        matched_phrases.append({
                            'phrase': phrase,
                            'category': category,
                            'message_type': message_data.get('type', 'unknown')
                        })
                        categories[category] += 1

        # Calculate score based on matches
        # More weight to frustration and escalation phrases
        total_matches = len(matched_phrases)

        if total_matches == 0:
            score = 0
        else:
            # Weighted scoring
            weighted_score = (
                categories['error_indicators'] * 1.0 +
                categories['frustration_indicators'] * 1.5 +
                categories['escalation_phrases'] * 2.0
            )

            # Normalize to 0-100 scale (cap at 100)
            score = min(100, weighted_score * 10)

        return {
            'score': round(score, 2),
            'matched_phrases': matched_phrases,
            'categories': categories,
            'total_matches': total_matches
        }

    def detect_behavioral_errors(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Method 2: Detect errors based on behavioral patterns.

        Args:
            session: Session dictionary

        Returns:
            Dictionary with behavioral pattern results
        """
        patterns_detected = []
        score_components = []

        # Pattern 1: Short conversation (< 3 messages, but only if we have messages)
        # If message_count is 0, it might be a correlation issue, not an error
        message_count = session.get('message_count', 0)
        if message_count > 0 and message_count < SHORT_CONVERSATION_THRESHOLD:
            patterns_detected.append('short_conversation')
            score_components.append(30)  # Strong indicator

        # Pattern 2: Rapid abandonment (< 2 minutes)
        started_at = session.get('started_at')
        ended_at = session.get('ended_at')

        if started_at and ended_at:
            try:
                if isinstance(started_at, str):
                    started_dt = datetime.fromisoformat(started_at.replace('Z', '+00:00'))
                else:
                    started_dt = started_at

                if isinstance(ended_at, str):
                    ended_dt = datetime.fromisoformat(ended_at.replace('Z', '+00:00'))
                else:
                    ended_dt = ended_at

                duration = (ended_dt - started_dt).total_seconds()

                if 0 < duration < RAPID_ABANDONMENT_THRESHOLD:
                    patterns_detected.append('rapid_abandonment')
                    score_components.append(40)  # Very strong indicator

                # Pattern 3: Stuck session (active > 30 minutes)
                elif session.get('status') == 'active' and duration > STUCK_SESSION_THRESHOLD:
                    patterns_detected.append('stuck_session')
                    score_components.append(35)

            except (ValueError, TypeError):
                pass

        # Pattern 4: Repeated messages (check for duplicate content)
        messages = session.get('messages', [])
        if messages:
            human_messages = []
            for msg in messages:
                message_data = msg.get('message', {})
                if message_data.get('type') == 'human':
                    content = message_data.get('content', '').strip().lower()
                    if content:
                        human_messages.append(content)

            if len(human_messages) >= 2:
                # Check for exact duplicates
                duplicates = len(human_messages) - len(set(human_messages))
                if duplicates > 0:
                    patterns_detected.append('repeated_messages')
                    score_components.append(25 * min(duplicates, 3))  # Cap at 3 repeats

        # Pattern 5: Failed or no sentiment (possible error)
        if session.get('status') == 'failed':
            patterns_detected.append('failed_session')
            score_components.append(50)  # Strong indicator

        if not session.get('analyse_sentimental') and session.get('status') == 'active':
            patterns_detected.append('no_sentiment_analysis')
            score_components.append(10)  # Weak indicator

        # Calculate final score (average of components, capped at 100)
        if score_components:
            score = min(100, sum(score_components) / len(score_components))
        else:
            score = 0

        return {
            'score': round(score, 2),
            'patterns': patterns_detected,
            'pattern_count': len(patterns_detected)
        }

    def detect_sentiment_errors(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Method 4: Correlate sentiment with error probability.

        Args:
            session: Session dictionary

        Returns:
            Dictionary with sentiment correlation results
        """
        raw_sentiment = session.get('analyse_sentimental')
        sentiment = (raw_sentiment or '').lower().strip()

        # Map sentiment to error probability score
        # Lower scores = less likely to be an error
        sentiment_scores = {
            'negativo': 80,
            'neutro': 15,
            'positivo': 5,
        }
        
        # If no sentiment, default to neutral (not necessarily an error)
        score = sentiment_scores.get(sentiment, 15)

        return {
            'score': score,
            'sentiment': raw_sentiment,
            'reasoning': f"Sentiment '{sentiment or 'none'}' correlates with {score}% error probability"
        }

    def calculate_combined_score(self, session: Dict[str, Any],
                                 phrase_result: Dict,
                                 behavioral_result: Dict,
                                 sentiment_result: Dict) -> float:
        """
        Calculate combined error confidence score using weighted average.

        Args:
            session: Session dictionary
            phrase_result: Results from phrase detection
            behavioral_result: Results from behavioral detection
            sentiment_result: Results from sentiment correlation

        Returns:
            Combined confidence score (0-100)
        """
        combined = (
            phrase_result['score'] * self.weights['phrase_matching'] +
            behavioral_result['score'] * self.weights['behavioral_patterns'] +
            sentiment_result['score'] * self.weights['sentiment_correlation']
        )

        # AI analysis weight is reserved for conversation_analyzer.py
        # Normalize by available weights (phrase + behavioral + sentiment = 0.65)
        # The scores are already 0-100, so just normalize by dividing by available weight
        available_weight = sum([
            self.weights['phrase_matching'],
            self.weights['behavioral_patterns'],
            self.weights['sentiment_correlation']
        ])

        if available_weight > 0:
            # This gives us the weighted average in 0-100 scale
            combined = combined / available_weight

        return min(100, round(combined, 2))

    def analyze_session(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single session for errors using all methods.

        Args:
            session: Session dictionary

        Returns:
            Complete error analysis results
        """
        phrase_result = self.detect_phrase_errors(session)
        behavioral_result = self.detect_behavioral_errors(session)
        sentiment_result = self.detect_sentiment_errors(session)

        combined_score = self.calculate_combined_score(
            session, phrase_result, behavioral_result, sentiment_result
        )

        # Determine confidence level
        if combined_score >= self.thresholds['high']:
            confidence_level = 'high'
        elif combined_score >= self.thresholds['medium']:
            confidence_level = 'medium'
        else:
            confidence_level = 'low'

        return {
            'session_id': session.get('id'),
            'confidence_score': combined_score,
            'confidence_level': confidence_level,
            'phrase_detection': phrase_result,
            'behavioral_patterns': behavioral_result,
            'sentiment_correlation': sentiment_result,
            'has_error': combined_score >= self.thresholds['medium']
        }

    def analyze_all_sessions(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze all sessions for errors.

        Args:
            sessions: List of session dictionaries

        Returns:
            Complete error analysis summary
        """
        print("Detecting errors using phrase matching and behavioral patterns...")

        results = []
        error_categories = Counter()

        for session in sessions:
            result = self.analyze_session(session)
            results.append(result)

            # Categorize errors
            if result['has_error']:
                patterns = result['behavioral_patterns']['patterns']
                for pattern in patterns:
                    error_categories[pattern] += 1

                # Also count phrase categories
                if result['phrase_detection']['total_matches'] > 0:
                    error_categories['phrase_matches'] += 1

        # Summary statistics
        high_confidence = [r for r in results if r['confidence_level'] == 'high']
        medium_confidence = [r for r in results if r['confidence_level'] == 'medium']
        low_confidence = [r for r in results if r['confidence_level'] == 'low']

        summary = {
            'total_sessions': len(sessions),
            'analyzed_sessions': len(results),
            'high_confidence_errors': len(high_confidence),
            'medium_confidence_errors': len(medium_confidence),
            'low_confidence_errors': len(low_confidence),
            'error_categories': dict(error_categories),
            'results': results,
            'metadata': {
                'analyzed_at': datetime.now().isoformat(),
                'methods_used': ['phrase_matching', 'behavioral_patterns', 'sentiment_correlation']
            }
        }

        print(f"Error detection complete:")
        print(f"  - High confidence errors: {len(high_confidence)}")
        print(f"  - Medium confidence errors: {len(medium_confidence)}")
        print(f"  - Low confidence errors: {len(low_confidence)}")

        return summary


if __name__ == "__main__":
    print("Error Detector for Belevita ROI Dashboard")
    print("=" * 50)
    print("This module is meant to be imported and used with extracted data.")
    print("Run generate_report.py to detect errors and generate the dashboard.")
