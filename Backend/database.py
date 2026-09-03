import hashlib
import os
import sqlite3
from datetime import datetime

import shutil
from werkzeug.security import generate_password_hash

try:
    from .integrity_scorer import SCORE_MAX, VIOLATION_DEDUCTION
except ImportError:
    from integrity_scorer import SCORE_MAX, VIOLATION_DEDUCTION

BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(BACKEND_DIR)
DB_PATH = os.path.join(BACKEND_DIR, 'exam_monitor.db')
DEFAULT_ADMIN_PASSWORD = os.getenv('ADMIN_DEFAULT_PASSWORD', 'admin@123')

VIOLATION_EVENT_TYPES = frozenset({
    'Face Not Detected', 'Face Absence', 'Multiple Faces',
    'Browser Focus Loss', 'Tab Switching', 'Copy Paste',
    'Suspicious Activity', 'Suspicious App', 'Screen Share', 'Audio Noise',
})
NON_VIOLATION_EVENT_TYPES = frozenset({
    'Face Detected', 'Browser Focus Regained', 'Verification Photo',
})

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
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute('PRAGMA foreign_keys = ON')
    return conn

def init_db():
    """Create tables, add missing columns, migrate existing data."""
    with get_db_connection() as conn:
        # --- Users ---
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('student', 'admin')),
                                student_id TEXT UNIQUE,
                session_id TEXT,
                profile_image TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

            )
        ''')
        user_columns = [row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()]
        if 'profile_image' not in user_columns:
            conn.execute('ALTER TABLE users ADD COLUMN profile_image TEXT')

        # --- Events ---

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
        # --- Stats ---
        conn.execute('''
            CREATE TABLE IF NOT EXISTS stats (
                user_id INTEGER PRIMARY KEY,
                face_absence_count INTEGER DEFAULT 0,
                focus_loss_count INTEGER DEFAULT 0,
                face_not_detected_count INTEGER DEFAULT 0,
                multiple_faces_count INTEGER DEFAULT 0,
                total_suspicious INTEGER DEFAULT 0,
                integrity_score INTEGER DEFAULT 100,
                exam_running BOOLEAN DEFAULT 0,
                started_at TIMESTAMP,
                ended_at TIMESTAMP,
                session_count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        # --- Evidence ---
        conn.execute('''
            CREATE TABLE IF NOT EXISTS evidence (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                file_path TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        # --- Sessions (NEW) ---
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                start_time TIMESTAMP,
                end_time TIMESTAMP,
                integrity_score INTEGER DEFAULT 100,
                exam_id INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS app_settings (
                setting_key TEXT PRIMARY KEY,
                setting_value TEXT NOT NULL DEFAULT '',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS examinations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                exam_date TEXT NOT NULL,
                duration_minutes INTEGER NOT NULL DEFAULT 60,
                break_minutes INTEGER NOT NULL DEFAULT 5,
                rules TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Draft' CHECK(status IN ('Draft', 'Published', 'Closed')),
                created_by INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (created_by) REFERENCES users(id) ON DELETE SET NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS exam_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                exam_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL DEFAULT 'Assigned',
                UNIQUE(exam_id, user_id),
                FOREIGN KEY (exam_id) REFERENCES examinations(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS review_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                admin_id INTEGER,
                decision TEXT NOT NULL,
                notes TEXT NOT NULL DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (admin_id) REFERENCES users(id) ON DELETE SET NULL
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                kind TEXT NOT NULL DEFAULT 'info',
                is_read BOOLEAN NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        ''')

        # ---------- Add missing columns to stats ----------

        cursor = conn.execute("PRAGMA table_info(stats)")
        existing_cols = [row[1] for row in cursor.fetchall()]
        required_cols = {
            'tab_switch_count': 'INTEGER DEFAULT 0',   # NEW
            'exam_running': 'BOOLEAN DEFAULT 0',
            'exam_paused': 'BOOLEAN DEFAULT 0',
            'started_at': 'TIMESTAMP',
            'ended_at': 'TIMESTAMP',
            'session_count': 'INTEGER DEFAULT 0',
            'face_not_detected_count': 'INTEGER DEFAULT 0',
            'multiple_faces_count': 'INTEGER DEFAULT 0',
            'exam_id': 'INTEGER',
            'review_state': "TEXT DEFAULT 'Not Reviewed'",

        }

        for col, col_type in required_cols.items():
            if col not in existing_cols:
                conn.execute(f'ALTER TABLE stats ADD COLUMN {col} {col_type}')

        session_cols = [row[1] for row in conn.execute("PRAGMA table_info(sessions)").fetchall()]
        if 'exam_id' not in session_cols:
            conn.execute('ALTER TABLE sessions ADD COLUMN exam_id INTEGER')

        # Convert scores produced by the previous 1000-point version to the new 100-point scale.
        conn.execute("UPDATE stats SET integrity_score = ROUND(integrity_score / 10.0, 1) WHERE integrity_score > 100")
        conn.execute("UPDATE sessions SET integrity_score = ROUND(integrity_score / 10.0, 1) WHERE integrity_score > 100")

        # ---------- Create/migrate default admin and credentials ----------

        admin = conn.execute("SELECT * FROM users WHERE email = 'admin@gmail.com'").fetchone()
        if not admin:
            conn.execute(
                "INSERT INTO users (email, password, name, role) VALUES (?, ?, ?, ?)",
                ('admin@gmail.com', generate_password_hash(DEFAULT_ADMIN_PASSWORD), 'Administrator', 'admin')
            )
        for row in conn.execute("SELECT id, password FROM users").fetchall():
            password = str(row['password'] or '')
            if not password.startswith(('scrypt:', 'pbkdf2:', 'argon2:')):
                conn.execute(
                    "UPDATE users SET password = ? WHERE id = ?",
                    (generate_password_hash(password), row['id'])
                )

        # ============================================================

        #  MIGRATE EXISTING DATA FROM stats INTO sessions
        # ============================================================
        # For every user with a completed exam (ended_at NOT NULL)
        conn.execute('''
            INSERT OR IGNORE INTO sessions (user_id, start_time, end_time, integrity_score)
            SELECT user_id, started_at, ended_at, integrity_score
            FROM stats
            WHERE started_at IS NOT NULL AND ended_at IS NOT NULL AND exam_running = 0
        ''')

        # ============================================================
        #  RECALCULATE AGGREGATE COUNTS FROM events
        # ============================================================
        # Update tab_switch_count
        conn.execute('''
            UPDATE stats
            SET tab_switch_count = (
                SELECT COUNT(*) FROM events
                WHERE events.user_id = stats.user_id AND events.type = 'Tab Switch'
            )
        ''')
        # Recalculate all event-based counts (ensures accuracy)
        conn.execute('''
            UPDATE stats
            SET
                face_absence_count = (SELECT COUNT(*) FROM events WHERE events.user_id = stats.user_id AND events.type = 'Face Absence'),
                focus_loss_count = (SELECT COUNT(*) FROM events WHERE events.user_id = stats.user_id AND events.type = 'Browser Focus Loss'),
                face_not_detected_count = (SELECT COUNT(*) FROM events WHERE events.user_id = stats.user_id AND events.type = 'Face Not Detected'),
                multiple_faces_count = (SELECT COUNT(*) FROM events WHERE events.user_id = stats.user_id AND events.type = 'Multiple Faces'),
                total_suspicious = (
                    SELECT COUNT(*) FROM events
                    WHERE events.user_id = stats.user_id
                      AND events.type IN ('Face Absence', 'Browser Focus Loss', 'Face Not Detected', 'Multiple Faces', 'Tab Switch')
                )
        ''')

        conn.commit()
       


# ---------- User operations ----------
def create_user(email, password, name, role, student_id=None, session_id=None):
    with get_db_connection() as conn:
        if role == 'student':
            cursor = conn.execute(
                "INSERT INTO users (email, password, name, role, student_id, session_id) VALUES (?, ?, ?, ?, ?, ?)",
                (email, generate_password_hash(password), name, role, student_id, session_id)
            )
            user_id = cursor.lastrowid
            conn.execute(
                "INSERT INTO stats (user_id, integrity_score, exam_running, session_count, tab_switch_count) VALUES (?, 100, 0, 0, 0)",
                (user_id,)
            )
            conn.commit()
            return user_id
        else:
            cursor = conn.execute(
                "INSERT INTO users (email, password, name, role) VALUES (?, ?, ?, ?)",
                (email, generate_password_hash(password), name, role)
            )
            conn.commit()
            return cursor.lastrowid

def get_user_by_email(email):
    with get_db_connection() as conn:
        return conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()

def update_user_profile(user_id, name, email, student_id):
    with get_db_connection() as conn:
        conn.execute(
            "UPDATE users SET name = ?, email = ?, student_id = ? WHERE id = ?",
            (name, email, student_id, user_id),
        )
        conn.commit()
    return get_user_by_id(user_id)

def update_user_profile_image(user_id, filename):
    with get_db_connection() as conn:
        conn.execute("UPDATE users SET profile_image = ? WHERE id = ?", (filename, user_id))
        conn.commit()
    return get_user_by_id(user_id)

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
    """Update counters using the server-owned fixed deduction policy.

    The client may send a legacy ``deducted`` value, but it is deliberately
    ignored. Only recognized violation types can change the integrity score.
    """
    deduction_points = VIOLATION_DEDUCTION if event_type in VIOLATION_EVENT_TYPES else 0
    with get_db_connection() as conn:
        stats = conn.execute("SELECT * FROM stats WHERE user_id = ?", (user_id,)).fetchone()
        if not stats:
            conn.execute(
                "INSERT INTO stats (user_id, integrity_score, total_suspicious, session_count, tab_switch_count) VALUES (?, ?, ?, 0, 0)",
                (user_id, max(0, SCORE_MAX - deduction_points), 1 if deduction_points else 0)
            )
            stats = conn.execute("SELECT * FROM stats WHERE user_id = ?", (user_id,)).fetchone()

        new_integrity = max(0, float(stats['integrity_score'] if stats['integrity_score'] is not None else SCORE_MAX) - deduction_points)
        new_total_susp = int(stats['total_suspicious'] or 0) + (1 if deduction_points else 0)
        counter_column = {
            'Face Absence': 'face_absence_count',
            'Browser Focus Loss': 'focus_loss_count',
            'Face Not Detected': 'face_not_detected_count',
            'Multiple Faces': 'multiple_faces_count',
            'Tab Switch': 'tab_switch_count',
            'Tab Switching': 'tab_switch_count',
        }.get(event_type)

        assignments = ['integrity_score = ?', 'total_suspicious = ?']
        params = [new_integrity, new_total_susp]
        if counter_column:
            assignments.append(f'{counter_column} = COALESCE({counter_column}, 0) + 1')
        params.append(user_id)
        conn.execute(f"UPDATE stats SET {', '.join(assignments)} WHERE user_id = ?", params)
        conn.commit()


def log_event(user_id, event_type, deducted, screenshot_path=None):
    """Persist an event with a server-calculated deduction."""
    stored_deducted = VIOLATION_DEDUCTION if event_type in VIOLATION_EVENT_TYPES else 0
    with get_db_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO events (user_id, type, deducted, screenshot_path, timestamp) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)",
            (user_id, event_type, stored_deducted, screenshot_path)
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

def set_exam_running(user_id, running, exam_id=None):
    with get_db_connection() as conn:
        if running:
            conn.execute('''
                UPDATE stats
                SET exam_running = 1,
                    exam_paused = 0,
                    started_at = CURRENT_TIMESTAMP,
                    ended_at = NULL,
                    exam_id = ?,
                    integrity_score = 100,
                    face_absence_count = 0,
                    focus_loss_count = 0,
                    face_not_detected_count = 0,
                    multiple_faces_count = 0,
                    tab_switch_count = 0,
                    total_suspicious = 0,
                    review_state = 'Not Reviewed'
                WHERE user_id = ?
            ''', (exam_id, user_id))
            if conn.total_changes == 0:
                conn.execute('''
                    INSERT INTO stats (user_id, integrity_score, exam_running, exam_paused, exam_id, started_at, session_count, tab_switch_count)
                    VALUES (?, 100, 1, 0, ?, CURRENT_TIMESTAMP, 0, 0)
                ''', (user_id, exam_id))
        else:
            stats = conn.execute("SELECT * FROM stats WHERE user_id = ?", (user_id,)).fetchone()
            if stats and stats['exam_running']:
                ended_at = datetime.now().isoformat()
                conn.execute(
                    "INSERT INTO sessions (user_id, start_time, end_time, integrity_score, exam_id) VALUES (?, ?, ?, ?, ?)",
                    (user_id, stats['started_at'], ended_at, stats['integrity_score'], stats['exam_id'])
                )
                conn.execute('''
                    UPDATE stats
                    SET exam_running = 0,
                        exam_paused = 0,
                        ended_at = CURRENT_TIMESTAMP,
                        session_count = session_count + 1
                    WHERE user_id = ?
                ''', (user_id,))
        conn.commit()
    return get_user_stats(user_id)


def set_exam_paused(user_id, paused):
    """Toggle the paused flag while preserving the exam-running state."""
    with get_db_connection() as conn:
        if paused:
            conn.execute(
                "UPDATE stats SET exam_paused = 1 WHERE user_id = ? AND exam_running = 1",
                (user_id,)
            )
        else:
            conn.execute(
                "UPDATE stats SET exam_paused = 0 WHERE user_id = ? AND exam_running = 1",
                (user_id,)
            )
        row = conn.execute(
            "SELECT exam_running, exam_paused FROM stats WHERE user_id = ?",
            (user_id,)
        ).fetchone()
        conn.commit()
        if not row:
            return {'exam_running': False, 'exam_paused': False}
        return {'exam_running': bool(row['exam_running']), 'exam_paused': bool(row['exam_paused'])}

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
    try:
        from .integrity_scorer import IntegrityScorer
    except ImportError:
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
                stats_dict = {'user_id': s['id'], 'exam_running': 0, 'integrity_score': SCORE_MAX,

                              'face_absence_count': 0, 'focus_loss_count': 0,
                              'total_suspicious': 0, 'session_count': 0,'started_at': None,
                               'ended_at': None,
                              'face_not_detected_count': 0}
                stats_list.append(stats_dict)
                integrity_values.append(SCORE_MAX)

            # ---- Compute risk for this student ----
            events = conn.execute("SELECT * FROM events WHERE user_id = ?", (s['id'],)).fetchall()
            events_list = [dict(e) for e in events] if events else []
            scorer = IntegrityScorer(events_list, stats_dict)
            report = scorer.compute()

            # Build enriched student object
            student_data = dict(s)
            student_data['risk_label'] = report['risk_label']
            student_data['face_ratio'] = report['face_ratio']
            student_data['integrity_score'] = report['score']
            student_data['exam_running'] = bool(stats_dict.get('exam_running', 0))
            student_data['total_suspicious'] = stats_dict.get('total_suspicious', 0)
            student_data['started_at'] = stats_dict.get('started_at')
            student_data['ended_at'] = stats_dict.get('ended_at')
            student_data['face_absence_count'] = stats_dict.get('face_absence_count', 0)
            student_data['focus_loss_count'] = stats_dict.get('focus_loss_count', 0)
            student_data['session_count'] = stats_dict.get('session_count', 0)
            student_data['exam_id'] = stats_dict.get('exam_id')
            student_data['review_state'] = stats_dict.get('review_state', 'Not Reviewed')
            student_data['event_count'] = sum(1 for event in events_list if int(event.get('deducted', 0) or 0) > 0)

            student_data['session_status'] = 'Completed' if not student_data['exam_running'] and student_data['session_count'] > 0 else ('Active' if student_data['exam_running'] else 'Not Started')
            student_data['duration_seconds'] = 0
            if student_data['started_at'] and student_data['ended_at']:
                try:
                    started = datetime.fromisoformat(str(student_data['started_at']).replace('Z', '+00:00'))
                    ended = datetime.fromisoformat(str(student_data['ended_at']).replace('Z', '+00:00'))
                    student_data['duration_seconds'] = max(0, int((ended - started).total_seconds()))
                except ValueError:
                    student_data['duration_seconds'] = 0
            students_with_risk.append(student_data)

            # Also collect events for the global list
            for ev in events:
                ev_dict = dict(ev)
                ev_dict['student_name'] = s['name']
                ev_dict['student_id'] = s['student_id']
                event_list.append(ev_dict)

        total = len(students)
        avg_integrity = round(sum(integrity_values)/len(integrity_values), 1) if integrity_values else 0

        recent_events = []
        for ev in sorted(event_list, key=lambda item: item.get('timestamp') or '', reverse=True)[:30]:
            recent_events.append({
                'id': ev.get('id'),
                'user_id': ev.get('user_id'),
                'type': ev.get('type'),
                'timestamp': ev.get('timestamp'),
                'deducted': ev.get('deducted', 0),
                'student_name': ev.get('student_name'),
                'student_id': ev.get('student_id'),
            })

        high_risk_candidates = []
        for student in sorted(students_with_risk, key=lambda item: (item.get('integrity_score', SCORE_MAX), item.get('total_suspicious', 0)))[:10]:
            if student.get('integrity_score', SCORE_MAX) <= 49:
                high_risk_candidates.append({
                    'id': student.get('id'),
                    'name': student.get('name'),
                    'student_id': student.get('student_id'),
                    'integrity_score': student.get('integrity_score', SCORE_MAX),
                    'risk_label': student.get('risk_label', 'Low Risk'),
                    'total_suspicious': student.get('total_suspicious', 0),
                })

        session_summary = {
            'total_candidates': total,
            'active_sessions': active,
            'completed_sessions': completed,
            'average_integrity': avg_integrity,
            'total_suspicious_events': total_suspicious,
            'recent_event_count': len(recent_events),
        }

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
            'students': students_with_risk,
            'recent_events': recent_events,
            'high_risk_candidates': high_risk_candidates,
            'session_summary': session_summary,
            'examinations': get_exams(),
        }

def get_integrity_report(user_id):
    """Return enhanced integrity report."""
    user = get_user_by_id(user_id)
    stats = get_user_stats(user_id)
    events = get_events_by_user(user_id)
    events_list = [dict(e) for e in events] if events else []
    stats_dict = dict(stats) if stats else {}

    try:
        from .integrity_scorer import IntegrityScorer
    except ImportError:
        from integrity_scorer import IntegrityScorer
    scorer = IntegrityScorer(events_list, stats_dict)
    report = scorer.compute()
    return {
        'user': dict(user) if user else None,
        'stats': stats_dict,
        'events': events_list,
        'exams': get_student_exams(user_id),
        'reviews': get_reviews(user_id),
        **report
    }

def get_verification_photo(user_id):
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT file_path FROM evidence WHERE user_id = ? AND file_path LIKE '%/verification/%' ORDER BY uploaded_at DESC LIMIT 1",
            (user_id,)
        ).fetchone()
        return row['file_path'] if row else None

def get_all_verification_photos(user_id):
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT file_path FROM evidence WHERE user_id = ? AND file_path LIKE '%/verification/%' ORDER BY uploaded_at DESC",
            (user_id,)
        ).fetchall()
        return [row['file_path'] for row in rows if row and row['file_path']]


def create_exam(title, exam_date, duration_minutes=60, break_minutes=5, rules='', created_by=None):
    with get_db_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO examinations (title, exam_date, duration_minutes, break_minutes, rules, status, created_by) VALUES (?, ?, ?, ?, ?, 'Draft', ?)",
            (title.strip(), exam_date, int(duration_minutes), int(break_minutes), (rules or '').strip(), created_by),
        )
        conn.commit()
        return get_exam(cursor.lastrowid)


def get_exam(exam_id):
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM examinations WHERE id = ?", (exam_id,)).fetchone()
        return dict(row) if row else None


def get_exams():
    with get_db_connection() as conn:
        rows = conn.execute("SELECT * FROM examinations ORDER BY exam_date DESC, id DESC").fetchall()
        return [dict(row) for row in rows]


def update_exam_status(exam_id, status):
    if status not in {'Draft', 'Published', 'Closed'}:
        raise ValueError('Invalid examination status')
    with get_db_connection() as conn:
        conn.execute("UPDATE examinations SET status = ? WHERE id = ?", (status, exam_id))
        conn.commit()
    return get_exam(exam_id)


def assign_students_to_exam(exam_id, user_ids):
    assigned = []
    with get_db_connection() as conn:
        for user_id in user_ids:
            try:
                conn.execute(
                    "INSERT OR IGNORE INTO exam_assignments (exam_id, user_id) VALUES (?, ?)",
                    (int(exam_id), int(user_id)),
                )
                assigned.append(int(user_id))
            except (TypeError, ValueError):
                continue
        conn.commit()
    return assigned


def get_exam_candidates(exam_id):
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT u.id, u.name, u.email, u.student_id, u.session_id, ea.status, ea.assigned_at "
            "FROM exam_assignments ea JOIN users u ON u.id = ea.user_id "
            "WHERE ea.exam_id = ? ORDER BY u.name",
            (exam_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_student_exams(user_id):
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT e.*, ea.status AS assignment_status FROM exam_assignments ea "
            "JOIN examinations e ON e.id = ea.exam_id WHERE ea.user_id = ? "
            "ORDER BY e.exam_date DESC, e.id DESC",
            (user_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def get_current_exam_for_student(user_id):
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT e.*, ea.status AS assignment_status FROM exam_assignments ea "
            "JOIN examinations e ON e.id = ea.exam_id "
            "WHERE ea.user_id = ? AND e.status = 'Published' "
            "ORDER BY e.exam_date DESC, e.id DESC LIMIT 1",
            (user_id,),
        ).fetchone()
        return dict(row) if row else None


def save_review(user_id, admin_id, decision, notes=''):
    allowed = {'Cleared', 'Under Review', 'Confirmed Violation', 'Appeal Pending'}
    if decision not in allowed:
        raise ValueError('Invalid review decision')
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO review_records (user_id, admin_id, decision, notes) VALUES (?, ?, ?, ?)",
            (user_id, admin_id, decision, (notes or '').strip()),
        )
        conn.execute("UPDATE stats SET review_state = ? WHERE user_id = ?", (decision, user_id))
        conn.commit()
    return get_reviews(user_id)


def get_reviews(user_id):
    with get_db_connection() as conn:
        rows = conn.execute(
            "SELECT r.*, a.name AS admin_name FROM review_records r "
            "LEFT JOIN users a ON a.id = r.admin_id WHERE r.user_id = ? ORDER BY r.created_at DESC, r.id DESC",
            (user_id,),
        ).fetchall()
        return [dict(row) for row in rows]


def create_notification(user_id, title, message, kind='info'):
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO notifications (user_id, title, message, kind) VALUES (?, ?, ?, ?)",
            (user_id, title.strip(), message.strip(), kind),
        )
        conn.commit()


def get_notifications(user_id, unread_only=False):
    query = "SELECT * FROM notifications WHERE user_id = ?"
    params = [user_id]
    if unread_only:
        query += " AND is_read = 0"
    query += " ORDER BY created_at DESC, id DESC LIMIT 50"
    with get_db_connection() as conn:
        rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]


def mark_notifications_read(user_id):
    with get_db_connection() as conn:
        conn.execute("UPDATE notifications SET is_read = 1 WHERE user_id = ?", (user_id,))
        conn.commit()
