# Definition of Done

A backlog item is done when all of the following are true:

1. Code is merged to the team `main` branch.
2. Feature works for the intended role (candidate or administrator) with session authentication.
3. API errors return JSON for `/api/` routes (no HTML login redirect for `fetch` clients).
4. New UI copy is readable on the existing dark theme.
5. No secrets (`.env`, API keys, cookies) are committed.
6. README setup steps still start the app with `python app.py`.
7. Relevant Agile status (backlog / sprint backlog) is updated.
