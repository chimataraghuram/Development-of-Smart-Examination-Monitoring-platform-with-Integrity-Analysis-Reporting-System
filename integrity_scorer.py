# integrity_scorer.py
from collections import Counter
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
    """Calculate integrity metrics without optional data-analysis dependencies."""

    def __init__(self, events, stats=None):
        self.events = [event for event in (events or []) if isinstance(event, dict)]
        self.stats = stats or {}

    @staticmethod
    def _to_number(value, default=0.0):
        try:
            return float(value)
        except (TypeError, ValueError):
            return float(default)

    @staticmethod
    def _to_datetime(value):
        if value is None or value == '':
            return None
        if isinstance(value, datetime):
            return value.replace(tzinfo=None) if value.tzinfo else value
        if isinstance(value, str):
            try:
                parsed = datetime.fromisoformat(value.replace('Z', '+00:00'))
                return parsed.replace(tzinfo=None) if parsed.tzinfo else parsed
            except ValueError:
                return None
        return None

    def compute(self):
        total_deduction = 0.0
        event_counts = Counter()

        for event in self.events:
            event_type = event.get('type')
            if event_type:
                event_counts[event_type] += 1

            weight = self._to_number(EVENT_WEIGHTS.get(event_type, 0))
            deducted = self._to_number(event.get('deducted', 1), default=1)
            total_deduction += weight * deducted

        face_not_detected = self._to_number(self.stats.get('face_not_detected_count', 0))
        started_at = self._to_datetime(self.stats.get('started_at'))
        ended_at = self._to_datetime(self.stats.get('ended_at')) or datetime.now()

        if started_at:
            total_seconds = max(0, (ended_at - started_at).total_seconds())
            total_intervals = max(1, int(total_seconds / 2))
        else:
            total_intervals = 1

        absent_intervals = min(max(0, face_not_detected), total_intervals)
        face_ratio = ((total_intervals - absent_intervals) / total_intervals) * 100
        face_ratio = float(round(face_ratio, 1))

        base_score = self.stats.get('integrity_score')
        raw_score_from_events = max(0, 100 - total_deduction)
        final_score = self._to_number(base_score, raw_score_from_events) if base_score is not None else raw_score_from_events
        final_score = float(round(max(0, min(100, final_score)), 1))

        return {
            'score': final_score,
            'face_ratio': face_ratio,
            'risk_label': self._get_risk_label(final_score),
            'total_deduction': float(total_deduction),
            'event_counts': dict(event_counts),
            'raw_score_from_events': float(round(raw_score_from_events, 1)),
        }

    @staticmethod
    def _get_risk_label(score):
        for label, (lo, hi) in RISK_THRESHOLDS.items():
            if lo <= score <= hi:
                return label
        return 'High Risk'
