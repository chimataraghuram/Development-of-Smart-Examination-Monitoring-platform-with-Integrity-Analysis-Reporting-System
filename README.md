# Smart Examination Monitoring Platform with Integrity Analysis Reporting System

An AI-powered online exam monitoring system. The platform monitors candidates during online examinations using computer vision, browser-event logging, integrity scoring, and administrator reporting.

---

## Features

- Candidate registration, login, and exam workspace
- Administrator dashboard, live monitoring, alerts, and event logs
- OpenCV Haar-cascade face detection (presence / absence / multiple faces)
- Tab switching and browser focus-loss tracking
- Server-authoritative start, pause, resume, and end session lifecycle
- Integrity scoring, review decisions, and student notifications
- Optional context-aware AI assistant (OpenRouter)
- SQLite persistence and report export

---

## Technologies

- Python (Flask)
- SQLite
- OpenCV (Haar Cascade Classifier)
- Scikit-Image
- HTML / CSS / JavaScript
- OpenRouter API (optional AI assistant)

---

## Repository structure

```text
Team GitHub Repository
│
├── Frontend/
│   └── Complete frontend source code (templates, static assets)
│
├── Backend/
│   └── Complete backend source code (Flask app, database, scoring, AI, exports)
│
├── Agile Documentation/
│   └── Required Agile documents
│
├── LICENSE
│   └── MIT License
│
├── README.md
│   └── Project information + setup/run instructions
│
└── Other required project files
    ├── app.py                 # Run from the repository root
    ├── requirements.txt
    ├── .env.example
    ├── run_local.ps1
    └── scripts/               # Diagnostic helpers
```

---

## Installation

Clone the repository:

```bash
git clone https://github.com/chimataraghuram/Development-of-Smart-Examination-Monitoring-platform-with-Integrity-Analysis-Reporting-System.git
```

Move into the project directory:

```bash
cd Development-of-Smart-Examination-Monitoring-platform-with-Integrity-Analysis-Reporting-System
```

Create a virtual environment (recommended) and install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

On macOS or Linux, activate with `source .venv/bin/activate`.

Set up environment variables:

1. Copy `.env.example` to `.env`.
2. Set a long random `FLASK_SECRET_KEY`.
3. Add `OPENROUTER_API_KEY` only if you want the AI assistant.

The local administrator account uses the email `admin@gmail.com`. Set `ADMIN_DEFAULT_PASSWORD` in `.env` to a strong private value before first use; never commit that value or the resulting `.env` file.

---

## Run the project

From the repository root:

```bash
python app.py
```

The application listens on `http://127.0.0.1:5000/`.

On Windows, `run_local.ps1` stops a stale local server and starts the app with the project virtual environment.

## Database setup

The application uses SQLite. On startup, it creates or migrates `Backend/exam_monitor.db` and seeds the local administrator account from `ADMIN_DEFAULT_PASSWORD`. The database file is intentionally ignored by Git because it contains local runtime data.

## How to use the system

Candidates register or sign in, review assigned examinations, complete the readiness checks, start an exam, and keep the monitoring workspace active until submission. During an active session, browser and face-monitoring events are recorded and reflected in the activity, statistics, and report views.

Administrators sign in through the same authentication flow and use the dashboard to review active sessions, alerts, event logs, examinations, integrity reports, review decisions, exports, and the optional AI assistant. The AI assistant requires `OPENROUTER_API_KEY`; without it, the application remains usable and reports that the assistant is unavailable.

---

## Current modules

- Candidate registration and login
- Admin dashboard and live analytics
- Browser tab and focus monitoring
- Photo / evidence capture
- Face detection (OpenCV)
- Integrity scoring
- Event logging and timeline
- Session management with pause / resume
- Examination creation, publishing, and candidate assignment
- Integrity review workflow
- Student notifications
- SQLite database
- Optional AI chatbot assistant

---

## License

This project is licensed under the [MIT License](LICENSE).

---

## Team

**Raghuram Chimata**

- GitHub: https://github.com/chimataraghuram
- LinkedIn: https://linkedin.com/in/chimataraghuram
- Portfolio: https://chimataraghuram.vercel.app
