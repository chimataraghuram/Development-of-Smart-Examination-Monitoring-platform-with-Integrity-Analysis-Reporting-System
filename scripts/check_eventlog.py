from pathlib import Path
import sqlite3

base_dir = Path(__file__).resolve().parent.parent
db_path = base_dir / "database" / "exam.db"

print("DB:", db_path)
connection = sqlite3.connect(str(db_path))
cursor = connection.cursor()

# List tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tables:")
for t in cursor.fetchall():
    print(" -", t[0])

# Show EventLog schema
print('\nEventLog schema:')
try:
    cursor.execute("PRAGMA table_info('EventLog')")
    cols = cursor.fetchall()
    if cols:
        for c in cols:
            print(c)
    else:
        print('EventLog table not found')
except Exception as e:
    print('Error fetching EventLog schema:', e)

# Show recent EventLog rows
print('\nEventLog rows (up to 20):')
try:
    cursor.execute("SELECT * FROM EventLog ORDER BY rowid DESC LIMIT 20")
    rows = cursor.fetchall()
    if rows:
        for r in rows:
            print(r)
    else:
        print('No rows in EventLog or table does not exist')
except Exception as e:
    print('Error querying EventLog:', e)

connection.close()
