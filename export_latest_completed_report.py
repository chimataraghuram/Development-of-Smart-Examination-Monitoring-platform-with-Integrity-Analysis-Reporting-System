import json
import database as db

with db.get_db_connection() as conn:
    latest = conn.execute(
        """
        SELECT s.user_id, s.started_at, s.ended_at
        FROM stats AS s
        WHERE s.exam_running = 0 AND s.ended_at IS NOT NULL
        ORDER BY s.ended_at DESC
        LIMIT 1
        """
    ).fetchone()

if latest is None:
    raise SystemExit('NO_COMPLETED_SESSION')

report = db.get_integrity_report(latest['user_id'])
report['export_metadata'] = {
    'latest_completed_user_id': latest['user_id'],
    'latest_completed_started_at': latest['started_at'],
    'latest_completed_ended_at': latest['ended_at'],
}

print(json.dumps(report, indent=2, ensure_ascii=False, default=str))
