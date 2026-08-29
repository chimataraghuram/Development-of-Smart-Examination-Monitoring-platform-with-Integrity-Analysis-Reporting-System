# ExamMonitor
> AI-powered online examination monitoring and invigilation platform.

[Project Overview](#-about-the-project) • [Features](#-key-features) • [Installation](#-installation) • [Usage](#%E2%96%B6%EF%B8%8F-running-the-project) • [Documentation](#-documentation)

---

## 🚀 Quick Overview

| | |
|---|---|
| **Project** | ExamMonitor |
| **Type** | AI-powered Online Examination Monitoring |
| **Program** | Infosys Virtual Internship 7.0 |
| **Architecture** | Frontend + Backend |
| **Monitoring** | Face & Browser Activity Monitoring |
| **AI** | AI-powered Candidate & Admin Assistant |
| **Reporting** | Examination & Monitoring Reports |
| **License** | MIT |

---

## 📌 About the Project
ExamMonitor is an online examination monitoring platform designed to help institutions conduct and monitor examinations through a centralized system. The platform provides separate experiences for:
- 👨‍🎓 **Candidates**
- 👨‍💼 **Administrators / Invigilators**

It combines examination management, candidate monitoring, suspicious-event detection, session tracking, statistics, reporting, and AI-assisted insights in one platform.

---

## 🎯 Objectives
- Conduct online examinations in a controlled environment
- Monitor candidates during examinations
- Detect and record suspicious activities
- Provide administrators with centralized examination insights
- Generate examination reports
- Provide candidates with clear examination and result information
- Provide AI-assisted answers and insights

---

## ✨ Key Features

### 👨‍🎓 Candidate Panel
- Candidate profile
- Examination access
- System readiness diagnostics
- Camera and monitoring checks
- Examination session monitoring
- Activity history
- Monitoring statistics
- Examination report
- Report download
- AI Ask assistant

### 👨‍💼 Admin / Invigilator Panel
- Dashboard overview
- Live candidate monitoring
- Examination management
- Action center
- Suspicious alerts
- Event logs
- Candidate information
- Session information
- Monitoring statistics
- Report generation
- Report export
- AI Ask assistant

### 🤖 AI Assistant
#### Candidate AI
The candidate assistant can answer questions such as:
- What are my examination rules?
- What is my current score?
- What is my examination about?
- Do I have an examination today?
- What is my examination status?
- Can I take a break?
- What happened during my examination?
- What is my monitoring status?
- What is my risk level?
- How many suspicious events were detected?

Responses should be concise and personalized using the candidate's available examination/session data.

#### Admin AI
The administrator assistant can provide personalized examination insights, such as:
- Who scored the highest?
- Who scored the lowest?
- What is the average score?
- How many candidates completed the examination?
- Did we conduct an examination today?
- Which candidates have high-risk activity?
- How many suspicious events occurred?
- Which candidate has the most alerts?
- Show candidate/session information
- Summarize examination activity

Where supported, candidate data can also be prepared for export.

---

## 🔍 Monitoring & Integrity
ExamMonitor records examination monitoring events such as:
- Face absence
- Multiple faces
- Browser focus loss
- Tab switching

The system maintains event timestamps and associated monitoring information for examination review.

---

## 📊 Reports
The system provides examination reports containing relevant information such as:
- Candidate details
- Session information
- Examination result
- Monitoring statistics
- Risk level
- Face presence information
- Suspicious events
- Event timestamps
- Available evidence/screenshots

Reports can be viewed and exported where supported.

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
├── scripts/
│   └── run_local.ps1
│
├── .env.example
├── .gitignore
├── FINAL_SUBMISSION_AUDIT.md
├── LICENSE
└── README.md
```

---

## 🛠️ Technology Stack

**Backend**
- Python
- Flask
- SQLite
- OpenCV (Haar Cascade Classifier)
- Scikit-Image

**Frontend**
- HTML
- CSS
- JavaScript

**AI**
- OpenRouter API

**Monitoring**
- Camera / video monitoring
- Browser activity monitoring
- Face detection
- Suspicious-event detection

---

## ⚙️ Requirements
Before running the project, make sure you have:
- Python 3.9+
- SQLite (built into Python)
- Node.js & npm (for optional frontend testing packages)

---

## 🚀 Installation

1. **Clone the repository**
```bash
git clone https://github.com/chimataraghuram/Development-of-Smart-Examination-Monitoring-platform-with-Integrity-Analysis-Reporting-System.git ExamMonitor
cd ExamMonitor
```

2. **Backend setup**
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
Install dependencies:
```bash
pip install -r Backend/requirements.txt
```

3. **Frontend setup**
```bash
cd Frontend
npm install
cd ..
```

4. **Environment configuration**
Create a `.env` file in the root directory based on `.env.example`.
```env
# Example only
FLASK_SECRET_KEY=your_secret_key_here
OPENROUTER_API_KEY=your_api_key_here
ADMIN_DEFAULT_PASSWORD=your_admin_password
```
*Do not commit real API keys, passwords, tokens, or other secrets.*

---

## ▶️ Running the Project

### Backend

To run the Flask application natively from the repository root:
```bash
python -m Backend.app
```

### Windows

From the repository root, you can use the provided PowerShell runner to automatically start the environment and server:
```powershell
.\scripts\run_local.ps1
```

### Frontend

*(Note: The frontend HTML templates are rendered directly by the Flask backend, so no separate frontend development server is required).*

---

## 👤 User Flow

**Candidate Flow**
Candidate Login ↓ Candidate Dashboard ↓ System Readiness Check ↓ Start Examination ↓ Monitoring ↓ Examination Completion ↓ Result / Report

**👨‍💼 Admin Flow**
Admin Login ↓ Dashboard ↓ Live Monitoring ↓ Examination Management ↓ Suspicious Alerts / Event Logs ↓ Candidate & Session Review ↓ Report Generation

---

## 🔐 Security
The project follows basic security practices including:
- Environment variables for sensitive configuration
- `.gitignore` for local/sensitive files
- No real credentials in the repository
- Protected authentication routes
- Controlled access to admin functionality

---

## 🧪 Testing
Testing includes verification of:
- Authentication
- Candidate examination flow
- Admin dashboard
- Monitoring
- Suspicious-event logging
- Database operations
- Reports
- AI assistant
- Frontend/backend communication

Diagnostic scripts are located in the `scripts/` directory to verify endpoints.

---

## 📚 Documentation
Project documentation is available in:
`Agile Documentation/`
This includes the project's available Agile and development documentation.

Additional final-submission information is available in:
`FINAL_SUBMISSION_AUDIT.md`

---

## 📸 Project Screenshots

**Evidence: Face Absence Detection**
![Face Absence](evidence/0222/Face%20Not%20Detected_20260812_192430.png)

**Evidence: Multiple Faces Detection**
![Multiple Faces](evidence/0222/Multiple_Faces_20260825_192620_159041_3fc19b38.png)

*(Note: Live dashboard screenshots have not been tracked in the repository. The above images demonstrate the real-time computer vision monitoring engine storing evidence.)*

---

## 🎓 Internship Project

This project was developed as part of the **Infosys Virtual Internship 7.0**.

**Mentor:** Subramaniam Sir

This was developed collaboratively as a team project under mentor guidance
throughout the internship project lifecycle.

---

## 👥 Team

### CHIMATA RAGHURAM
- 🔗 **LinkedIn:** https://www.linkedin.com/in/chimataraghuram/
- 💻 **GitHub:** https://github.com/chimataraghuram

### NARLA SAHITHYA REDDY
- 🔗 **LinkedIn:** https://www.linkedin.com/in/narla-sahithyareddy-056342399/
- 💻 **GitHub:** https://github.com/narlasahithyareddy

### SIREESHA JONNADA
- 🔗 **LinkedIn:** https://www.linkedin.com/in/sireesha-jonnada-650468315
- 💻 **GitHub:** https://github.com/sireeshajonnada05-pixel

### THOTA SATHWIKA
- 🔗 **LinkedIn:** https://www.linkedin.com/in/thota-sathwika-2648b42bb
- 💻 **GitHub:** https://github.com/thota-sathwika

---

## 📄 License

This project is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.
