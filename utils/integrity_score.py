import sqlite3

def calculate_integrity_score(candidate_id):

    connection = sqlite3.connect("database/exam.db")
    cursor = connection.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM EventLog
        WHERE candidate_id=?
        AND event_type='Face Not Detected'
    """, (candidate_id,))
    face_missing = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM EventLog
        WHERE candidate_id=?
        AND event_type='Browser Focus Lost'
    """, (candidate_id,))
    browser_lost = cursor.fetchone()[0]

    score = 100
    score -= face_missing * 5
    score -= browser_lost * 10

    score = max(score, 0)

    connection.close()

    return {
        "score": score,
        "face_missing": face_missing,
        "browser_lost": browser_lost
    }
