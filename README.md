# LogExp — Radiation Logging & Exploration Platform

LogExp is a radiation logging and visualization platform that integrates a MightyOhm Geiger Counter with a Flask backend, Postgres storage, and a web UI. It supports real‑time polling, analytics, CSV export, diagnostics, and a production‑ready Docker deployment using Gunicorn.

---

## Quickstart (Development Mode)

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure environment

```bash
export SQLALCHEMY_DATABASE_URI=postgresql://logexp:logexp@localhost:5432/logexp
```

### 3. Initialize the database

```bash
flask db upgrade
```

### 4. Run the development server

```bash
flask run
```
---
## Continuous Integration (CI)
LogExp uses GitHub Actions to enforce application correctness on every push and pull request.
The CI pipeline runs:
-    Python 3.11
-    Dependency installation from requirements.txt
-    Full pytest suite
-    Import‑time validation of all modules
-    Deterministic, environment‑clean test execution
The workflow file lives at:
```
.github/workflows/application-ci.yml
```
A green CI run is required before any changes can be merged into `main`.
---
## Branch Protection Rules
The `main` branch is protected to ensure stability and reproducibility:
- ✔️ Require pull request
- ✔️ Require all status checks to pass
- ✔️ Require Application CI
- ✔️ Require branches to be up to date before merging
- ✔️ No direct pushes to main
This ensures that `main` always reflects a deployable, production‑ready state.
---
## Working With Feature Branches
All development must occur on feature branches:
```bash
git checkout -b feature/my-change
```
When ready, open a pull request targeting `main`.
## PR Requirements
- CI must pass
- Code must import cleanly
- Tests must be updated if behavior changes
- No unpinned or implicit dependencies
- No environment‑specific assumptions
Once CI is green and the PR is approved, it can be merged.
---
## Running Tests Locally
Before opening a PR, run the full test suite:
```bash
pytest
```
If your change introduces new dependencies, update:
```
requirements.txt
```
and ensure the tests still pass in a clean environment.
---
## Dependency Management
LogExp uses a **fully pinned, CI‑validated dependency set**:
```
Flask==3.0.0
Flask-Migrate==4.0.5
Flask-SQLAlchemy==3.1.1
matplotlib>=3.7,<3.11
psycopg2-binary==2.9.9
pydantic==2.12.0
python-dotenv==1.0.1
pyserial==3.5
pytest==8.2.1
pytz==2025.2
```
If you add a new import, you must add the corresponding package to `requirements.txt` and verify CI passes.
---
## Local Development Environment
To ensure your environment matches CI:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pytest
```
This mirrors the GitHub Actions environment and prevents “wOrKs On My MaChInE” drift.
---
## Pull Request Checklist
Before submitting a PR:
- [ ] Tests pass locally
- [ ] Dependencies updated (if needed)
- [ ] No stray debug prints or commented code
- [ ] Code follows existing structure and conventions
- [ ] CI passes on GitHub
---
## Why This Matters
LogExp is designed to be:
-    reproducible
-    deterministic
-    safe for collaborators
-    deployable at any time
-    free of environment drift

The CI + branch protection workflow ensures that every contributor (including future you) works within a stable, predictable system.
---
## Production Deployment (Docker + Gunicorn)

LogExp ships with a production‑grade Docker setup:

- Multi‑stage Dockerfile (slim runtime)
- Gunicorn application server (1 worker, thread‑safe for poller)
- Automatic Alembic migrations on startup
- Idempotent database seeding (`flask seed-data`)
- Poller disabled by default inside Docker (`START_POLLER=False`)
- Healthchecks for both Postgres and the Flask app

### Start the full stack

```bash
docker compose up --build
```

### Stop the stack

```bash
docker compose down
```

### Rebuild without cache

```bash
docker compose build --no-cache
```

### View logs

```bash
docker compose logs -f
```

---

## Environment Variables

| Variable | Purpose | Default |
|---------|---------|---------|
| `SQLALCHEMY_DATABASE_URI` | Database connection string | Required |
| `START_POLLER` | Enable hardware poller | `False` in Docker |
| `FLASK_ENV` | Flask environment | `production` |
| `LOCAL_TIMEZONE` | UI timezone | `America/Chicago` |

---

## API Endpoints

### Readings

- `/readings` — Web UI table and chart  
- `/api/readings.json` — JSON readings  
- `/api/readings.csv` — CSV export  

### Poller Control

- `/api/poller/status`  
- `/api/poller/start`  
- `/api/poller/stop`  

### Diagnostics

- `/api/geiger/test`  
- `/api/health` — Application healthcheck  

---

## Poller Lifecycle

The Geiger poller runs as a background thread and reads from a USB‑serial device.

### In development

Poller starts automatically.

### In Docker

Poller is disabled unless explicitly enabled:

```yaml
environment:
  START_POLLER: "True"
```

### Manual control (CLI)

```bash
flask geiger-start
flask geiger-stop
```

---

## Database Migrations and Seeding

### Run migrations manually

```bash
flask db upgrade
```

### Seed the database (idempotent)

```bash
flask seed-data
```

---

## Project Structure

```
logexp/
|-- app/
|   |-- app_blueprints/
|   |-- templates/
|   |-- static/
|   |-- poller.py
|   |-- config.py
|   |-- extensions.py
|   |-- models.py
|   |-- __init__.py
|
|-- seeds/
|   |-- seed_data.py
|
|-- Dockerfile
|-- docker-compose.yml
|-- gunicorn.conf.py
|-- README.md
```


---

## System Overview (ASCII)

```text
   ┌──────────────────────────────┐
   │   MightyOhm Geiger Counter   │
   └───────────────┬──────────────┘
                   │ USB-Serial
                   ▼
        ┌───────────────────────────┐
        │     LogExp Poller Thread  │
        │     (optional in Docker)  │
        └───────────────┬───────────┘
                        │
                        ▼
        ┌───────────────────────────┐
        │      Postgres Database    │
        └───────────────┬───────────┘
                        │
                        ▼
        ┌───────────────────────────┐
        │   Flask API / Gunicorn    │
        └───────────────┬───────────┘
                        │
                        ▼
        ┌───────────────────────────┐
        │      Web UI / Clients     │
        └───────────────────────────┘
```

---

## System Overview (Mermaid)

```mermaid
flowchart TD

    A[MightyOhm Geiger Counter] -->|USB-Serial| B[LogExp Poller Thread]

    B --> C[(Postgres Database)]
    C --> D[Flask API / Gunicorn]
    D --> E[Web UI / Clients]
```

---

## Development vs Production Modes

| Mode | Server | Poller | Database | Notes |
|------|--------|--------|----------|-------|
| Dev | Flask dev server | Enabled | Local Postgres | Hot reload |
| Prod | Gunicorn (Docker) | Disabled by default | Docker Postgres | Auto‑migrations and seeding |

---

## Diagnostics

### Test hardware connection

```bash
curl http://localhost:5000/api/geiger/test
```

### Check poller status

```bash
curl http://localhost:5000/api/poller/status
```

### Check application health

```bash
curl http://localhost:5000/api/health
```

---

## License

MIT License
