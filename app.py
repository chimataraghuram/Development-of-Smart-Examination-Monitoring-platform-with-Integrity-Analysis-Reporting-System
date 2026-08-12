import os
import base64
import hashlib
import sqlite3
import logging
from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for, render_template
from flask_cors import CORS
from functools import wraps
from datetime import datetime
import cv2
import numpy as np
import database as db
from ai_service import AIServiceError, answer_question

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = 'exam'   # Keep this consistent
CORS(app, supports_credentials=True)

app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'evidence')
# Session configuration – critical for local development
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False,   # False for HTTP (localhost)
    SESSION_COOKIE_PATH='/',
    PERMANENT_SESSION_LIFETIME=3600,  # 1 hour
)

# Configuration
UPLOAD_FOLDER = 'evidence'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize database
db.init_db()

# ---------- Helper functions ----------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            logger.warning("Session missing for %s", request.path)
            # API callers must receive JSON, not an HTML redirect that fetch()
            # follows and then fails to parse as JSON.
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login_page'))
        logger.debug(f"Session valid: user_id={session['user_id']}")
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required'}), 401
            return redirect(url_for('login_page'))
        user = db.get_user_by_id(session['user_id'])
        if not user or user['role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

# ---------- Serve HTML pages using render_template ----------
@app.route('/')
def index():
    return redirect(url_for('login_page'))

@app.route('/register')
@app.route('/register.html')
def register_page():
    return render_template('register.html')

@app.route('/login')
@app.route('/login.html')
def login_page():
    return render_template('login.html')

@app.route('/dashboard')
@app.route('/dashboard.html')
@login_required
def dashboard_page():
    return render_template('dashboard.html')

@app.route('/admin_dashboard')
@app.route('/admin_dashboard.html')
@admin_required
def admin_dashboard_page():
    return render_template('admin_dashboard.html')

@app.route('/report')
@app.route('/report.html')
@login_required
def report_page():
    return render_template('report.html')

# Load Haar cascade once
CASCADE_PATH = 'haarcascade_frontalface_default.xml'
face_cascade = cv2.CascadeClassifier(CASCADE_PATH)

@app.route('/api/detect_faces', methods=['POST'])
def detect_faces():
    try:
        data = request.get_json(silent=True) or {}
        image_b64 = data.get('image')
        if not image_b64:
            return jsonify({'error': 'No image provided'}), 400

        if ',' in image_b64:
            image_b64 = image_b64.split(',', 1)[1]
        try:
            image_data = base64.b64decode(image_b64, validate=True)
        except (TypeError, ValueError):
            return jsonify({'error': 'Invalid image encoding'}), 400

        np_arr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img is None:
            return jsonify({'error': 'Invalid image data'}), 400

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(30, 30))

        # Robust conversion to list
        if isinstance(faces, np.ndarray):
            boxes = faces.tolist()
        else:
            # faces is likely a tuple of arrays (or empty tuple)
            boxes = [list(face) for face in faces] if faces else []

        return jsonify({'face_count': len(faces), 'boxes': boxes}), 200
    except Exception as e:
        logger.exception('Face detection error')
        return jsonify({'error': str(e)}), 500
    
# ---------- Authentication ----------
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    logger.debug(f"Registration data: {data}")
    
    role = data.get('role')
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not all([role, name, email, password]):
        return jsonify({'error': 'Missing required fields'}), 400
    if not email.endswith('@gmail.com'):
        return jsonify({'error': 'Email must be @gmail.com'}), 400
    if len(password) != 6:
        return jsonify({'error': 'Password must be exactly 6 characters'}), 400

    # Check email exists
    if db.get_user_by_email(email):
        return jsonify({'error': 'Email already registered'}), 400

    try:
        if role == 'student':
            student_id = data.get('student_id')
            session_id = data.get('session_id')
            if not student_id or not session_id:
                return jsonify({'error': 'Student ID and Session ID required'}), 400
            if not student_id.isdigit() or len(student_id) != 4:
                return jsonify({'error': 'Student ID must be exactly 4 numbers'}), 400
            if not (len(session_id) == 6 and session_id[:4].isalpha() and session_id[4:].isdigit()):
                return jsonify({'error': 'Session ID must be 4 letters + 2 numbers'}), 400

            user_id = db.create_user(email, password, name, role, student_id, session_id)
            logger.info(f"Created student with ID: {user_id}")
            # Auto-login
            session['user_id'] = user_id
            session['role'] = role
            session['name'] = name
            logger.info(f"Session set after registration: {dict(session)}")
            return jsonify({
                'message': 'Student registered successfully',
                'role': 'student',
                'user_id': user_id,
                'auto_login': True
            }), 201

        elif role == 'admin':
            user_id = db.create_user(email, password, name, role)
            logger.info(f"Created admin with ID: {user_id}")
            session['user_id'] = user_id
            session['role'] = role
            session['name'] = name
            logger.info(f"Session set after registration: {dict(session)}")
            return jsonify({
                'message': 'Admin registered successfully',
                'role': 'admin',
                'user_id': user_id,
                'auto_login': True
            }), 201

        else:
            return jsonify({'error': 'Invalid role'}), 400

    except sqlite3.IntegrityError as e:
        logger.error(f"IntegrityError: {e}")
        return jsonify({'error': 'Student ID or email already used'}), 400
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    logger.debug(f"Login attempt: email={email}")

    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    if not email.endswith('@gmail.com'):
        return jsonify({'error': 'Email must be @gmail.com'}), 400
    if len(password) != 6:
        return jsonify({'error': 'Password must be exactly 6 characters'}), 400

    user = db.get_user_by_email(email)
    if not user or user['password'] != password:
        logger.warning(f"Invalid credentials for {email}")
        return jsonify({'error': 'Invalid credentials'}), 401

    session['user_id'] = user['id']
    session['role'] = user['role']
    session['name'] = user['name']
    logger.info(f"Session after login: {dict(session)}")

    return jsonify({
        'id': user['id'],
        'email': user['email'],
        'name': user['name'],
        'role': user['role'],
        'student_id': user['student_id'],
        'session_id': user['session_id']
    }), 200

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out'}), 200

# ---------- Student Dashboard API ----------
 #@app.route('/api/dashboard/student', methods=['GET'])
#@login_required
#def student_dashboard():
   # user_id = session['user_id']
   # user = db.get_user_by_id(user_id)
   # stats = db.get_user_stats(user_id)
   # events = db.get_events_by_user(user_id)

   # return jsonify({
       # 'user': dict(user) if user else None,
       # 'stats': dict(stats) if stats else None,
       # 'events': [dict(e) for e in events],
       # 'exam_running': bool(stats['exam_running']) if stats else False,
       # 'integrity_score': stats['integrity_score'] if stats else 100,
       # 'final_score': stats['integrity_score'] if stats and not stats['exam_running'] else None
    #}), 200 

@app.route('/api/dashboard/student', methods=['GET'])
@login_required
def student_dashboard():
    user_id = session['user_id']
    user = db.get_user_by_id(user_id)
    stats = db.get_user_stats(user_id)
    events = db.get_events_by_user(user_id)

    # Use the scorer
    from integrity_scorer import IntegrityScorer
    stats_dict = dict(stats) if stats else {}
    events_list = [dict(e) for e in events] if events else []
    scorer = IntegrityScorer(events_list, stats_dict)
    scorer = scorer.compute()

    return jsonify({
        'user': dict(user) if user else None,
        'stats': stats_dict,
        'events': events_list,
        'exam_running': bool(stats_dict.get('exam_running', False)),
        'integrity_score': scorer['score'],  # normalized
        'final_score': scorer['score'] if not stats_dict.get('exam_running') else None,
        'risk_label': scorer['risk_label'],
        'face_ratio': scorer['face_ratio'],
        'total_deduction': scorer['total_deduction'],
        'event_counts': scorer['event_counts'],
    }), 200
    
# ---------- Admin Dashboard API ----------
@app.route('/api/dashboard/admin', methods=['GET'])
@admin_required
def admin_dashboard():
    # 1. Get the global stats and analytics (Total candidates, Active, Avg Integrity, etc.)
    dashboard_data = db.get_admin_dashboard_data()
    
    # 2. Read the filter parameters sent from your frontend
    candidate_id = request.args.get('candidate_id')
    event_type = request.args.get('event_type')
    date_str = request.args.get('date')
    
    # 3. Fetch the EVENTS using your new filtered function
    filtered_events = db.get_filtered_events(candidate_id, event_type, date_str)
    
    # 4. Construct the final response
    response_data = {
        "stats": dashboard_data['stats'],
        "analytics": dashboard_data['analytics'],
        "students": dashboard_data['students'],
        "events": filtered_events  # <--- Replaces the unfiltered events with your filtered ones!
    }
    
    return jsonify(response_data), 200
# ---------- Event Logging ----------
@app.route('/api/events', methods=['POST'])
@login_required
def log_event():
    user_id = session['user_id']
    data = request.json
    event_type = data.get('type')
    deducted = data.get('deducted', 0)
    screenshot_base64 = data.get('screenshot')

    if not event_type:
        return jsonify({'error': 'Event type required'}), 400

    # Fetch the user to get student_id
    user = db.get_user_by_id(user_id)
    # Use student_id if it exists, otherwise fallback to user_id
    candidate_folder_id = user['student_id'] if user and user['student_id'] else user_id

    screenshot_path = None
    if screenshot_base64 and screenshot_base64.startswith('data:image'):
        header, encoded = screenshot_base64.split(',', 1)
        ext = header.split(';')[0].split('/')[1]
        filename = f"{event_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{ext}"
        # Use candidate_folder_id for the folder name
        user_folder = os.path.join(app.config['UPLOAD_FOLDER'], str(candidate_folder_id))
        os.makedirs(user_folder, exist_ok=True)
        file_path = os.path.join(user_folder, filename)
        with open(file_path, 'wb') as f:
            f.write(base64.b64decode(encoded))
        # Store path relative to UPLOAD_FOLDER using candidate_folder_id
        screenshot_path = f"{candidate_folder_id}/{filename}"
        db.save_evidence(user_id, screenshot_path)

    event_id = db.log_event(user_id, event_type, deducted, screenshot_path)
    db.update_stats_after_event(user_id, deducted, event_type)

    return jsonify({'message': 'Event logged', 'event_id': event_id, 'screenshot_path': screenshot_path}), 201

# ---------- Evidence serving ----------
@app.route('/evidence/<path:filepath>')
@login_required
def serve_evidence(filepath):
    user = db.get_user_by_id(session['user_id'])
    full_path = os.path.join(app.config['UPLOAD_FOLDER'], filepath)
    
    # Admin can see everything
    if user['role'] == 'admin':
        return send_from_directory(app.config['UPLOAD_FOLDER'], filepath)
    
    # For students: check that the filepath starts with their student_id or user_id
    allowed_prefixes = []
    if user['student_id']:   # if student_id exists and is not None
        allowed_prefixes.append(str(user['student_id']))
    allowed_prefixes.append(str(user['id']))  # fallback to internal ID
    
    if not any(filepath.startswith(prefix + '/') for prefix in allowed_prefixes):
        return jsonify({'error': 'Forbidden'}), 403
    
    return send_from_directory(app.config['UPLOAD_FOLDER'], filepath)
# ---------- Report ----------
@app.route('/api/report/<int:user_id>', methods=['GET'])
@login_required
def get_report(user_id):
    user = db.get_user_by_id(session['user_id'])
    if session['user_id'] != user_id and user['role'] != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    target_user = db.get_user_by_id(user_id)
    stats = db.get_user_stats(user_id)
    events = db.get_events_by_user(user_id)

    return jsonify({
        'user': dict(target_user) if target_user else None,
        'stats': dict(stats) if stats else None,
        'events': [dict(e) for e in events]
    }), 200

# ---------- Exam control ----------
@app.route('/api/exam/start', methods=['POST'])
@login_required
def start_exam():
    db.set_exam_running(session['user_id'], True)
    return jsonify({'message': 'Exam started'}), 200

@app.route('/api/exam/end', methods=['POST'])
@login_required
def end_exam():
    db.set_exam_running(session['user_id'], False)
    return jsonify({'message': 'Exam ended'}), 200

# Integrity report APIs
@app.route('/api/integrity_report', methods=['GET'])
@login_required
def current_integrity_report():
    """Return the authenticated candidate's report without trusting a client ID."""
    report = db.get_integrity_report(session['user_id'])
    return jsonify(report), 200

@app.route('/api/integrity_report/<int:user_id>', methods=['GET'])
@login_required
def integrity_report(user_id):
    current_user = db.get_user_by_id(session['user_id'])
    if session['user_id'] != user_id and current_user['role'] != 'admin':
        return jsonify({'error': 'Forbidden'}), 403

    report = db.get_integrity_report(user_id)
    return jsonify(report), 200

@app.route('/api/ai/ask', methods=['POST'])
@login_required
def ai_ask():
    """Answer a question using only the authenticated role's authorized data."""
    payload = request.get_json(silent=True) or {}
    current_user = db.get_user_by_id(session['user_id'])
    if not current_user:
        session.clear()
        return jsonify({'error': 'Authentication required'}), 401

    try:
        answer = answer_question(
            dict(current_user),
            payload.get('question'),
            payload.get('history'),
        )
        return jsonify({'answer': answer}), 200
    except AIServiceError as exc:
        return jsonify({'error': str(exc)}), exc.status_code
    except Exception:
        logger.exception('AI Ask request failed')
        return jsonify({'error': 'AI Ask is temporarily unavailable. Please try again.'}), 502


@app.route('/admin_logs')
@admin_required
def admin_logs_page():
    return render_template('admin_logs.html')

# ---------- Run ----------
if __name__ == '__main__':
    app.run(debug=True, port=5000)