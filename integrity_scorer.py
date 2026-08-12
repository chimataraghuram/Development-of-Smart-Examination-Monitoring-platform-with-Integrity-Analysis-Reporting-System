# integrity_scorer.py
from collections import Counter
from datetime import datetime

SCORE_MAX = 1000
VIOLATION_DEDUCTION = 100

# Each recognized integrity violation reduces the score by the same 100 points.
VIOLATION_EVENTS = frozenset({
    'Face Not Detected',
    'Face Absence',
    'Multiple Faces',
    'Browser Focus Loss',
    'Tab Switching',
    'Copy Paste',
    'Suspicious Activity',
    'Suspicious App',
    'Screen Share',
    'Audio Noise',
})

# Kept as a public mapping for reporting and diagnostics.
EVENT_WEIGHTS = {event_type: VIOLATION_DEDUCTION for event_type in VIOLATION_EVENTS}

RISK_THRESHOLDS = {
    'Low Risk': (800, SCORE_MAX),
    'Medium Risk': (500, 799),
    'High Risk': (0, 499),
}


def get_event_deduction(event_type):
    """Return the fixed deduction for a monitored integrity violation."""
    return VIOLATION_DEDUCTION if event_type in VIOLATION_EVENTS else 0


class IntegrityScorer:
    """Calculate integrity metrics using a 1000-point, fixed-deduction model."""

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
            total_deduction += get_event_deduction(event_type)

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

        raw_score_from_events = max(0, SCORE_MAX - total_deduction)
        persisted_score = self.stats.get('integrity_score')
        final_score = self._to_number(persisted_score, raw_score_from_events) if persisted_score is not None else raw_score_from_events
        final_score = float(round(max(0, min(SCORE_MAX, final_score)), 1))

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
