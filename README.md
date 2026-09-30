# FitLog

A lightweight workout and nutrition journal built with Python, FastAPI, SQLAlchemy, and plain JavaScript. A personal learning project focused on understanding a complete browser → API → database workflow.

![FitLog journal with example food and workout entries](docs/screenshot.png)

## What works

- Create an account, sign in, and sign out with a revocable cookie session.
- Log exercises with sets, reps per set, and weight in pounds.
- Manually log food portions with calories, protein, carbohydrates, and fat.
- See daily nutrition totals against editable goals.
- Select a date to review or add past entries.
- Remove incorrect entries and log replacements.
- Keep each account's entries private from other accounts.
- Use a responsive interface without a frontend framework or build step.

A workout row represents sets performed at the same weight and repetition count. Log separate rows when these differ. Food values are the totals for the portion consumed, not per 100 g. Default nutrition goals are editable placeholders, not personalized recommendations.

## Run locally

Requires Python 3.12. Run these commands from the repository root:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m uvicorn Backend.main:app --reload
```

Open **http://127.0.0.1:8000** and create an account. The frontend is served by FastAPI; do not open the HTML file directly. SQLite creates `fitlog.db` automatically at the repository root and keeps entries after restarting the server. This file is ignored by Git.

Interactive API documentation: **http://127.0.0.1:8000/docs** (loads its documentation UI from a CDN). The raw API schema is available offline at **http://127.0.0.1:8000/openapi.json**.

`requirements.txt` lists runtime dependencies; `requirements-dev.txt` adds testing tools. `requirements-lock.txt` records every installed version used for verification.

## Test

```sh
python -m pytest -q
```

The tests use disposable databases in pytest's temporary directory. They cover account creation, login/logout, password hashing, session expiry, account isolation, food and workout persistence, daily totals, goals, validation, static files, and compatibility with the original bcrypt account hashes. An optional GitHub Actions template in `docs/github-actions-tests.yml` runs the suite and checks JavaScript syntax. To enable it, copy it to `.github/workflows/tests.yml` and commit using GitHub credentials with workflow permission. The current publishing token cannot create workflows, so CI is not enabled automatically.

## How it fits together

```text
Frontend/index.html  →  Frontend/app.js  →  Backend/main.py
   Forms and UI         fetch + render      HTTP routes
                                             ↓
                                    schemas.py validates
                                    auth.py identifies user
                                             ↓
                                    models.py + database.py
                                             ↓
                                      SQLite / PostgreSQL
```

| File | Responsibility |
| --- | --- |
| `Backend/main.py` | API routes, startup, security headers, frontend serving |
| `Backend/schemas.py` | Validate incoming data and define safe responses |
| `Backend/models.py` | Database tables and columns |
| `Backend/database.py` | Database engine and per-request sessions |
| `Backend/auth.py` | Password hashing and cookie sessions |
| `Frontend/index.html` | Accessible forms and page structure |
| `Frontend/style.css` | Layout, styling, responsive breakpoints |
| `Frontend/app.js` | Form handling, API calls, safe DOM updates |
| `tests/test_api.py` | API integration tests with an isolated database |

**Start learning with [the code walkthrough](docs/LEARNING.md).** It explains the changed code in source order and follows one complete request.

## Optional PostgreSQL

The default SQLite setup is enough for local use. To connect to PostgreSQL:

```sh
python -m pip install 'psycopg[binary]>=3.2,<4'
export DATABASE_URL='postgresql+psycopg://YOUR_USER:YOUR_PASSWORD@localhost/fitlog'
python -m uvicorn Backend.main:app --reload
```

Create the `fitlog` database first. Environment variables are read from your shell; `.env.example` documents them, but `.env` files are not loaded automatically. Do not commit credentials. Switching databases does not copy existing data. The original prototype's PostgreSQL users table is preserved; older bcrypt accounts can sign in, and receive default goals on first login.

## Scope and tradeoffs

This is a local learning MVP. It does not include password reset, email verification, public-deployment rate limiting, database migrations, food search, barcode scanning, body-weight charts, or a mobile app. Accounts are case-sensitive by username; email is normalized to lowercase. Sessions expire after seven days. Goals apply to all dates, including history.

Passwords use salted PBKDF2-HMAC-SHA256; session tokens are random, stored hashed in the database, and sent in HttpOnly/SameSite=Strict cookies. Each data route checks the logged-in user. Before internet hosting, configure HTTPS with `COOKIE_SECURE=true`, add login rate limiting and account recovery, and introduce reviewed migrations and backups. `create_all()` creates missing tables but does not migrate existing columns.

Publishing the source to GitHub does not host the running Python application. GitHub Pages cannot run this backend.
