# Vision and Scope

## Product vision

Build an AI-assisted online examination platform that monitors candidate presence and browser behavior, records evidence, and produces integrity analysis reports for administrators.

## Problem

Remote examinations are difficult to invigilate. Face absence, multiple faces, tab switching, and focus loss are hard to detect without a dedicated monitoring workflow and a durable audit trail.

## Goals

- Authenticate candidates and administrators with role-based access.
- Detect face-related and browser-related integrity events in near real time.
- Persist events, evidence, session lifecycle, and administrator review decisions.
- Provide dashboards, logs, alerts, and exportable integrity reports.

## In scope

- Candidate registration, login, dashboard, and exam workspace
- Admin dashboard, live monitoring, action center, alerts, examinations, and event logs
- OpenCV Haar-cascade face detection
- Integrity scoring and review notes
- Optional LLM assistant (OpenRouter)

## Out of scope (future)

- Full face recognition / identity matching as a primary biometric
- Eye-gaze and head-pose models
- Production email notification service
