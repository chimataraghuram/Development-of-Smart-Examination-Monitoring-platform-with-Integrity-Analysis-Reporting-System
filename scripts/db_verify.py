import sqlite3
import os

path = os.path.join(os.path.dirname(__file__), '..', 'database', 'exam.db')
path = os.path.normpath(path)
print('DB path:', path)
conn = sqlite3.connect(path)
cur = conn.cursor()

for name in ['Candidate', 'Session', 'EventLog']:
    print(f'\n=== {name} ===')
    try:
        cur.execute(f'SELECT * FROM {name}')
        rows = cur.fetchall()
        if rows:
            for row in rows:
                print(row)
        else:
            print('(no rows)')
    except Exception as e:
        print('ERROR:', e)

print('\n=== Event counts ===')
try:
    cur.execute('SELECT event_type, COUNT(*) FROM EventLog GROUP BY event_type')
    rows = cur.fetchall()
    if rows:
        for row in rows:
            print(row)
    else:
        print('(no rows)')
except Exception as e:
    print('ERROR counts:', e)

print('\n=== Candidate 101 events ===')
try:
    cur.execute("SELECT * FROM EventLog WHERE candidate_id = '101'")
    rows = cur.fetchall()
    if rows:
        for row in rows:
            print(row)
    else:
        print('(no rows for candidate 101)')
except Exception as e:
    print('ERROR candidate 101:', e)

conn.close()
