import cv2
import sqlite3
import argparse
from datetime import datetime
from pathlib import Path

script_dir = Path(__file__).resolve().parent
base_dir = script_dir.parent

cascade_path = base_dir / "haarcascade" / "haarcascade_frontalface_default.xml"
face_cascade = cv2.CascadeClassifier(str(cascade_path))

if face_cascade.empty():
    print("Error: Haar Cascade XML file not loaded!")
    exit()

photos_dir = base_dir / "photos"
photos_dir.mkdir(parents=True, exist_ok=True)

parser = argparse.ArgumentParser(description='Face detection script')
parser.add_argument(
    "--candidate-id",
    type=str,
    required=True,
    help='Candidate ID for event logging'
)
args = parser.parse_args()
candidate_id = args.candidate_id
print("Candidate ID :", candidate_id)
face_missing = False
absence_start = None
absence_duration = 0
face_detected_count = 0
face_not_detected_count = 0

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

missed_frames = 0
detected_frames = 0
last_face = None
FACE_MISSING_THRESHOLD = 10
FACE_DETECTED_THRESHOLD = 3

while True:
    try:
        with open(base_dir / "exam_status.txt", "r", encoding="utf-8") as f:
            status = f.read().strip()
        if status == "STOP":
            print("Exam ended. Closing webcam...")
            break
    except FileNotFoundError:
        pass
    except Exception as e:
        print("Error reading exam status file:", e)

    ret, frame = camera.read()
    if not ret:
        break

    frame = cv2.resize(frame, (640, 480))
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.05,
        minNeighbors=7,
        minSize=(80,80)
    )

    current_date = datetime.now().strftime("%d-%m-%Y")
    current_time = datetime.now().strftime("%I:%M:%S %p")

    if len(faces) > 0:
        missed_frames = 0
        detected_frames += 1
        if detected_frames >= FACE_DETECTED_THRESHOLD:
            if face_missing:
                face_detected_count += 1

                db_path = base_dir / "database" / "exam.db"
                conn = sqlite3.connect(str(db_path))
                cur = conn.cursor()

                cur.execute(
                    """
                    INSERT INTO EventLog(candidate_id, event_type, timestamp, remarks)
                    VALUES (?, ?, ?, ?)
                    """,
                    (
                        candidate_id,
                        "Face Detected",
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Candidate returned to camera"
                    )
                )

                conn.commit()
                conn.close()

            face_missing = False
            absence_start = None
            absence_duration = 0

        last_face = faces[0]
        last_face_frames = 5
        detected_text = "Face Detected"
        status_color = (0, 255, 0)
    else:
        detected_frames = 0
        missed_frames += 1

        if missed_frames >= FACE_MISSING_THRESHOLD:
            if not face_missing:
                face_not_detected_count += 1
                face_missing = True
                absence_start = datetime.now()

                db_path = base_dir / "database" / "exam.db"
                conn = sqlite3.connect(str(db_path))
                cur = conn.cursor()

                cur.execute(
                    "INSERT INTO EventLog(candidate_id,event_type,timestamp,remarks) VALUES (?,?,?,?)",
                    (candidate_id, "Face Not Detected", datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Candidate face is absent")
                )

                conn.commit()
                conn.close()

            detected_text = "Face Not Detected"
            status_color = (0, 0, 255)
        else:
            # keep the previous state until the threshold is reached
            detected_text = "Face Detected" if not face_missing else "Face Not Detected"
            status_color = (0, 255, 0) if not face_missing else (0, 0, 255)

    if last_face is not None and last_face_frames > 0:
        x, y, w, h = last_face
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
        last_face_frames -= 1

    if face_missing and absence_start is not None:
        absence_duration = (datetime.now() - absence_start).seconds

    cv2.putText(frame, detected_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.9, status_color, 2)
    cv2.putText(frame, f"ONLINE EXAM MONITORING", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 150, 0), 2)
    cv2.putText(frame, f"Date : {current_date}", (20, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Time : {current_time}", (20, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, f"Absence : {absence_duration} sec", (20, 175), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
    cv2.putText(frame, f"Detected : {face_detected_count}", (20, 205), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f"Missing : {face_not_detected_count}", (20, 235), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    cv2.imshow("Face Detection", frame)

    key = cv2.waitKey(1) & 0xFF
    if key == ord("q"):
        break
    elif key == ord("c"):
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        cv2.imwrite(str(photos_dir / f"capture_{ts}.png"), frame)

camera.release()
cv2.destroyAllWindows()
