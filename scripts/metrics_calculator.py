"""
Metrics Calculator for Belevita ROI Dashboard
Calculates key performance metrics from extracted data.
"""

import json
from datetime import datetime, timedelta
from typing import List, Dict, Any
from collections import defaultdict
import pandas as pd
import numpy as np

# Import settings
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from config.settings import RESPONSE_TIME_OUTLIER_THRESHOLD


class MetricsCalculator:
    """
    Calculates business metrics for the dashboard.
    """

    def __init__(self, sessions: List[Dict[str, Any]]):
        """
        Initialize with session data.

        Args:
            sessions: List of enriched session dictionaries
        """
        self.sessions = sessions
        self.df = pd.DataFrame(sessions)

        # Convert datetime strings to datetime objects
        if not self.df.empty:
            self.df['started_at'] = pd.to_datetime(self.df['started_at'], format='ISO8601')
            self.df['ended_at'] = pd.to_datetime(self.df['ended_at'], format='ISO8601', errors='coerce')
            self.df['date'] = self.df['started_at'].dt.date

    def calculate_volume_metrics(self) -> Dict[str, Any]:
        """
        Calculate volume of attendances metrics.

        Returns:
            Dictionary with volume metrics
        """
        if self.df.empty:
            return {}

        # Daily sessions count
        daily_sessions = self.df.groupby('date').size().reset_index(name='sessions_count')
        daily_sessions['date'] = daily_sessions['date'].astype(str)

        # Calculate 7-day moving average
        daily_sessions['ma_7day'] = daily_sessions['sessions_count'].rolling(window=7, min_periods=1).mean()

        # Weekly aggregation
        self.df['week'] = self.df['started_at'].dt.to_period('W')
        weekly_sessions = self.df.groupby('week').size().reset_index(name='sessions_count')
        weekly_sessions['week'] = weekly_sessions['week'].astype(str)

        # Monthly aggregation
        self.df['month'] = self.df['started_at'].dt.to_period('M')
        monthly_sessions = self.df.groupby('month').size().reset_index(name='sessions_count')
        monthly_sessions['month'] = monthly_sessions['month'].astype(str)

        # Peak hours analysis
        self.df['hour'] = self.df['started_at'].dt.hour
        hourly_distribution = self.df.groupby('hour').size().reset_index(name='sessions_count')

        # Unique leads per day
        daily_leads = self.df.groupby('date')['lead_id'].nunique().reset_index(name='unique_leads')
        daily_leads['date'] = daily_leads['date'].astype(str)

        return {
            'daily': daily_sessions.to_dict('records'),
            'weekly': weekly_sessions.to_dict('records'),
            'monthly': monthly_sessions.to_dict('records'),
            'hourly_distribution': hourly_distribution.to_dict('records'),
            'daily_unique_leads': daily_leads.to_dict('records'),
            'total_sessions': len(self.df),
            'total_unique_leads': self.df['lead_id'].nunique(),
            'average_sessions_per_day': daily_sessions['sessions_count'].mean(),
            'peak_hour': int(hourly_distribution.loc[hourly_distribution['sessions_count'].idxmax(), 'hour'])
        }

    def calculate_response_time_metrics(self) -> Dict[str, Any]:
        """
        Calculate average response time metrics.

        Returns:
            Dictionary with response time metrics
        """
        if self.df.empty:
            return {}

        response_times = []
        daily_response_times = defaultdict(list)

        for _, session in self.df.iterrows():
            messages = session.get('messages', [])

            if not messages or len(messages) < 2:
                continue

            # Find first human message and first AI response
            first_human_time = None
            first_ai_time = None

            for msg in messages:
                message_data = msg.get('message', {})
                msg_type = message_data.get('type')

                if msg_type == 'human' and first_human_time is None:
                    first_human_time = session['started_at']

                if msg_type == 'ai' and first_human_time is not None and first_ai_time is None:
                    first_ai_time = session['started_at']
                    break

            # Calculate response time (for now, using started_at as proxy)
            # In real implementation, would parse message timestamps
            if session.get('ended_at') and pd.notna(session['ended_at']):
                duration = (session['ended_at'] - session['started_at']).total_seconds()

                # Filter out outliers and invalid values
                if 0 < duration < 86400:  # Less than 24 hours
                    response_time_seconds = duration / max(session.get('message_count', 1), 1)
                    response_times.append(response_time_seconds)
                    daily_response_times[session['date']].append(response_time_seconds)

        # Calculate daily medians
        daily_metrics = []
        for date, times in sorted(daily_response_times.items()):
            daily_metrics.append({
                'date': str(date),
                'median_response_time': float(np.median(times)),
                'avg_response_time': float(np.mean(times)),
                'p95_response_time': float(np.percentile(times, 95))
            })

        return {
            'daily': daily_metrics,
            'overall_median': float(np.median(response_times)) if response_times else 0,
            'overall_average': float(np.mean(response_times)) if response_times else 0,
            'overall_p95': float(np.percentile(response_times, 95)) if response_times else 0,
            'outliers_count': sum(1 for rt in response_times if rt > RESPONSE_TIME_OUTLIER_THRESHOLD)
        }

    def calculate_resolution_rate_metrics(self) -> Dict[str, Any]:
        """
        Calculate resolution rate metrics.

        Returns:
            Dictionary with resolution rate metrics
        """
        if self.df.empty:
            return {}

        total_sessions = len(self.df)
        completed_sessions = len(self.df[self.df['status'] == 'completed'])

        resolution_rate = (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0

        # Breakdown by reason_interaction
        breakdown_by_reason = []
        if 'reason_interaction' in self.df.columns:
            for reason in self.df['reason_interaction'].unique():
                if pd.isna(reason):
                    continue

                reason_df = self.df[self.df['reason_interaction'] == reason]
                reason_total = len(reason_df)
                reason_completed = len(reason_df[reason_df['status'] == 'completed'])
                reason_rate = (reason_completed / reason_total * 100) if reason_total > 0 else 0

                breakdown_by_reason.append({
                    'reason': reason,
                    'total_sessions': reason_total,
                    'completed_sessions': reason_completed,
                    'resolution_rate': round(reason_rate, 2)
                })

        # Weekly resolution rate trend
        weekly_metrics = []
        for week in self.df['week'].unique():
            week_df = self.df[self.df['week'] == week]
            week_total = len(week_df)
            week_completed = len(week_df[week_df['status'] == 'completed'])
            week_rate = (week_completed / week_total * 100) if week_total > 0 else 0

            weekly_metrics.append({
                'week': str(week),
                'resolution_rate': round(week_rate, 2),
                'total_sessions': week_total,
                'completed_sessions': week_completed
            })

        return {
            'overall_rate': round(resolution_rate, 2),
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'active_sessions': len(self.df[self.df['status'] == 'active']),
            'failed_sessions': len(self.df[self.df['status'] == 'failed']),
            'breakdown_by_reason': breakdown_by_reason,
            'weekly_trend': weekly_metrics
        }

    def calculate_sentiment_metrics(self) -> Dict[str, Any]:
        """
        Calculate sentiment analysis metrics.

        Returns:
            Dictionary with sentiment metrics
        """
        if self.df.empty or 'analyse_sentimental' not in self.df.columns:
            return {}

        # Overall sentiment distribution
        sentiment_counts = self.df['analyse_sentimental'].value_counts().to_dict()

        total_with_sentiment = sum(sentiment_counts.values())

        sentiment_distribution = {
            'Positivo': sentiment_counts.get('Positivo', 0),
            'Neutro': sentiment_counts.get('Neutro', 0),
            'Negativo': sentiment_counts.get('Negativo', 0),
            'None': sentiment_counts.get(None, 0) + sentiment_counts.get('', 0)
        }

        sentiment_percentages = {
            k: round((v / len(self.df) * 100), 2) if len(self.df) > 0 else 0
            for k, v in sentiment_distribution.items()
        }

        # Weekly sentiment trend
        weekly_sentiment = []
        for week in self.df['week'].unique():
            week_df = self.df[self.df['week'] == week]
            week_sentiments = week_df['analyse_sentimental'].value_counts().to_dict()

            weekly_sentiment.append({
                'week': str(week),
                'Positivo': week_sentiments.get('Positivo', 0),
                'Neutro': week_sentiments.get('Neutro', 0),
                'Negativo': week_sentiments.get('Negativo', 0),
                'total': len(week_df)
            })

        # Correlation with resolution rate
        completed_df = self.df[self.df['status'] == 'completed']
        sentiment_resolution_correlation = {}

        for sentiment in ['Positivo', 'Neutro', 'Negativo']:
            sentiment_df = self.df[self.df['analyse_sentimental'] == sentiment]
            if len(sentiment_df) > 0:
                sentiment_completed = len(sentiment_df[sentiment_df['status'] == 'completed'])
                sentiment_resolution_correlation[sentiment] = round(
                    (sentiment_completed / len(sentiment_df) * 100), 2
                )

        return {
            'distribution': sentiment_distribution,
            'percentages': sentiment_percentages,
            'weekly_trend': weekly_sentiment,
            'correlation_with_resolution': sentiment_resolution_correlation,
            'positive_rate': sentiment_percentages.get('Positivo', 0),
            'negative_rate': sentiment_percentages.get('Negativo', 0)
        }

    def calculate_all_metrics(self) -> Dict[str, Any]:
        """
        Calculate all metrics.

        Returns:
            Dictionary containing all calculated metrics
        """
        print("Calculating metrics...")

        metrics = {
            'volume': self.calculate_volume_metrics(),
            'response_time': self.calculate_response_time_metrics(),
            'resolution_rate': self.calculate_resolution_rate_metrics(),
            'sentiment': self.calculate_sentiment_metrics(),
            'metadata': {
                'calculated_at': datetime.now().isoformat(),
                'total_sessions_analyzed': len(self.df),
                'date_range': {
                    'start': self.df['started_at'].min().isoformat() if not self.df.empty else None,
                    'end': self.df['started_at'].max().isoformat() if not self.df.empty else None
                }
            }
        }

        print(f"Metrics calculated for {len(self.df)} sessions")
        return metrics


if __name__ == "__main__":
    print("Metrics Calculator for Belevita ROI Dashboard")
    print("=" * 50)
    print("This module is meant to be imported and used with extracted data.")
    print("Run generate_report.py to calculate metrics and generate the dashboard.")
