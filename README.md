# Smart Examination Monitoring Platform with Integrity Analysis Reporting System

An AI-powered online exam monitoring system. The platform monitors candidates during online examinations using computer vision, browser-event logging, integrity scoring, and administrator reporting.

---

## 1. Project Name
**Development of Smart Examination Monitoring Platform with Integrity Analysis Reporting System**

## 2. Project Overview
This project provides a robust platform for administering online examinations while maintaining academic integrity. It uses advanced monitoring techniques including face detection and browser behavior tracking to ensure a fair testing environment.

## 3. Problem Statement
With the shift towards remote learning and online assessments, traditional invigilation methods are no longer sufficient. There is a critical need for an automated, intelligent system that can continuously monitor candidates and accurately report suspicious activities to maintain the credibility of online exams.

## 4. Main Objectives
- Provide a secure, easy-to-use exam environment for candidates.
- Give administrators and invigilators real-time oversight of ongoing exams.
- Automate the detection of suspicious behaviors (e.g., looking away, multiple faces, switching tabs).
- Generate comprehensive integrity reports and automated scores.

## 5. Key Features
- **Real-time Monitoring:** Browser focus tracking and OpenCV Haar-cascade face detection.
- **Role-based Dashboards:** Dedicated panels for Candidates and Administrators.
- **Integrity Scoring:** Automated deductions based on violation severity.
- **AI Assistant:** Context-aware chatbot (via OpenRouter) to assist users and admins.
- **Reporting:** Exportable integrity reports and timeline logs.

## 6. Technology Stack
- **Backend:** Python, Flask
- **Database:** SQLite
- **Computer Vision:** OpenCV (Haar Cascade Classifier), Scikit-Image
- **Frontend:** HTML, CSS, JavaScript (Vanilla JS with glassmorphism UI)
- **AI Integration:** OpenRouter API

## 7. Project Architecture
The platform follows a monolithic client-server architecture. The Flask backend serves server-side rendered HTML templates and RESTful APIs, which the JavaScript frontend consumes to handle live monitoring (webcam feeds, browser events) and asynchronous data loading.

## 8. Repository Structure
\\	ext
ExamMonitor/
├── Frontend/
│   ├── package.json
│   ├── package-lock.json
│   ├── templates/            # HTML Templates
│   └── static/               # CSS, JS, Images
├── Backend/
│   ├── app.py                # Main Flask entry point
│   ├── requirements.txt      # Python dependencies
│   ├── database.py           # SQLite operations
│   ├── ai_service.py         # AI chatbot integration
│   ├── integrity_scorer.py   # Scoring logic
│   └── haarcascade...xml     # OpenCV model
├── Agile Documentation/      # Sprint plans, backlogs, user stories
├── evidence/                 # Internship screenshots and testing evidence
├── scripts/                  # Diagnostic and run scripts (e.g., run_local.ps1)
├── .env.example              # Environment variables template
├── .gitignore
├── FINAL_SUBMISSION_AUDIT.md # Audit document for final submission
├── LICENSE                   # MIT License
└── README.md                 # This file
\
## 9. Frontend Setup
The frontend uses standard web technologies. Optional Node dependencies (like JSDOM/Puppeteer) are listed in \Frontend/package.json\ for testing purposes.
\\ash
cd Frontend
npm install
cd ..
\
## 10. Backend Setup & 11. Environment Configuration
Create a virtual environment (recommended) and install backend dependencies:

\\ash
python -m venv .venv
# Windows:
.venv\Scriptsctivate
# macOS/Linux:
source .venv/bin/activate

pip install -r Backend/requirements.txt
\
Set up environment variables:
1. Copy \.env.example\ to a new file named \.env\ in the root directory.
2. Set a long random \FLASK_SECRET_KEY\.
3. Add \OPENROUTER_API_KEY\ if you want to enable the AI assistant.
4. Set \ADMIN_DEFAULT_PASSWORD\ to a strong private value before first use.

## 12. Database Setup
The application uses SQLite. On startup, it automatically creates or migrates the \Backend/exam_monitor.db\ database file and seeds the local administrator account (admin@gmail.com) using the \ADMIN_DEFAULT_PASSWORD\ from \.env\.

## 13. How to run the project
From the repository root (with the virtual environment activated):

\\ash
python -m Backend.app
\
The application will listen on \http://127.0.0.1:5000/\.

**Windows Users:** You can use the provided PowerShell script to automatically kill stale instances and start the server:
\\powershell
.\scriptsun_local.ps1
\
## 14. Candidate/User Features
- Secure registration and login.
- Exam workspace with readiness checks.
- Real-time display of integrity score and session status.
- Personal AI assistant for exam-related queries.
- Submission and post-exam reports.

## 15. Admin/Invigilator Features
- Comprehensive dashboard displaying active sessions and live metrics.
- Action center for reviewing suspicious alerts and flags.
- Ability to pause, resume, or terminate candidate sessions.
- Final review decisions on flagged exams.

## 16. AI Assistant Features
- Powered by OpenRouter, available directly in the UI.
- Context-aware: knows the student's current score, exam rules, and session status.
- Admin capabilities: can query the database to summarize candidate data and suspicious events on demand.

## 17. Monitoring Features
- **Browser Tracking:** Detects tab switching, window minimizing, and focus loss.
- **Vision Tracking:** Uses the webcam to detect Face Absence and Multiple Faces.
- Continuous event logging directly to the backend timeline.

## 18. Report Generation
- Automated integrity score calculation (starts at 100, deducts based on violations).
- Downloadable/exportable session reports with full timeline logs.

## 19. Testing Information
Diagnostic and testing scripts are available in the \scripts/\ directory to probe the API endpoints, verify scoring schemas, and test dashboard features.

## 20. Team/Contribution Information
**Raghuram Chimata**
- GitHub: https://github.com/chimataraghuram
- LinkedIn: https://linkedin.com/in/chimataraghuram
- Portfolio: https://chimataraghuram.vercel.app

---
## License
This project is licensed under the [MIT License](LICENSE).
