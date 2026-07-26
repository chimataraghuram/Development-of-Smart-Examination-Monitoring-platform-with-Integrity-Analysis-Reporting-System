import sqlite3

# Connect to SQLite database (creates exam.db if it doesn't exist)
connection = sqlite3.connect("database/exam.db")

# Create a cursor object to execute SQL commands
cursor = connection.cursor()

# Create Candidate table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Candidate (
    candidate_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    photo_path TEXT
)
""")

# Create Session table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Session (
    session_id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id TEXT,
    start_time TEXT,
    end_time TEXT,
    status TEXT
)
""")

# Create EventLog table
cursor.execute("""
CREATE TABLE IF NOT EXISTS EventLog(
    event_id INTEGER PRIMARY KEY AUTOINCREMENT,
    candidate_id TEXT,
    event_type TEXT,
    timestamp TEXT,
    remarks TEXT
)
""")

# Save changes
connection.commit()

# Close database connection
connection.close()

print("Database and tables created successfully!")