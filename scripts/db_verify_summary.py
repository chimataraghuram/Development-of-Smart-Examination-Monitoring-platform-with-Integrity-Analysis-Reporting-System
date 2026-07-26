import sqlite3
import os

path = os.path.join(os.path.dirname(__file__), '..', 'database', 'exam.db')
path = os.path.normpath(path)
conn = sqlite3.connect(path)
cur = conn.cursor()

print('DB path:', path)

# Candidate summary
print('\n=== Candidate table summary ===')
cur.execute('PRAGMA table_info(Candidate)')
print('Columns:', [row[1] for row in cur.fetchall()])
cur.execute('SELECT COUNT(*) FROM Candidate')
print('Rows:', cur.fetchone()[0])
cur.execute('SELECT * FROM Candidate LIMIT 5')
for row in cur.fetchall():
    print(row)

# Session summary
print('\n=== Session table summary ===')
cur.execute('PRAGMA table_info(Session)')
print('Columns:', [row[1] for row in cur.fetchall()])
cur.execute('SELECT COUNT(*) FROM Session')
print('Rows:', cur.fetchone()[0])
cur.execute('SELECT * FROM Session ORDER BY session_id DESC LIMIT 5')
for row in cur.fetchall():
    print(row)

# EventLog summary
print('\n=== EventLog table summary ===')
cur.execute('PRAGMA table_info(EventLog)')
print('Columns:', [row[1] for row in cur.fetchall()])
cur.execute('SELECT COUNT(*) FROM EventLog')
print('Rows:', cur.fetchone()[0])
cur.execute('SELECT * FROM EventLog ORDER BY event_id DESC LIMIT 10')
for row in cur.fetchall():
    print(row)

print('\n=== Event counts by type ===')
cur.execute('SELECT event_type, COUNT(*) FROM EventLog GROUP BY event_type')
for row in cur.fetchall():
    print(row)

print('\n=== Candidate 101 events ===')
cur.execute("SELECT * FROM EventLog WHERE candidate_id = '101' ORDER BY event_id DESC LIMIT 20")
rows = cur.fetchall()
if rows:
    for row in rows:
        print(row)
else:
    print('(no rows for candidate 101)')

conn.close()
