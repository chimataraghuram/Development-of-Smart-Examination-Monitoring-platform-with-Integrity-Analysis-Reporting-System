# ExamMonitor
> AI-powered online examination monitoring and invigilation platform.

*Developed collaboratively as a team project for the Infosys Virtual Internship 7.0 under the mentorship of Subramaniam Sir.*

---

## 📌 About the Project
ExamMonitor is an online examination monitoring platform designed to help institutions conduct and monitor examinations through a centralized system. It provides a secure testing environment by actively monitoring candidates and detecting suspicious events.

The platform includes:
- Real-time candidate monitoring using computer vision
- Suspicious-event detection (e.g., face absence, multiple faces, browser tab switching)
- Automated integrity scoring based on violations
- Continuous activity and event tracking
- Comprehensive statistics and exportable reports
- Centralized admin monitoring dashboard
- Context-aware AI assistant functionality for both candidates and administrators

---

## 🎯 Objectives
- Conduct online examinations in a controlled, secure environment.
- Continuously monitor candidates during examinations.
- Detect and record suspicious activities automatically.
- Provide administrators with centralized examination insights and alerts.
- Generate comprehensive examination integrity reports.
- Provide candidates with clear examination rules and result information.
- Provide AI-assisted answers and insights on demand.

---

## ✨ Key Features

### Candidate Features
- Candidate profile and authentication
- System readiness diagnostics (Camera and monitoring checks)
- Examination access and active session monitoring
- Activity history and monitoring statistics
- Downloadable examination reports

### AI-Powered Monitoring
- Face absence detection
- Multiple faces detection
- Browser focus loss and tab switching detection
- Context-aware AI assistant (Candidate AI & Admin AI)

### Admin Features
- Dashboard overview and live candidate monitoring
- Examination management and candidate assignments
- Action center with live suspicious alerts and event logs
- Candidate and session information review

### Reports & Analytics
- Automated integrity scoring
- Comprehensive monitoring statistics
- Report generation and export

### Security/Integrity
- Automated violation logging with timestamps
- Webcam evidence capture for flagged events
- SQLite persistence for audit trails

---

## 🛠️ Technologies Used
- **Backend:** Python, Flask, SQLite
- **Computer Vision:** OpenCV (Haar Cascade Classifier), Scikit-Image
- **Frontend:** HTML, CSS, Vanilla JavaScript
- **AI Integration:** OpenRouter API

---

## 🏗️ Project Structure
```text
ExamMonitor/
├── Agile Documentation/
│   ├── Agile_Template_Completed.xlsm
│   ├── Agile_Template_v0.1_Completed.xlsx
│   ├── Defect_Tracker_Template_v0.1_Completed.xlsx
│   ├── Sample_Agile_Completed.xls
│   └── Unit_Test_Plan_v0.1_Completed.xlsx
│
├── Backend/
│   ├── app.py
│   ├── database.py
│   ├── ai_service.py
│   ├── integrity_scorer.py
│   ├── export_service.py
│   ├── haarcascade_frontalface_default.xml
│   ├── requirements.txt
│   └── exam_monitor.db
│
├── Frontend/
│   ├── package.json
│   ├── package-lock.json
│   ├── templates/
│   └── static/
│
├── evidence/
│   └── (Candidate monitoring screenshots and event logs)
│
├── scripts/
│   └── run_local.ps1
│
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🚀 Running the Project

### 1. Clone the repository
```bash
git clone https://github.com/chimataraghuram/Development-of-Smart-Examination-Monitoring-platform-with-Integrity-Analysis-Reporting-System.git ExamMonitor
cd ExamMonitor
```

### 2. Configure Environment Variables
Create a `.env` file in the root directory based on `.env.example`.
```env
FLASK_SECRET_KEY=your_secret_key_here
OPENROUTER_API_KEY=your_api_key_here
ADMIN_DEFAULT_PASSWORD=your_admin_password
```
*Note: Do not commit real API keys, passwords, tokens, or other secrets.*

### 3. Setup Virtual Environment & Install Dependencies
```bash
python -m venv .venv
```
Activate the virtual environment.

*Windows:*
```cmd
.venv\Scripts\activate
```
*Linux/macOS:*
```bash
source .venv/bin/activate
```
Install backend dependencies:
```bash
pip install -r Backend/requirements.txt
```

### 4. Start the Application
To run the Flask application natively from the repository root:
```bash
python -m Backend.app
```
*(Windows users can alternately use the provided PowerShell script from the root: `.\scripts\run_local.ps1`)*

The application will be accessible locally at `http://127.0.0.1:5000/`. The frontend HTML templates are rendered directly by the Flask backend, so no separate frontend development server is required.

---

## 👤 User Flow

**Candidate Flow**
Candidate Login ↓ Candidate Dashboard ↓ System Readiness Check ↓ Start Examination ↓ Monitoring ↓ Examination Completion ↓ Result / Report

**Admin Flow**
Admin Login ↓ Dashboard ↓ Live Monitoring ↓ Examination Management ↓ Suspicious Alerts / Event Logs ↓ Candidate & Session Review ↓ Report Generation

---

## 🔐 Security
- Environment variables for sensitive configuration
- `.gitignore` for local database and sensitive files
- Protected authentication routes
- Controlled access to administrator functionality

---

## 🧪 Testing
The project includes verification for authentication, candidate examination flow, admin dashboard functionality, computer vision monitoring, suspicious-event logging, database operations, and frontend/backend communication.

Diagnostic scripts are located in the `scripts/` directory to verify backend endpoints.

---

## 📚 Documentation
The repository contains the required Agile and project documentation located under the `Agile Documentation/` directory.

---

## 📸 Project Screenshots

**Evidence: Face Absence Detection**
![Face Absence](evidence/0222/Face%20Not%20Detected_20260812_192430.png)

**Evidence: Multiple Faces Detection**
![Multiple Faces](evidence/0222/Multiple_Faces_20260825_192620_159041_3fc19b38.png)

*(Note: Live dashboard screenshots have not been tracked in the repository. The above images demonstrate the real-time computer vision monitoring engine storing evidence.)*

---

## 🎓 Internship

This project was developed as part of the Infosys Virtual Internship 7.0 program.

**Mentor:** Subramaniam Sir

---

## 👥 Team

This is a collaborative team project developed by:

### CHIMATA RAGHURAM
- LinkedIn: https://www.linkedin.com/in/chimataraghuram/
- GitHub: https://github.com/chimataraghuram

### NARLA SAHITHYA REDDY
- LinkedIn: https://www.linkedin.com/in/narla-sahithya-reddy-056342399/
- GitHub: https://github.com/narlasahithyareddy

### SIREESHA JONNADA
- LinkedIn: https://www.linkedin.com/in/sireesha-jonnada-650468315
- GitHub: https://github.com/sireeshajonnada05-pixel

### THOTA SATHWIKA
- LinkedIn: https://www.linkedin.com/in/thota-sathwika-2648b42bb
- GitHub: https://github.com/thota-sathwika

---

## 📄 License

This project is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.
