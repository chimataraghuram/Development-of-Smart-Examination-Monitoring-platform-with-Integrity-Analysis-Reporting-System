# 🎓 Development of Smart Examination Monitoring platform with Integrity Analysis Reporting System

An AI-powered Online Exam Monitoring System developed as part of an internship project. The platform helps monitor candidates during online examinations using computer vision and event logging to improve exam integrity.

---

## 🚀 Features

### 👤 Candidate Management
- Candidate Registration
- Candidate Login
- Modern Dark-Themed Candidate Dashboard
- SQLite Database Integration

### 📷 OpenCV Integration
- Access System Webcam
- Live Video Feed
- Capture Candidate Photo (Evidence)
- Save Photos Automatically

### 😀 Face Detection & Analytics
- Haar Cascade Face Detection
- Real-Time Face Monitoring
- Face Detected / Face Not Detected / Multiple Faces Status
- Dynamic Integrity Scoring Algorithm

### ⏱️ Monitoring Features
- Continuous Face Presence Monitoring
- Browser Tab & Focus Loss Tracking
- Real-Time Monitoring Information
- Animated Statistical Pie Charts

### 📋 Event Logging
Whenever a suspicious event occurs, the system automatically logs:

- Candidate ID
- Event Type (Face Absence, Focus Loss, Tab Switching)
- Timestamp
- Evidence (Base64 Screenshots)

### 📝 Session Management
- Start Exam
- End Exam
- Continuous Uninterrupted Sessions

### 🤖 AI Chatbot Assistant
- **Admin Assistant:** Instantly summarizes candidate logs, identifies high-risk behaviors, and gives actionable recommendations.
- **Candidate Assistant:** Provides real-time rule clarification, tech support, and exam anxiety reduction.
- **Context-Aware:** Powered by LLMs and aware of real-time monitoring data.

---

## 🛠️ Technologies Used

- Python (Flask)
- SQLite
- OpenCV (Haar Cascade Classifier)
- Scikit-Image
- HTML / CSS / JavaScript
- Google Gemini API

---

## 📂 Project Structure

```text
Development-of-Smart-Examination-Monitoring-platform-with-Integrity-Analysis-Reporting-System
│
├── app.py                         # Main Flask Application Entry Point
├── requirements.txt               # Python Dependencies
├── README.md
├── .env                           # Environment Variables (API Keys)
│
├── backend/                       # Core Backend Logic
│   ├── database.py                # SQLite Database Operations
│   ├── ai_service.py              # LLM Chatbot Integration
│   ├── export_service.py          # CSV/PDF Export Logic
│   ├── integrity_scorer.py        # Algorithmic Scoring Engine
│   └── haarcascade_frontalface_default.xml
│
├── frontend/                      # Frontend UI
│   └── templates/                 # HTML Views (Jinja2)
│       ├── _ai_assistant.html     # AI Chatbot Component
│       ├── admin_dashboard.html   # Admin View
│       ├── dashboard.html         # Candidate View
│       ├── login.html
│       ├── register.html
│       └── report.html
│
├── scripts/                       # Testing & Diagnostic Scripts
├── logs/                          # Application Logs
└── evidence/                      # Stored Webcam Screenshots
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

Set up your environment variables:
Create a `.env` file from `.env.example` and add your Google Gemini API key.

---

## ▶️ Run the Project

Start the Flask application:

```bash
python app.py
```

The application will run on `http://127.0.0.1:5000/`.

---

## 📸 Current Modules

- ✅ Candidate Registration & Login
- ✅ Admin Dashboard & Live Analytics
- ✅ Browser Tab & Focus Monitoring
- ✅ Photo/Evidence Capture
- ✅ Face Detection (OpenCV)
- ✅ Continuous Face Monitoring
- ✅ Integrity Scoring Algorithm
- ✅ Event Logging & Timeline
- ✅ Session Management
- ✅ SQLite Database
- ✅ Context-Aware AI Chatbot Assistant

---

## 📈 Future Improvements

- Face Recognition Integration
- Eye Gaze Tracking
- Head Pose Detection
- Advanced PDF Report Generation
- Email Notifications

---

## 📄 License

This project is licensed under the MIT License.

---

## 👨‍💻 TEAM

**Raghuram Chimata**

GitHub: https://github.com/chimataraghuram

LinkedIn: https://linkedin.com/in/chimataraghuram

Portfolio: https://chimataraghuram.vercel.app