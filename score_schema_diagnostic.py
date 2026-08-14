import json
import database as db
from integrity_scorer import EVENT_WEIGHTS, IntegrityScorer

TABLES = ('users', 'stats', 'events', 'evidence')

with db.get_db_connection() as conn:
    schema = {}
    for table in TABLES:
        schema[table] = [dict(row) for row in conn.execute(f'PRAGMA table_info({table})')]

    latest = conn.execute(
        """
        SELECT s.user_id, s.started_at, s.ended_at, s.exam_running,
               u.name, u.student_id
        FROM stats AS s
        JOIN users AS u ON u.id = s.user_id
        WHERE s.exam_running = 0 AND s.ended_at IS NOT NULL
        ORDER BY s.ended_at DESC
        LIMIT 1
        """
    ).fetchone()

if latest is None:
    raise SystemExit('NO_COMPLETED_SESSION')

report = db.get_integrity_report(latest['user_id'])
event_breakdown = []
for event in report['events']:
    weight = EVENT_WEIGHTS.get(event['type'], 0)
    deducted = event.get('deducted', 1)
    calculated_deduction = weight * deducted
    event_breakdown.append({
        'event_id': event['id'],
        'type': event['type'],
        'timestamp': event['timestamp'],
        'stored_deducted': deducted,
        'weight': weight,
        'weighted_deduction': calculated_deduction,
    })

output = {
    'schema': schema,
    'latest_completed_session': dict(latest),
    'scoring_algorithm': {
        'score_source': 'stats.integrity_score when present; otherwise 100 - weighted event deductions',
        'event_weight_formula': 'EVENT_WEIGHTS[event.type] * event.deducted',
        'raw_score_formula': 'max(0, 100 - total_deduction)',
        'face_ratio_formula': '((max(1, floor(duration_seconds / 2)) - min(face_not_detected_count, intervals)) / intervals) * 100',
        'risk_bands': {'Low Risk': '80-100', 'Medium Risk': '50-79', 'High Risk': '0-49'},
    },
    'report_summary': {
        'score': report['score'],
        'raw_score_from_events': report['raw_score_from_events'],
        'total_deduction': report['total_deduction'],
        'face_ratio': report['face_ratio'],
        'risk_label': report['risk_label'],
        'event_counts': report['event_counts'],
        'stats_integrity_score': report['stats'].get('integrity_score'),
        'event_count': len(report['events']),
    },
    'event_breakdown': event_breakdown,
}

print(json.dumps(output, indent=2, ensure_ascii=False, default=str))
