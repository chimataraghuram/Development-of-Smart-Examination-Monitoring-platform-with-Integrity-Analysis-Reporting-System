# Sprint Retrospective

## Sprint 4

### What went well

- Role-based dashboards and exam lifecycle are usable end to end.
- Integrity events and evidence give administrators a review trail.
- Optional AI assistant is isolated behind configuration, so local demos still run without a key.

### What to improve

- Keep runtime artifacts (`evidence/`, databases, logs) out of source control going forward.
- Reduce duplicated candidate UI between `dashboard.html` and `exam.html`.
- Add automated tests for scoring and session pause/resume.

### Action items

| Action | Owner | Status |
| --- | --- | --- |
| Standardize team repository layout (Frontend / Backend / Agile Documentation) | Team | Done |
| Document MIT license and setup in README | Team | Done |
| Ignore local logs and cookie dumps | Team | Done |
