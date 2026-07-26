from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import re
import cv2
import os
import subprocess
from pathlib import Path
from datetime import datetime

app = Flask(__name__)
app.secret_key = "infosys_exam_monitoring"


def login_required(view_func):
    def wrapper(*args, **kwargs):
        if not session.get("candidate_id"):
            return redirect(url_for("login_page"))
        return view_func(*args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def capture_photo(candidate_id):

    if not os.path.exists("photos"):
        os.makedirs("photos")

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        return None

    while True:

        ret, frame = camera.read()

        cv2.imshow("Capture Photo", frame)

        key = cv2.waitKey(1)

        if key == ord('c'):

            photo_path = f"photos/{candidate_id}.jpg"

            cv2.imwrite(photo_path, frame)

            break

    camera.release()
    cv2.destroyAllWindows()

    return photo_path


# ---------------- Home ----------------
@app.route("/")
def home():
    if session.get("candidate_id"):
        return redirect(url_for("dashboard"))
    return render_template("register.html")


# ---------------- Candidate Registration ----------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        if session.get("candidate_id"):
            return redirect(url_for("dashboard"))
        return render_template("register.html")


    candidate_id = request.form["candidate_id"].strip()
    name = request.form["name"].strip()
    email = request.form["email"].strip()
    password = request.form["password"]

    # ---------- Validation ----------

    # Empty Fields
    if candidate_id == "" or name == "" or email == "" or password == "":
        return "All fields are required!"

    # Email Validation
    email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'

    if not re.match(email_pattern, email):
        return "Invalid Email Format!"

    # Password Validation
    if password == "":
        return "Password cannot be empty!"
    # ---------- Database ----------
    try:
        with sqlite3.connect("database/exam.db") as connection:
            cursor = connection.cursor()

            # Check Duplicate Email
            cursor.execute(
                "SELECT * FROM Candidate WHERE email=?",
                (email,)
            )

            user = cursor.fetchone()

            if user:
                return "Email already registered! Please use another email."

            # Do not capture photo at registration time; use placeholder
            photo_path = ""

            # Debug prints to confirm values before insert
            print(candidate_id)
            print(name)
            print(email)
            print(photo_path)

            # Insert Candidate (photo will be captured on Start Exam)
            cursor.execute("""
                INSERT INTO Candidate(candidate_id, name, email, password, photo_path)
                VALUES (?, ?, ?, ?, ?)
            """, (candidate_id, name, email, password, photo_path))

            # Commit explicitly
            connection.commit()
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"Error: {e}"

    # Redirect to Login Page
    return redirect("/login")


# ---------------- Login Page ----------------
@app.route("/login")
def login_page():
    if session.get("candidate_id"):
        return redirect(url_for("dashboard"))
    return render_template("login.html")


# ---------------- Login ----------------
@app.route("/login", methods=["POST"])
def login():

    email = request.form["email"]
    password = request.form["password"]

    try:
        with sqlite3.connect("database/exam.db") as connection:
            cursor = connection.cursor()
            cursor.execute(
                "SELECT candidate_id, name FROM Candidate WHERE email=? AND password=?",
                (email, password)
            )
            user = cursor.fetchone()
    except Exception as e:
        print("Error logging in:", e)
        return "Login failed. Please try again."

    if user:
        # store candidate_id and name in session for later use
        session['candidate_id'] = user[0]
        session['candidate_name'] = user[1]
        return redirect("/dashboard")
    else:
        return "Invalid Email or Password"


# ---------------- Candidate Dashboard ----------------
@app.route("/dashboard")
@login_required
def dashboard():
    candidate_id = session["candidate_id"]
    latest_session = {
        "start_time": "N/A",
        "end_time": "N/A",
        "status": "No Session"
    }
    browser_loss_count = 0
    face_missing_count = 0
    face_detected_count = 0

    try:
        with sqlite3.connect("database/exam.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT start_time, end_time, status
                FROM Session
                WHERE candidate_id = ?
                ORDER BY session_id DESC
                LIMIT 1
            """, (candidate_id,))
            session_row = cursor.fetchone()
            if session_row:
                latest_session["start_time"] = session_row[0] or "N/A"
                latest_session["end_time"] = session_row[1] or "N/A"
                latest_session["status"] = session_row[2] or "N/A"

            cursor.execute("""
                SELECT COUNT(*)
                FROM EventLog
                WHERE candidate_id = ? AND event_type = 'Browser Focus Lost'
            """, (candidate_id,))
            browser_loss_count = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT COUNT(*)
                FROM EventLog
                WHERE candidate_id = ? AND event_type = 'Face Not Detected'
            """, (candidate_id,))
            face_missing_count = cursor.fetchone()[0] or 0

            cursor.execute("""
                SELECT COUNT(*)
                FROM EventLog
                WHERE candidate_id = ? AND event_type = 'Face Detected'
            """, (candidate_id,))
            face_detected_count = cursor.fetchone()[0] or 0
    except Exception as e:
        print("Error loading dashboard summary:", e)

    return render_template(
        "dashboard.html",
        candidate=session["candidate_name"],
        candidate_id=session["candidate_id"],
        browser_loss_count=browser_loss_count,
        face_missing_count=face_missing_count,
        face_detected_count=face_detected_count,
        session_status=latest_session["status"],
        start_time=latest_session["start_time"],
        end_time=latest_session["end_time"]
    )


# ---------------- Session Page ----------------
@app.route("/session")
@login_required
def session_page():
    return render_template(
        "session.html",
        candidate=session["candidate_name"]
    )


# ---------------- Exam Page ----------------
@app.route("/exam")
@login_required
def exam():
    return render_template(
        "exam.html",
        candidate=session["candidate_name"]
    )

# ---------------- Start Exam ----------------
@app.route("/start_exam", methods=["POST"])
@login_required
def start_exam():
    candidate_id = session["candidate_id"]
    start_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with sqlite3.connect("database/exam.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO Session(candidate_id, start_time, status)
                VALUES (?, ?, ?)
            """, (candidate_id, start_time, "Started"))
    except Exception as e:
        print("Error starting exam:", e)
        return "Failed to start exam. Please try again."

    # mark exam as running so the face detection subprocess knows to continue
    try:
        project_dir = Path(__file__).resolve().parent
        status_path = project_dir / "exam_status.txt"
        with open(status_path, "w", encoding="utf-8") as f:
            f.write("RUNNING")
    except Exception as e:
        print("Error writing exam status file:", e)

    # start face detection process for this candidate (use full script path)
    try:
        project_dir = Path(__file__).resolve().parent

        face_detection_script = (
            project_dir /
            "scripts" /
            "face_detection.py"
        )

        subprocess.Popen([
            "python",
            str(face_detection_script),
            "--candidate-id",
            str(candidate_id)
        ])
    except Exception as e:
        print("Error launching face detection:", e)

    return redirect("/exam")

# ---------------- Pause Exam ----------------
@app.route("/pause_exam", methods=["POST"])
@login_required
def pause_exam():
    try:
        with sqlite3.connect("database/exam.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE Session
                SET status=?
                WHERE session_id=(SELECT MAX(session_id) FROM Session)
            """, ("Paused",))
    except Exception as e:
        print("Error pausing exam:", e)
        return "Failed to pause exam. Please try again."

    return "Exam Paused Successfully!"

# ---------------- Resume Exam ----------------
@app.route("/resume_exam", methods=["POST"])
@login_required
def resume_exam():
    try:
        with sqlite3.connect("database/exam.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE Session
                SET status=?
                WHERE session_id=(SELECT MAX(session_id) FROM Session)
            """, ("Resumed",))
    except Exception as e:
        print("Error resuming exam:", e)
        return "Failed to resume exam. Please try again."

    return "Exam Resumed Successfully!"

# ---------------- End Exam ----------------
@app.route("/end_exam", methods=["POST"])
@login_required
def end_exam():
    end_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with sqlite3.connect("database/exam.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""
                UPDATE Session
                SET end_time=?, status=?
                WHERE session_id=(SELECT MAX(session_id) FROM Session)
            """, (end_time, "Ended"))
    except Exception as e:
        print("Error ending exam:", e)
        return "Failed to end exam. Please try again."

    try:
        project_dir = Path(__file__).resolve().parent
        status_path = project_dir / "exam_status.txt"
        with open(status_path, "w", encoding="utf-8") as f:
            f.write("STOP")
    except Exception as e:
        print("Error writing exam status file:", e)

    return redirect("/dashboard")


# ---------------- Browser Event ----------------
@app.route("/browser_event", methods=["POST"])
@login_required
def browser_event():

    data = request.get_json()

    event_type = data["event"]

    candidate_id = session["candidate_id"]

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if event_type == "lost":
        event_name = "Browser Focus Lost"
        remarks = "Candidate switched away from exam"
    else:
        event_name = "Browser Focus Regained"
        remarks = "Candidate returned to exam"

    try:
        with sqlite3.connect("database/exam.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO EventLog(candidate_id, event_type, timestamp, remarks)
                VALUES (?, ?, ?, ?)
            """, (candidate_id, event_name, timestamp, remarks))
    except Exception as e:
        print("Error logging browser event:", e)
        return {"message": "Failed to log event"}, 500

    return {"message": "Event Logged Successfully"}


# ---------------- Event Logs ----------------
@app.route("/event_logs")
@login_required
def event_logs():
    try:
        with sqlite3.connect("database/exam.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT candidate_id, event_type, timestamp, remarks
                FROM EventLog
                ORDER BY timestamp DESC
            """)
            logs = cursor.fetchall()
    except Exception as e:
        print("Error loading event logs:", e)
        logs = []

    return render_template(
        "event_logs.html",
        logs=logs
    )


@app.route("/admin")
@login_required
def admin_dashboard():
    total_candidates = 0
    browser_events = 0
    face_events = 0
    total_events = 0

    try:
        with sqlite3.connect("database/exam.db") as connection:
            cursor = connection.cursor()

            cursor.execute("SELECT COUNT(*) FROM Candidate")
            total_candidates = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*)
                FROM EventLog
                WHERE event_type='Browser Focus Lost'
            """)
            browser_events = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*)
                FROM EventLog
                WHERE event_type='Face Not Detected'
            """)
            face_events = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM EventLog")
            total_events = cursor.fetchone()[0]
    except Exception as e:
        print("Error loading admin dashboard:", e)

    return render_template(
        "admin.html",
        total_candidates=total_candidates,
        browser_events=browser_events,
        face_events=face_events,
        total_events=total_events
    )



# ---------------- Integrity Report ----------------
@app.route("/report")
@login_required
def report():

    candidate_id = session.get("candidate_id")
    browser_lost = 0
    face_missing = 0

    try:
        with sqlite3.connect("database/exam.db") as connection:
            cursor = connection.cursor()
            cursor.execute("""
                SELECT COUNT(*)
                FROM EventLog
                WHERE candidate_id=?
                AND event_type='Browser Focus Lost'
            """, (candidate_id,))
            browser_lost = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*)
                FROM EventLog
                WHERE candidate_id=?
                AND event_type='Face Not Detected'
            """, (candidate_id,))
            face_missing = cursor.fetchone()[0]
    except Exception as e:
        print("Error loading report:", e)

    violations = browser_lost + face_missing

    score = max(0, 100 - violations * 2)

    status = "PASSED"

    if score < 75:
        status = "REVIEW REQUIRED"

    return render_template(
        "report.html",
        candidate_id=candidate_id,
        browser_lost=browser_lost,
        face_missing=face_missing,
        violations=violations,
        score=score,
        status=status
    )


# ---------------- Logout ----------------
@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect(url_for("login_page"))


if __name__ == "__main__":
    app.run(debug=True)