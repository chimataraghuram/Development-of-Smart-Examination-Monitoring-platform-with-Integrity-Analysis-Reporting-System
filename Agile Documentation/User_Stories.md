# User Stories

## Candidates

**US-01 — Registration**
As a candidate, I want to register with my details so that I can access assigned examinations.
**Acceptance:** Valid registration stores a hashed password; duplicate email is rejected.

**US-02 — Login**
As a candidate, I want to log in so that I can open my dashboard and exams.
**Acceptance:** Correct credentials create a session; invalid credentials show an error.

**US-03 — Exam workspace**
As a candidate, I want a monitored exam workspace so that I can sit the exam while integrity events are recorded.
**Acceptance:** Start/pause/resume/end are persisted server-side; webcam monitoring can run during an active session.

**US-04 — Notifications**
As a candidate, I want notifications when an exam or review status changes.
**Acceptance:** Review updates create a notification the candidate can mark as read.

## Administrators

**US-05 — Live monitoring**
As an administrator, I want to view live candidate status so that I can respond to integrity risk.
**Acceptance:** Dashboard shows active sessions, scores, and recent events.

**US-06 — Alerts and logs**
As an administrator, I want alerts and filterable event logs with evidence.
**Acceptance:** Face absence, multiple faces, and tab/focus events appear in logs with timestamps.

**US-07 — Examination management**
As an administrator, I want to create, publish, assign, and close examinations.
**Acceptance:** Assigned candidates see the exam; closed exams are no longer startable.

**US-08 — Integrity review**
As an administrator, I want to record a review decision and notes.
**Acceptance:** Decision is stored, visible in history, and notified to the candidate.

**US-09 — AI assistant**
As an administrator, I want an assistant that summarizes logs so that I can triage faster.
**Acceptance:** Assistant uses session context when an API key is configured; it degrades gracefully without a key.
