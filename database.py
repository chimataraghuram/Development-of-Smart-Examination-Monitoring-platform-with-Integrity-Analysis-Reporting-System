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
            raw_date = date_str.strip()
            parsed_date = None
            for date_format in ("%Y-%m-%d", "%m/%d/%Y"):
                try:
                    parsed_date = datetime.strptime(raw_date, date_format).strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue
            if parsed_date:
                base_query += " AND DATE(e.timestamp) = ?"
                params.append(parsed_date)
        
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
                exam_paused BOOLEAN DEFAULT 0,
                started_at TIMESTAMP,
                paused_at TIMESTAMP,
                total_paused_seconds INTEGER DEFAULT 0,
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
            'exam_paused': 'BOOLEAN DEFAULT 0',
            'started_at': 'TIMESTAMP',
            'paused_at': 'TIMESTAMP',
            'total_paused_seconds': 'INTEGER DEFAULT 0',
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
                    exam_paused = 0,
                    paused_at = NULL,
                    total_paused_seconds = 0,
                    face_absence_count = 0,
                    focus_loss_count = 0,
                    face_not_detected_count = 0,
                    multiple_faces_count = 0,
                    total_suspicious = 0
                WHERE user_id = ?
            ''', (SCORE_MAX, user_id))
            if conn.total_changes == 0:
                conn.execute('''
                    INSERT INTO stats (user_id, integrity_score, exam_running, exam_paused, started_at, total_paused_seconds, session_count)
                    VALUES (?, ?, 1, 0, CURRENT_TIMESTAMP, 0, 0)
                ''', (user_id, SCORE_MAX))
        else:
            conn.execute('''
                UPDATE stats
                SET exam_running = 0,
                    exam_paused = 0,
                    total_paused_seconds = total_paused_seconds + CASE
                        WHEN exam_paused = 1 AND paused_at IS NOT NULL
                        THEN MAX(0, strftime('%s', 'now') - strftime('%s', paused_at))
                        ELSE 0
                    END,
                    paused_at = NULL,
                    ended_at = CURRENT_TIMESTAMP,
                    session_count = session_count + 1
                WHERE user_id = ?
            ''', (user_id,))
        conn.commit()


def set_exam_paused(user_id, paused):
    """Persist a pause or resume action for an active examination session."""
    with get_db_connection() as conn:
        if paused:
            conn.execute('''
                UPDATE stats
                SET exam_paused = 1,
                    paused_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND exam_running = 1
            ''', (user_id,))
        else:
            conn.execute('''
                UPDATE stats
                SET exam_paused = 0,
                    total_paused_seconds = total_paused_seconds + CASE
                        WHEN paused_at IS NOT NULL
                        THEN MAX(0, strftime('%s', 'now') - strftime('%s', paused_at))
                        ELSE 0
                    END,
                    paused_at = NULL
                WHERE user_id = ? AND exam_running = 1
            ''', (user_id,))
        conn.commit()
        row = conn.execute(
            'SELECT exam_running, exam_paused FROM stats WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        return dict(row) if row else None


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
    """Return role-authorized, live monitoring data for the administrator panel."""
    from integrity_scorer import IntegrityScorer

    def elapsed_seconds(stats_dict):
        started_at = stats_dict.get('started_at')
        if not started_at:
            return 0
        try:
            started = datetime.fromisoformat(str(started_at))
            if stats_dict.get('exam_running'):
                ended = datetime.fromisoformat(str(stats_dict['paused_at'])) if stats_dict.get('exam_paused') and stats_dict.get('paused_at') else datetime.now()
            else:
                if not stats_dict.get('ended_at'):
                    return 0
                ended = datetime.fromisoformat(str(stats_dict['ended_at']))
            return max(0, int((ended - started).total_seconds()) - int(stats_dict.get('total_paused_seconds') or 0))
        except (TypeError, ValueError):
            return 0

    with get_db_connection() as conn:
        students = conn.execute("SELECT * FROM users WHERE role = 'student'").fetchall()
        event_list = []
        face_absences = 0
        focus_losses = 0
        integrity_values = []
        total_suspicious = 0
        active = 0
        paused = 0
        completed = 0
        completed_candidates = 0
        ready = 0
        students_with_risk = []

        for student in students:
            stats_row = conn.execute("SELECT * FROM stats WHERE user_id = ?", (student['id'],)).fetchone()
            stats_dict = dict(stats_row) if stats_row else {
                'user_id': student['id'], 'exam_running': 0, 'exam_paused': 0,
                'integrity_score': SCORE_MAX, 'face_absence_count': 0,
                'focus_loss_count': 0, 'total_suspicious': 0,
                'session_count': 0, 'face_not_detected_count': 0,
                'multiple_faces_count': 0, 'total_paused_seconds': 0,
            }
            events = conn.execute(
                "SELECT * FROM events WHERE user_id = ? ORDER BY timestamp DESC",
                (student['id'],)
            ).fetchall()
            events_list = [dict(event) for event in events]
            report = IntegrityScorer(events_list, stats_dict).compute()

            is_running = bool(stats_dict.get('exam_running'))
            is_paused = bool(stats_dict.get('exam_paused')) and is_running
            if is_paused:
                session_status = 'Paused'
                paused += 1
            elif is_running:
                session_status = 'Active'
                active += 1
            elif int(stats_dict.get('session_count') or 0) > 0:
                session_status = 'Completed'
                completed += int(stats_dict.get('session_count') or 0)
                completed_candidates += 1
            else:
                session_status = 'Ready'
                ready += 1

            face_absences += int(stats_dict.get('face_absence_count') or 0)
            focus_losses += int(stats_dict.get('focus_loss_count') or 0)
            total_suspicious += int(stats_dict.get('total_suspicious') or 0)
            integrity_values.append(report['score'])

            student_data = dict(student)
            student_data.update({
                'risk_label': report['risk_label'],
                'face_ratio': report['face_ratio'],
                'integrity_score': report['score'],
                'event_count': int(stats_dict.get('total_suspicious') or 0),
                'session_status': session_status,
                'duration_seconds': elapsed_seconds(stats_dict),
                'latest_event': events_list[0] if events_list else None,
            })
            students_with_risk.append(student_data)

            for event in events_list:
                event['student_name'] = student['name']
                event['student_id'] = student['student_id']
                event['risk_label'] = report['risk_label']
                event_list.append(event)

        event_list.sort(key=lambda event: event.get('timestamp') or '', reverse=True)
        students_with_risk.sort(key=lambda student: (student['integrity_score'], student['name'].lower()))
        total = len(students_with_risk)
        average_integrity = round(sum(integrity_values) / total, 1) if total else 0
        risk_counts = {
            'low': sum(student['risk_label'] == 'Low Risk' for student in students_with_risk),
            'medium': sum(student['risk_label'] == 'Medium Risk' for student in students_with_risk),
            'high': sum(student['risk_label'] == 'High Risk' for student in students_with_risk),
        }
        high_risk = [student for student in students_with_risk if student['risk_label'] == 'High Risk'][:5]

        return {
            'stats': {
                'total_candidates': total,
                'active_sessions': active,
                'paused_sessions': paused,
                'ready_candidates': ready,
                'completed_sessions': completed,
                'total_suspicious_events': total_suspicious,
                'average_integrity': average_integrity,
            },
            'analytics': {
                'total_face_absence': face_absences,
                'total_focus_loss': focus_losses,
                'highest_integrity': max(integrity_values) if integrity_values else 0,
                'lowest_integrity': min(integrity_values) if integrity_values else 0,
                'average_integrity': average_integrity,
                'risk_counts': risk_counts,
            },
            'session_summary': {
                'active': active,
                'paused': paused,
                'completed': completed,
                'completed_candidates': completed_candidates,
                'ready': ready,
            },
            'recent_events': event_list[:10],
            'high_risk_candidates': high_risk,
            'events': event_list,
            'students': students_with_risk,
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