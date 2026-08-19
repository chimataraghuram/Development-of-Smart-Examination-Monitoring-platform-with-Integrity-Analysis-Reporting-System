import sqlite3
import hashlib
import os
from datetime import datetime
import shutil

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
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
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
        }
        for col, col_type in required_cols.items():
            if col not in existing_cols:
                conn.execute(f'ALTER TABLE stats ADD COLUMN {col} {col_type}')

        # ---------- Create default admin ----------
        admin = conn.execute("SELECT * FROM users WHERE email = 'admin@gmail.com'").fetchone()
        if not admin:
            conn.execute(
                "INSERT INTO users (email, password, name, role) VALUES (?, ?, ?, ?)",
                ('admin@gmail.com', 'admin@123', 'Administrator', 'admin')
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
                (email, password, name, role, student_id, session_id)
            )
            user_id = cursor.lastrowid
            conn.execute(
                "INSERT INTO stats (user_id, integrity_score, exam_running, session_count, tab_switch_count) VALUES (?, 1000, 0, 0, 0)",
                (user_id,)
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
    with get_db_connection() as conn:
        stats = conn.execute("SELECT * FROM stats WHERE user_id = ?", (user_id,)).fetchone()
        if stats:
            raw_deducted = float(deducted) if deducted is not None else 0.0
            deduction_points = (raw_deducted * 100) if raw_deducted > 0 else 0
            new_integrity = max(0, stats['integrity_score'] - deduction_points)
            new_total_susp = stats['total_suspicious'] + (1 if raw_deducted > 0 else 0)

            if event_type == 'Face Absence':
                conn.execute(
                    "UPDATE stats SET integrity_score = ?, total_suspicious = ?, face_absence_count = face_absence_count + 1 WHERE user_id = ?",
                    (new_integrity, new_total_susp, user_id)
                )
            elif event_type == 'Browser Focus Loss':
                conn.execute(
                    "UPDATE stats SET integrity_score = ?, total_suspicious = ?, focus_loss_count = focus_loss_count + 1 WHERE user_id = ?",
                    (new_integrity, new_total_susp, user_id)
                )
            elif event_type == 'Face Not Detected':
                conn.execute(
                    "UPDATE stats SET integrity_score = ?, total_suspicious = ?, face_not_detected_count = face_not_detected_count + 1 WHERE user_id = ?",
                    (new_integrity, new_total_susp, user_id)
                )
            elif event_type == 'Multiple Faces':
                conn.execute(
                    "UPDATE stats SET integrity_score = ?, total_suspicious = ?, multiple_faces_count = multiple_faces_count + 1 WHERE user_id = ?",
                    (new_integrity, new_total_susp, user_id)
                )
            elif event_type in ('Tab Switch', 'Tab Switching') or (event_type and event_type.lower() in ('tab_switch', 'tab switching')):
                conn.execute(
                    "UPDATE stats SET integrity_score = ?, total_suspicious = ?, tab_switch_count = tab_switch_count + 1 WHERE user_id = ?",
                    (new_integrity, new_total_susp, user_id)
                )
            else:
                conn.execute(
                    "UPDATE stats SET integrity_score = ?, total_suspicious = ? WHERE user_id = ?",
                    (new_integrity, new_total_susp, user_id)
                )
        else:
            # Create stats row with all counters at 0
            raw_deducted = float(deducted) if deducted is not None else 0.0
            initial_score = max(0, 1000 - (raw_deducted * 100 if raw_deducted > 0 else 0))
            conn.execute(
                "INSERT INTO stats (user_id, integrity_score, total_suspicious, session_count, tab_switch_count) VALUES (?, ?, ?, 0, 0)",
                (user_id, initial_score, 1 if raw_deducted > 0 else 0)
            )
        conn.commit()


def log_event(user_id, event_type, deducted, screenshot_path=None):
    with get_db_connection() as conn:
        raw_deducted = float(deducted) if deducted is not None else 0.0
        stored_deducted = int(raw_deducted * 100) if raw_deducted > 0 else 0
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

def set_exam_running(user_id, running):
    with get_db_connection() as conn:
        if running:
            # Start exam: reset stats
            conn.execute('''
                UPDATE stats
                SET exam_running = 1,
                    exam_paused = 0,
                    started_at = CURRENT_TIMESTAMP,
                    ended_at = NULL,
                    integrity_score = 1000,
                    face_absence_count = 0,
                    focus_loss_count = 0,
                    face_not_detected_count = 0,
                    multiple_faces_count = 0,
                    tab_switch_count = 0,
                    total_suspicious = 0
                WHERE user_id = ?
            ''', (user_id,))
            if conn.total_changes == 0:
                conn.execute('''
                    INSERT INTO stats (user_id, integrity_score, exam_running, exam_paused, started_at, session_count, tab_switch_count)
                    VALUES (?, 1000, 1, 0, CURRENT_TIMESTAMP, 0, 0)
                ''', (user_id,))
        else:
            # End exam: log session and update stats
            stats = conn.execute("SELECT * FROM stats WHERE user_id = ?", (user_id,)).fetchone()
            if stats:
                conn.execute(
                    "INSERT INTO sessions (user_id, start_time, end_time, integrity_score) VALUES (?, ?, ?, ?)",
                    (user_id, stats['started_at'], datetime.now().isoformat(), stats['integrity_score'])
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
                              'total_suspicious': 0, 'session_count': 0,'started_at': None,
                               'ended_at': None,
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
            student_data['integrity_score'] = report['score']
            student_data['exam_running'] = bool(stats_dict.get('exam_running', 0))
            student_data['total_suspicious'] = stats_dict.get('total_suspicious', 0)
            student_data['started_at'] = stats_dict.get('started_at')
            student_data['ended_at'] = stats_dict.get('ended_at')
            student_data['face_absence_count'] = stats_dict.get('face_absence_count', 0)
            student_data['focus_loss_count'] = stats_dict.get('focus_loss_count', 0)
            student_data['session_count'] = stats_dict.get('session_count', 0)
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
        for student in sorted(students_with_risk, key=lambda item: (item.get('integrity_score', 1000), item.get('total_suspicious', 0)))[:10]:
            if student.get('integrity_score', 1000) <= 600:
                high_risk_candidates.append({
                    'id': student.get('id'),
                    'name': student.get('name'),
                    'student_id': student.get('student_id'),
                    'integrity_score': student.get('integrity_score', 1000),
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
        }

def get_integrity_report(user_id):
    """Return enhanced integrity report."""
    user = get_user_by_id(user_id)
    stats = get_user_stats(user_id)
    events = get_events_by_user(user_id)
    events_list = [dict(e) for e in events] if events else []
    stats_dict = dict(stats) if stats else {}

    from integrity_scorer import IntegrityScorer
    scorer = IntegrityScorer(events_list, stats_dict)
    report = scorer.compute()
    return {
        'user': dict(user) if user else None,
        'stats': stats_dict,
        'events': events_list,
        **report
    }

def get_verification_photo(user_id):
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT file_path FROM evidence WHERE user_id = ? AND file_path LIKE '%/verification/%' ORDER BY uploaded_at DESC LIMIT 1",
            (user_id,)
        ).fetchone()
        return row['file_path'] if row else None
