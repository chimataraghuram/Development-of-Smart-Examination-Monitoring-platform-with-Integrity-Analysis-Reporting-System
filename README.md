# 🎓 Development of Smart Examination Monitoring platform with Integrity Analysis Reporting System

An AI-powered Online Exam Monitoring System developed as part of an internship project. The platform helps monitor candidates during online examinations using computer vision and event logging to improve exam integrity.

---

## 🚀 Features

### 👤 Candidate Management
- Candidate Registration
- Candidate Login
- Dashboard
- SQLite Database Integration

### 📷 OpenCV Integration
- Access System Webcam
- Live Video Feed
- Capture Candidate Photo
- Save Photos Automatically

### 😀 Face Detection
- Haar Cascade Face Detection
- Real-Time Face Monitoring
- Face Detected / Face Not Detected Status
- Bounding Box Around Face

### ⏱️ Monitoring Features
- Continuous Face Presence Monitoring
- Face Absence Duration Tracking
- Current Time Display
- Real-Time Monitoring Information

### 📋 Event Logging
Whenever a candidate's face is not detected, the system automatically logs:

- Candidate ID
- Event Type
- Timestamp
- Remarks

All events are stored in an SQLite database.

### 📝 Session Management
- Start Exam
- Pause Exam
- Resume Exam
- End Exam

---

## 🛠️ Technologies Used

- Python
- Flask
- SQLite
- OpenCV
- Haar Cascade Classifier
- HTML
- CSS
- JavaScript

---

## 📂 Project Structure

```
Development-of-Smart-Examination-Monitoring-platform-with-Integrity-Analysis-Reporting-System
│
├── app.py
├── requirements.txt
├── README.md
├── LICENSE
│
├── database/
│   ├── exam.db
│   └── candidates.csv
│
├── models/
│   ├── database.py
│   ├── candidate.py
│   └── faker_data.py
│
├── modules/
│   ├── authentication.py
│   ├── registration.py
│   ├── monitoring.py
│   ├── report.py
│   └── scoring.py
│
├── scripts/
│   ├── face_detection.py
│   ├── camera_test.py
│   ├── check_database.py
│   ├── export_exam_db.py
│   └── exam.py
│
├── static/
├── templates/
├── photos/
└── haarcascade/
```

---

## ⚙️ Installation

Clone the repository:

```bash
git clone <repository-url>
```

Move into the project directory:

```bash
cd Development-of-Smart-Examination-Monitoring-platform-with-Integrity-Analysis-Reporting-System
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## ▶️ Run the Project

Start the Flask application:

```bash
python app.py
```

Run Face Detection:

```bash
python scripts/face_detection.py
```

Run Camera Test:

```bash
python scripts/camera_test.py
```

---

## 📸 Current Modules

- ✅ Candidate Registration
- ✅ Candidate Login
- ✅ Dashboard
- ✅ Photo Capture
- ✅ Face Detection
- ✅ Continuous Face Monitoring
- ✅ Face Absence Tracking
- ✅ Event Logging
- ✅ Session Management
- ✅ SQLite Database

---

## 📈 Future Improvements

- Face Recognition
- Multiple Face Detection Alerts
- Browser Tab Monitoring
- Eye Gaze Tracking
- Head Pose Detection
- AI-Based Proctoring
- PDF Report Generation
- Email Notifications
- Admin Dashboard
- Exam Analytics

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 TEAM

**Raghuram Chimata**

GitHub: https://github.com/chimataraghuram

LinkedIn: https://linkedin.com/in/chimataraghuram

Portfolio: https://chimataraghuram.vercel.app