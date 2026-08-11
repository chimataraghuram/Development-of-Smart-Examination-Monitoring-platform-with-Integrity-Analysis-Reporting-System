# integrity_scorer.py
import pandas as pd
from datetime import datetime

EVENT_WEIGHTS = {
    'Face Not Detected': 2,
    'Face Absence': 5,
    'Multiple Faces': 7,
    'Browser Focus Loss': 3,
    'Tab Switching': 5,
    'Copy Paste': 8,
    'Suspicious App': 7,
    'Screen Share': 6,
    'Audio Noise': 4,
}

RISK_THRESHOLDS = {
    'Low Risk': (80, 100),
    'Medium Risk': (50, 79),
    'High Risk': (0, 49),
}

class IntegrityScorer:
    def __init__(self, events, stats=None):
        self.events = events or []
        self.stats = stats or {}
        self.df = pd.DataFrame(self.events)

    def _to_datetime(self, value):
        if value is None:
            return None
        if isinstance(value, datetime):
            return value
        try:
            return pd.to_datetime(value)
        except Exception:
            return None

    def compute(self):
        # 1. Weighted deduction
        if not self.df.empty:
            self.df['weight'] = self.df['type'].map(EVENT_WEIGHTS).fillna(0)
            if 'deducted' in self.df.columns:
                self.df['deduction'] = self.df['weight'] * self.df['deducted']
            else:
                self.df['deduction'] = self.df['weight']
            total_deduction = float(self.df['deduction'].sum())   # convert to float
        else:
            total_deduction = 0.0

        # 2. Face Presence Ratio
        face_not_detected = self.stats.get('face_not_detected_count', 0)
        started_at = self._to_datetime(self.stats.get('started_at'))
        ended_at = self._to_datetime(self.stats.get('ended_at')) or datetime.now()

        if started_at:
            total_seconds = (ended_at - started_at).total_seconds()
            total_intervals = max(1, int(total_seconds / 2))
        else:
            total_intervals = 1

        absent_intervals = min(face_not_detected, total_intervals)
        face_ratio = ((total_intervals - absent_intervals) / total_intervals) * 100
        face_ratio = float(round(face_ratio, 1))

        # 3. Normalize score
        base_score = self.stats.get('integrity_score', 100)
        raw_score_from_events = max(0, 100 - total_deduction)
        final_score = base_score if base_score is not None else raw_score_from_events
        final_score = max(0, min(100, final_score))
        final_score = float(round(final_score, 1))   # convert to float

        # 4. Risk label
        risk_label = self._get_risk_label(final_score)

        # 5. Event counts – convert to int
        if not self.df.empty:
            event_counts = self.df['type'].value_counts().to_dict()
            event_counts = {k: int(v) for k, v in event_counts.items()}
        else:
            event_counts = {}

        return {
            'score': final_score,
            'face_ratio': face_ratio,
            'risk_label': risk_label,
            'total_deduction': total_deduction,
            'event_counts': event_counts,
            'raw_score_from_events': float(round(raw_score_from_events, 1)),
        }

    def _get_risk_label(self, score):
        for label, (lo, hi) in RISK_THRESHOLDS.items():
            if lo <= score <= hi:
                return label
        return 'High Risk'