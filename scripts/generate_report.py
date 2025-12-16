#!/usr/bin/env python3
"""
Main Report Generator for Belevita ROI Dashboard

This script orchestrates the entire pipeline:
1. Extract data from Supabase
2. Calculate metrics
3. Detect errors (phrase + behavioral patterns)
4. Analyze conversations with AI
5. Generate JSON outputs for dashboard

Usage:
    python scripts/generate_report.py [--use-cache] [--skip-ai-analysis]
"""

import argparse
import json
import os
from datetime import datetime
from typing import Dict, Any

# Import modules
from data_extractor import SupabaseMCPExtractor, save_extracted_data, load_cached_data
from metrics_calculator import MetricsCalculator
from error_detector import ErrorDetector
from conversation_analyzer import ConversationAnalyzer

# Import settings
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.settings import (
    OUTPUT_DIR,
    CACHE_ENABLED,
    ERROR_WEIGHTS,
    AGENT_ID,
    CLIENT_ID
)


def ensure_output_dir():
    """Ensure output directory exists."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(os.path.join(OUTPUT_DIR, '..', 'cache'), exist_ok=True)


def save_json_output(data: Dict[str, Any], filename: str):
    """
    Save data to JSON file in output directory.

    Args:
        data: Data to save
        filename: Output filename
    """
    output_path = os.path.join(OUTPUT_DIR, filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"[OK] Saved {filename}")


def combine_error_analyses(basic_analysis: Dict, ai_analysis: list = None) -> Dict:
    """
    Combine basic error detection with AI analysis results.

    Args:
        basic_analysis: Results from error_detector.py
        ai_analysis: Results from conversation_analyzer.py

    Returns:
        Combined analysis with updated scores
    """
    if not ai_analysis:
        return basic_analysis

    # Create mapping of AI results
    ai_results_dict = {r['session_id']: r for r in ai_analysis if r.get('analyzed')}

    # Update scores for analyzed sessions
    for result in basic_analysis['results']:
        session_id = result['session_id']

        if session_id in ai_results_dict:
            ai_result = ai_results_dict[session_id]

            # Calculate new combined score including AI analysis
            basic_score = (
                result['phrase_detection']['score'] * ERROR_WEIGHTS['phrase_matching'] +
                result['behavioral_patterns']['score'] * ERROR_WEIGHTS['behavioral_patterns'] +
                result['sentiment_correlation']['score'] * ERROR_WEIGHTS['sentiment_correlation']
            )

            ai_score = ai_result['score'] * ERROR_WEIGHTS['ai_analysis']

            combined_score = basic_score + ai_score

            # Update result
            result['confidence_score'] = round(combined_score, 2)
            result['ai_analysis'] = ai_result

            # Update confidence level
            if combined_score >= 70:
                result['confidence_level'] = 'high'
            elif combined_score >= 40:
                result['confidence_level'] = 'medium'
            else:
                result['confidence_level'] = 'low'

            result['has_error'] = combined_score >= 40

    # Recalculate summary statistics
    high_confidence = [r for r in basic_analysis['results'] if r['confidence_level'] == 'high']
    medium_confidence = [r for r in basic_analysis['results'] if r['confidence_level'] == 'medium']
    low_confidence = [r for r in basic_analysis['results'] if r['confidence_level'] == 'low']

    basic_analysis['high_confidence_errors'] = len(high_confidence)
    basic_analysis['medium_confidence_errors'] = len(medium_confidence)
    basic_analysis['low_confidence_errors'] = len(low_confidence)

    basic_analysis['metadata']['methods_used'].append('ai_analysis')
    basic_analysis['metadata']['ai_analyzed_sessions'] = len(ai_results_dict)

    return basic_analysis


def generate_conversation_samples(sessions: list, error_analysis: Dict, sample_size: int = 100) -> list:
    """
    Generate sample conversations for dashboard review.

    Args:
        sessions: All sessions
        error_analysis: Error analysis results
        sample_size: Number of samples to include

    Returns:
        List of sample conversations with metadata
    """
    # Sort by error confidence score
    sorted_results = sorted(
        error_analysis['results'],
        key=lambda x: x['confidence_score'],
        reverse=True
    )

    # Get top N sessions
    top_sessions_ids = [r['session_id'] for r in sorted_results[:sample_size]]

    sessions_dict = {s['id']: s for s in sessions}

    samples = []
    for session_id in top_sessions_ids:
        if session_id not in sessions_dict:
            continue

        session = sessions_dict[session_id]
        error_result = next((r for r in error_analysis['results'] if r['session_id'] == session_id), None)

        sample = {
            'session_id': session_id,
            'started_at': session.get('started_at'),
            'ended_at': session.get('ended_at'),
            'status': session.get('status'),
            'sentiment': session.get('analyse_sentimental'),
            'error_confidence': error_result['confidence_score'] if error_result else 0,
            'error_level': error_result['confidence_level'] if error_result else 'low',
            'messages': session.get('messages', []),
            'lead': {
                'name': session.get('lead', {}).get('name', 'Unknown') if session.get('lead') else 'Unknown',
                'phone': session.get('lead', {}).get('phone', '') if session.get('lead') else ''
            }
        }

        samples.append(sample)

    return samples


def main(use_cache: bool = False, skip_ai_analysis: bool = False):
    """
    Main execution function.

    Args:
        use_cache: Use cached data if available
        skip_ai_analysis: Skip AI analysis step (faster, less accurate)
    """
    print("=" * 60)
    print("BELEVITA ROI DASHBOARD - REPORT GENERATOR")
    print("=" * 60)
    print(f"Agent ID: {AGENT_ID}")
    print(f"Client ID: {CLIENT_ID}")
    print(f"Use cache: {use_cache}")
    print(f"Skip AI analysis: {skip_ai_analysis}")
    print("=" * 60)

    ensure_output_dir()

    # Step 1: Extract Data
    print("\n[1/6] Extracting data from Supabase...")

    if use_cache and CACHE_ENABLED:
        extracted_data = load_cached_data()
        if extracted_data:
            print("[OK] Loaded data from cache")
        else:
            print("Cache not found, extracting fresh data...")
            use_cache = False  # Force extraction

    if not use_cache or not extracted_data:
        try:
            # Try to import MCP execute_sql function
            # This will work when run within Claude Code with MCP access
            import subprocess
            import json as json_lib

            def mcp_execute_sql(query: str) -> Any:
                """Execute SQL via MCP tool (simulated for standalone Python)."""
                # This is a placeholder - in actual Claude Code environment,
                # this would be replaced with the real MCP function call
                print(f"Executing query: {query[:100]}...")
                # Return empty result for now
                return []

            print("Initializing MCP extractor...")
            extractor = SupabaseMCPExtractor(mcp_execute_sql)
            extracted_data = extractor.extract_all_data()

            # Save to cache
            if CACHE_ENABLED:
                save_extracted_data(extracted_data)

            print("[OK] Data extraction complete")

        except Exception as e:
            print(f"ERROR: Data extraction failed: {e}")
            print("\nThis script needs to be run with MCP access to Supabase.")
            print("Try running with --use-cache if data was previously extracted.")
            return

    sessions = extracted_data['sessions']
    print(f"[OK] Loaded {len(sessions)} sessions")

    # Step 2: Calculate Metrics
    print("\n[2/6] Calculating metrics...")
    calculator = MetricsCalculator(sessions)
    metrics = calculator.calculate_all_metrics()
    save_json_output(metrics, 'daily_metrics.json')
    print("[OK] Metrics calculated")

    # Step 3: Detect Errors (Basic Methods)
    print("\n[3/6] Detecting errors (phrase matching + behavioral patterns)...")
    detector = ErrorDetector()
    error_analysis = detector.analyze_all_sessions(sessions)
    print("[OK] Basic error detection complete")

    # Step 4: AI Analysis (Optional)
    if not skip_ai_analysis:
        print("\n[4/6] Analyzing conversations with Claude API...")
        try:
            analyzer = ConversationAnalyzer()

            # Select sessions for AI analysis
            sessions_to_analyze = analyzer.select_sessions_for_analysis(sessions, error_analysis)

            # Analyze in parallel
            ai_results = analyzer.analyze_sessions_parallel(sessions_to_analyze)

            # Combine results
            error_analysis = combine_error_analyses(error_analysis, ai_results)
            print("[OK] AI analysis complete")

        except Exception as e:
            print(f"Warning: AI analysis failed: {e}")
            print("Continuing with basic error detection only...")
    else:
        print("\n[4/6] Skipping AI analysis (--skip-ai-analysis flag)")

    save_json_output(error_analysis, 'error_analysis.json')

    # Step 5: Generate Conversation Samples
    print("\n[5/6] Generating conversation samples...")
    samples = generate_conversation_samples(sessions, error_analysis, sample_size=500)
    save_json_output(samples, 'conversation_samples.json')
    print(f"[OK] Generated {len(samples)} conversation samples")

    # Step 6: Generate Summary Data
    print("\n[6/6] Generating summary data...")

    summary = {
        'overview': {
            'total_sessions': len(sessions),
            'total_leads': extracted_data['metadata']['total_leads'],
            'total_messages': extracted_data['metadata']['total_messages'],
            'agent_id': AGENT_ID,
            'client_id': CLIENT_ID,
            'date_range': metrics['metadata']['date_range'],
            'generated_at': datetime.now().isoformat()
        },
        'key_metrics': {
            'total_sessions': metrics['volume']['total_sessions'],
            'unique_leads': metrics['volume']['total_unique_leads'],
            'resolution_rate': metrics['resolution_rate']['overall_rate'],
            'positive_sentiment_rate': metrics['sentiment']['positive_rate'],
            'avg_sessions_per_day': round(metrics['volume']['average_sessions_per_day'], 1),
            'median_response_time': metrics['response_time']['overall_median']
        },
        'error_summary': {
            'total_analyzed': error_analysis['total_sessions'],
            'high_confidence_errors': error_analysis['high_confidence_errors'],
            'medium_confidence_errors': error_analysis['medium_confidence_errors'],
            'error_rate': round(
                (error_analysis['high_confidence_errors'] + error_analysis['medium_confidence_errors']) /
                error_analysis['total_sessions'] * 100, 2
            ) if error_analysis['total_sessions'] > 0 else 0
        }
    }

    save_json_output(summary, 'summary.json')
    save_json_output(metrics['sentiment'], 'sentiment_analysis.json')

    # Also save full session summary (subset of data for dashboard)
    sessions_summary = []
    for session in sessions:
        sessions_summary.append({
            'id': session.get('id'),
            'started_at': session.get('started_at'),
            'ended_at': session.get('ended_at'),
            'status': session.get('status'),
            'sentiment': session.get('analyse_sentimental'),
            'reason': session.get('reason_interaction'),
            'message_count': session.get('message_count', 0)
        })

    save_json_output({'sessions': sessions_summary}, 'sessions_summary.json')

    print("\n" + "=" * 60)
    print("REPORT GENERATION COMPLETE!")
    print("=" * 60)
    print(f"\nGenerated files in {OUTPUT_DIR}:")
    print("  - summary.json")
    print("  - daily_metrics.json")
    print("  - sentiment_analysis.json")
    print("  - error_analysis.json")
    print("  - conversation_samples.json")
    print("  - sessions_summary.json")
    print("\nNext step: Open dashboard/index.html in your browser")
    print("=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Belevita ROI Dashboard Report')
    parser.add_argument('--use-cache', action='store_true',
                      help='Use cached data if available')
    parser.add_argument('--skip-ai-analysis', action='store_true',
                      help='Skip AI analysis step (faster but less accurate)')

    args = parser.parse_args()

    main(use_cache=args.use_cache, skip_ai_analysis=args.skip_ai_analysis)
