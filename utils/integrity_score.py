import sqlite3

def calculate_integrity_score(candidate_id):

    connection = sqlite3.connect("database/exam.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT start_time
        FROM Session
        WHERE candidate_id=?
        ORDER BY session_id DESC
        LIMIT 1
    """, (candidate_id,))
    row = cursor.fetchone()
    start_time = row[0] if row and row[0] else None
    timestamp_filter = ""
    params = (candidate_id,)
    if start_time:
        timestamp_filter = "AND timestamp >= ?"
        params = (candidate_id, start_time)

    cursor.execute(f"""
        SELECT COUNT(*)
        FROM EventLog
        WHERE candidate_id=?
        AND event_type='Face Not Detected'
        {timestamp_filter}
    """, params)
    face_missing = cursor.fetchone()[0] or 0

    cursor.execute(f"""
        SELECT COUNT(*)
        FROM EventLog
        WHERE candidate_id=?
        AND event_type='Browser Focus Lost'
        {timestamp_filter}
    """, params)
    browser_lost = cursor.fetchone()[0] or 0

    score = 1000
    score -= face_missing * 100
    score -= browser_lost * 100

    score = max(score, 0)

    connection.close()

    return {
        "score": score,
        "face_missing": face_missing,
        "browser_lost": browser_lost
    }
