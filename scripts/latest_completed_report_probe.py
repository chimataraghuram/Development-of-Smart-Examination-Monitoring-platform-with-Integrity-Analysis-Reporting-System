import database as db

with db.get_db_connection() as conn:
    latest = conn.execute(
        """
        SELECT s.user_id, s.started_at, s.ended_at, u.name, u.student_id
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
print(f"LATEST_COMPLETED_USER_ID={latest['user_id']}")
print(f"LATEST_COMPLETED_NAME={latest['name']}")
print(f"LATEST_COMPLETED_STUDENT_ID={latest['student_id']}")
print(f"LATEST_COMPLETED_STARTED_AT={latest['started_at']}")
print(f"LATEST_COMPLETED_ENDED_AT={latest['ended_at']}")
print(f"REPORT_SCORE={report['score']}")
print(f"REPORT_RISK={report['risk_label']}")
print(f"REPORT_FACE_RATIO={report['face_ratio']}")
print(f"REPORT_EVENT_COUNT={len(report['events'])}")
print(f"REPORT_EVENT_TYPES={report['event_counts']}")
