import sqlite3
import hashlib
import os
from datetime import datetime
import shutil

from integrity_scorer import SCORE_MAX, get_event_deduction

DB_PATH = 'exam_monitor.db'

def get_filtered_events(candidate_id=None, event_type=None, date_str=None):
    """Fetch events with dynamic filters. Handles partial matching and date formatting."""
    with get_db_connection() as conn:
        base_query = """
            SELECT e.*, u.name, u.student_id 
            FROM events e 
            JOIN users u ON e.user_id = u.id 
            WHERE 1=1
        """
        params = []
        
        if candidate_id and candidate_id.strip():
            base_query += " AND u.student_id = ?"
            params.append(candidate_id.strip())
        
        if event_type and event_type.strip() and event_type != 'All':
            base_query += " AND e.type LIKE ?"
            params.append(f'%{event_type.strip()}%')
        
        if date_str and date_str.strip():
            try:
                parsed_date = datetime.strptime(date_str.strip(), "%m/%d/%Y").strftime("%Y-%m-%d")
                base_query += " AND DATE(e.timestamp) = ?"
                params.append(parsed_date)
            except ValueError:
                pass
        
        base_query += " ORDER BY e.timestamp DESC"
        rows = conn.execute(base_query, params).fetchall()
        return [dict(row) for row in rows]

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create tables and default admin if not exists."""
    with get_db_connection() as conn:
        # Users
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('student', 'admin')),
                student_id TEXT UNIQUE,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Events
        conn.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                deducted INTEGER DEFAULT 0,
                screenshot_path TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        # Stats – base table with all columns
        conn.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                user_id INTEGER PRIMARY KEY,
                face_absence_count INTEGER DEFAULT 0,
                focus_loss_count INTEGER DEFAULT 0,
                face_not_detected_count INTEGER DEFAULT 0,
                multiple_faces_count INTEGER DEFAULT 0,
                total_suspicious INTEGER DEFAULT 0,
                integrity_score INTEGER DEFAULT 1000,
                exam_running BOOLEAN DEFAULT 0,
                started_at TIMESTAMP,
                ended_at TIMESTAMP,
                session_count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        # Evidence
        conn.execute('''
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        # Application-wide administrator settings. Values are intentionally
        # stored separately from user and exam-report data.
        conn.execute('''
            CREATE TABLE IF NOT EXISTS app_settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT NOT NULL DEFAULT '',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # ---- ADD MISSING COLUMNS (for existing databases) ----
        cursor = conn.execute("PRAGMA table_info(stats)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        # List of (column_name, column_type) that should exist
        required_columns = {
            'exam_running': 'BOOLEAN DEFAULT 0',
            'started_at': 'TIMESTAMP',
            'ended_at': 'TIMESTAMP',
            'session_count': 'INTEGER DEFAULT 0',
            'face_not_detected_count': 'INTEGER DEFAULT 0',
            'multiple_faces_count': 'INTEGER DEFAULT 0',
        }
        for col, col_type in required_columns.items():
            if col not in existing_columns:
                conn.execute(f'ALTER TABLE stats ADD COLUMN {col} {col_type}')
        
        # Migrate legacy 0-100 integrity scores to the fixed 1000-point scale.
        # total_suspicious is the per-session count maintained by event updates.
        conn.execute('''
            UPDATE stats
            SET integrity_score = MAX(0, ? - (total_suspicious * ?))
            WHERE integrity_score <= 100
        ''', (SCORE_MAX, get_event_deduction('Face Not Detected')))

        # Create default admin
        admin = conn.execute("SELECT * FROM users WHERE email = 'admin@gmail.com'").fetchone()
        if not admin:
            password = 'admin@123'
            conn.execute(
                "INSERT INTO users (email, password, name, role) VALUES (?, ?, ?, ?)",
                ('admin@gmail.com', password, 'Administrator', 'admin')
            )
        conn.commit()
        print("Database initialized successfully.")


# ---------- User operations ----------
def create_user(email, password, name, role, student_id=None, session_id=None):
    
    with get_db_connection() as conn:
        if role == 'student':
            cursor = conn.execute(
                "INSERT INTO users (email, password, name, role, student_id, session_id) VALUES (?, ?, ?, ?, ?, ?)",
                (email, password, name, role, student_id, session_id)
            )
            user_id = cursor.lastrowid
            conn.execute(
                "INSERT INTO stats (user_id, integrity_score, exam_running, session_count) VALUES (?, ?, 0, 0)",
                (user_id, SCORE_MAX)
            )
            conn.commit()
            return user_id
        else:
            cursor = conn.execute(
                "INSERT INTO users (email, password, name, role) VALUES (?, ?, ?, ?)",
                (email, password, name, role)
            )
            conn.commit()
            return cursor.lastrowid

def get_user_by_email(email):
    with get_db_connection() as conn:
        return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

def get_user_by_id(user_id):
    with get_db_connection() as conn:
        return conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()


def get_app_setting(setting_key, default=''):
    """Return one application setting without exposing unrelated values."""
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT setting_value FROM app_settings WHERE setting_key = ?",
            (setting_key,)
        ).fetchone()
        return row['setting_value'] if row else default


def set_app_setting(setting_key, setting_value):
    """Create or update an application setting."""
    with get_db_connection() as conn:
        conn.execute('''
            INSERT INTO app_settings (setting_key, setting_value, updated_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(setting_key) DO UPDATE SET
                setting_value = excluded.setting_value,
                updated_at = CURRENT_TIMESTAMP
        ''', (setting_key, setting_value))
        conn.commit()

def get_students():
    with get_db_connection() as conn:
        return conn.execute("SELECT * FROM users WHERE role = 'student'").fetchall()

def get_user_stats(user_id):
    with get_db_connection() as conn:
        return conn.execute("SELECT * FROM stats WHERE user_id = ?", (user_id,)).fetchone()

def update_stats_after_event(user_id, deducted, event_type):
    """Apply the fixed 100-point deduction for each recognized violation."""
    score_deduction = get_event_deduction(event_type)
    is_violation = score_deduction > 0

    with get_db_connection() as conn:
        stats = conn.execute("SELECT * FROM stats WHERE user_id = ?", (user_id,)).fetchone()
        if stats:
            new_integrity = max(0, stats['integrity_score'] - score_deduction)
            new_total_susp = stats['total_suspicious'] + (1 if is_violation else 0)
            updates = {
                'integrity_score': new_integrity,
                'total_suspicious': new_total_susp,
            }
            counter_columns = {
                'Face Absence': 'face_absence_count',
                'Browser Focus Loss': 'focus_loss_count',
                'Face Not Detected': 'face_not_detected_count',
                'Multiple Faces': 'multiple_faces_count',
            }
            counter_column = counter_columns.get(event_type)
            if counter_column:
                updates[counter_column] = stats[counter_column] + 1

            assignments = ', '.join(f"{column} = ?" for column in updates)
            conn.execute(
                f"UPDATE stats SET {assignments} WHERE user_id = ?",
                (*updates.values(), user_id)
            )
        else:
            conn.execute(
                "INSERT INTO stats (user_id, integrity_score, total_suspicious, session_count) VALUES (?, ?, ?, 0)",
                (user_id, max(0, SCORE_MAX - score_deduction), 1 if is_violation else 0)
            )
        conn.commit()

def log_event(user_id, event_type, deducted, screenshot_path=None):
    """Store a server-authoritative deduction, ignoring client-provided weights."""
    score_deduction = get_event_deduction(event_type)
    with get_db_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO events (user_id, type, deducted, screenshot_path, timestamp) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
            (user_id, event_type, score_deduction, screenshot_path)
        )
        event_id = cursor.lastrowid
        conn.commit()
        return event_id

def get_events_by_user(user_id):
    with get_db_connection() as conn:
        return conn.execute("SELECT * FROM events WHERE user_id = ? ORDER BY timestamp DESC", (user_id,)).fetchall()

def get_all_events():
    with get_db_connection() as conn:
        return conn.execute("SELECT e.*, u.name, u.student_id FROM events e JOIN users u ON e.user_id = u.id ORDER BY e.timestamp DESC").fetchall()

def set_exam_running(user_id, running):
    with get_db_connection() as conn:
        if running:
            conn.execute('''
                UPDATE stats
                SET exam_running = 1,
                    started_at = CURRENT_TIMESTAMP,
                    ended_at = NULL,
                    integrity_score = ?,
                    face_absence_count = 0,
                    focus_loss_count = 0,
                    face_not_detected_count = 0,
                    multiple_faces_count = 0,
                    total_suspicious = 0
                WHERE user_id = ?
            ''', (SCORE_MAX, user_id))
            if conn.total_changes == 0:
                conn.execute('''
                    INSERT INTO stats (user_id, integrity_score, exam_running, started_at, session_count)
                    VALUES (?, ?, 1, CURRENT_TIMESTAMP, 0)
                ''', (user_id, SCORE_MAX))
        else:
            conn.execute('''
                UPDATE stats
                SET exam_running = 0,
                    ended_at = CURRENT_TIMESTAMP,
                    session_count = session_count + 1
                WHERE user_id = ?
            ''', (user_id,))
        conn.commit()

def save_evidence(user_id, file_path):
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO evidence (user_id, file_path) VALUES (?, ?)",
            (user_id, file_path)
        )
        conn.commit()

def get_evidence_by_user(user_id):
    with get_db_connection() as conn:
        return conn.execute("SELECT * FROM evidence WHERE user_id = ?", (user_id,)).fetchall()

def get_admin_dashboard_data():
    """Return all needed stats, analytics, and event list for admin dashboard, with risk labels."""
    from integrity_scorer import IntegrityScorer
    with get_db_connection() as conn:
        students = conn.execute("SELECT * FROM users WHERE role = 'student'").fetchall()
        stats_list = []
        event_list = []
        face_absences = 0
        focus_losses = 0
        integrity_values = []
        total_suspicious = 0
        active = 0
        completed = 0
        students_with_risk = []   # will store enriched student dicts

        for s in students:
            stats = conn.execute("SELECT * FROM stats WHERE user_id = ?", (s['id'],)).fetchone()
            if stats:
                stats_dict = dict(stats)
                stats_list.append(stats_dict)
                face_absences += stats['face_absence_count']
                focus_losses += stats['focus_loss_count']
                integrity_values.append(stats['integrity_score'])
                total_suspicious += stats['total_suspicious']
                if stats['exam_running'] == 1:
                    active += 1
                completed += stats['session_count']
            else:
                stats_dict = {'user_id': s['id'], 'exam_running': 0, 'integrity_score': 100,
                              'face_absence_count': 0, 'focus_loss_count': 0,
                              'total_suspicious': 0, 'session_count': 0,
                              'face_not_detected_count': 0}
                stats_list.append(stats_dict)
                integrity_values.append(100)

            # ---- Compute risk for this student ----
            events = conn.execute("SELECT * FROM events WHERE user_id = ?", (s['id'],)).fetchall()
            events_list = [dict(e) for e in events] if events else []
            scorer = IntegrityScorer(events_list, stats_dict)
            report = scorer.compute()

            # Build enriched student object
            student_data = dict(s)
            student_data['risk_label'] = report['risk_label']
            student_data['face_ratio'] = report['face_ratio']
            student_data['integrity_score'] = report['score']  # optionally use computed score
            students_with_risk.append(student_data)

            # Also collect events for the global list
            for ev in events:
                ev_dict = dict(ev)
                ev_dict['student_name'] = s['name']
                ev_dict['student_id'] = s['student_id']
                event_list.append(ev_dict)

        total = len(students)
        avg_integrity = round(sum(integrity_values)/len(integrity_values), 1) if integrity_values else 0

        return {
            'stats': {
                'total_candidates': total,
                'active_sessions': active,
                'completed_sessions': completed,
                'total_suspicious_events': total_suspicious,
                'average_integrity': avg_integrity,
            },
            'analytics': {
                'total_face_absence': face_absences,
                'total_focus_loss': focus_losses,
                'highest_integrity': max(integrity_values) if integrity_values else 0,
                'lowest_integrity': min(integrity_values) if integrity_values else 0,
                'average_integrity': avg_integrity,
            },
            'events': event_list,
            'students': students_with_risk,   # now includes risk_label & face_ratio
        }

def migrate_evidence_to_student_id():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, student_id FROM users WHERE role = 'student' AND student_id IS NOT NULL")
    users = cursor.fetchall()
    for user_id, student_id in users:
        old_folder = os.path.join('evidence', str(user_id))
        new_folder = os.path.join('evidence', str(student_id))
        if os.path.exists(old_folder):
            if os.path.exists(new_folder):
                for file in os.listdir(old_folder):
                    shutil.move(os.path.join(old_folder, file), os.path.join(new_folder, file))
                os.rmdir(old_folder)
            else:
                os.rename(old_folder, new_folder)
            cursor.execute(
                "UPDATE evidence SET file_path = REPLACE(file_path, ?, ?) WHERE user_id = ?",
                (f"{user_id}/", f"{student_id}/", user_id)
            )
            conn.commit()
            print(f"Migrated user {user_id} -> student_id {student_id}")
    conn.close()
    
def get_integrity_report(user_id):
    """Return enhanced integrity report using Pandas and IntegrityScorer."""
    from integrity_scorer import IntegrityScorer
    user = get_user_by_id(user_id)
    stats = get_user_stats(user_id)
    events = get_events_by_user(user_id)
    events_list = [dict(e) for e in events] if events else []
    stats_dict = dict(stats) if stats else {}

    scorer = IntegrityScorer(events_list, stats_dict)
    return {
        'user': dict(user) if user else None,
        'stats': stats_dict,
        'events': events_list,
        **scorer.compute()
    }