# LogExp — Radiation Logging & Exploration Platform

![Pre-commit](https://github.com/gaspode-wonder/logexp/actions/workflows/application-ci.yml/badge.svg?branch=main&event=push)
![CI](https://github.com/gaspode-wonder/logexp/actions/workflows/ci.yml/badge.svg)

LogExp is a radiation logging and visualization platform that integrates a MightyOhm Geiger Counter with a Flask backend, Postgres storage, and a responsive web UI. It supports real‑time polling, analytics, CSV export, diagnostics, and a production‑ready Docker deployment using Gunicorn.

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

- Python 3.11
- Dependency installation from `requirements.txt`
- Full pytest suite
- Import‑time validation of all modules
- Deterministic, environment‑clean test execution

Workflow file:

```
.github/workflows/application-ci.yml
```

A green CI run is required before merging into `main`.

---

## Branch Protection Rules

The `main` branch is protected to ensure stability and reproducibility:

- ✔ Require pull request
- ✔ Require all status checks to pass
- ✔ Require Application CI
- ✔ Require branches to be up to date
- ✔ No direct pushes to `main`

This ensures `main` always reflects a deployable, production‑ready state.

---

## Working With Feature Branches

All development occurs on feature branches:

```bash
git checkout -b feature/my-change
```

### PR Requirements

- CI must pass
- Code must import cleanly
- Tests updated if behavior changes
- No unpinned or implicit dependencies
- No environment‑specific assumptions

Once CI is green and the PR is approved, it can be merged.

---

## Running Tests Locally

```bash
pytest
```

If you add a new dependency, update:

```
requirements.txt
```

and ensure tests still pass in a clean environment.

---

## Dependency Management

LogExp uses a **fully pinned, CI‑validated dependency set**:

```
Flask==3.0.0
Flask-Migrate==4.1.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
matplotlib==3.10.8
psycopg2-binary==2.9.9
pydantic==2.12.5
python-dotenv==1.0.1
pyserial==3.5
pytest==8.2.1
pytz==2025.2
```

If you add a new import, add the corresponding package and verify CI passes.

---

## Local Development Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pytest
```

This mirrors CI and prevents environment drift.

---

## Pull Request Checklist

- [ ] Tests pass locally
- [ ] Dependencies updated (if needed)
- [ ] No stray debug prints or commented code
- [ ] Code follows existing structure and conventions
- [ ] CI passes on GitHub

---

## Production Deployment (Docker + Gunicorn)

LogExp ships with a production‑grade Docker setup:

- Multi‑stage Dockerfile (slim runtime)
- Gunicorn application server
- Automatic Alembic migrations
- Idempotent database seeding (`flask seed-data`)
- Poller disabled by default (`START_POLLER=False`)
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
| `START_POLLER` | Enable hardware poller | `False` |
| `FLASK_ENV` | Flask environment | `production` |
| `LOCAL_TIMEZONE` | UI timezone | `America/Chicago` |

---

## API Endpoints

### Readings

- `/readings` — Web UI
- `/api/readings.json` — JSON
- `/api/readings.csv` — CSV export

### Poller Control

- `/api/poller/status`
- `/api/poller/start`
- `/api/poller/stop`

### Diagnostics

- `/api/geiger/test`
- `/api/health` — Healthcheck

---

## Poller Lifecycle

The Geiger poller runs as a background thread reading from a USB‑serial device.

### Development

Poller starts automatically.

### Docker

Poller is disabled unless explicitly enabled:

```yaml
environment:
  START_POLLER: "True"
```

### CLI Control

```bash
flask geiger-start
flask geiger-stop
```

---

## Database Migrations and Seeding

### Apply migrations

```bash
flask db upgrade
```

### Seed database (idempotent)

```bash
flask seed-data
```

---

## Project Structure

```
logexp/
│
├── app/
│   ├── app_blueprints/        # Flask blueprints (UI, API, diagnostics)
│   ├── templates/             # Jinja2 templates
│   ├── static/                # CSS, JS, images
│   ├── config.py              # Config + env var parsing
│   ├── extensions.py          # SQLAlchemy, Migrate, LoginManager
│   ├── models.py              # SQLAlchemy models
│   ├── poller.py              # Geiger poller thread
│   ├── services/              # DB analytics, telemetry, helpers
│   ├── __init__.py            # create_app()
│   └── wsgi.py                # WSGI entrypoint for Gunicorn
│
├── analytics/
│   ├── engine.py              # Pure analytics engine (deterministic, DB‑free)
│   └── types.py               # ReadingSample, Batch types
│
├── seeds/
│   └── seed_data.py           # Idempotent database seeding
│
├── migrations/                # Alembic migrations
│
├── docker/                    # Entrypoint scripts, compose variants
│   └── entrypoint.sh
│
├── tests/                     # Full pytest suite
│
├── docker-compose.yml         # Default compose (Linux/macOS)
├── docker-compose.pi.yml      # Raspberry Pi deployment (KEEP‑0001)
├── docker-compose.mac.yml     # macOS developer stack
├── docker-compose.linux.yml   # Linux host stack
│
├── Dockerfile                 # Multi‑stage production build
├── gunicorn.conf.py           # Gunicorn configuration
├── pyproject.toml             # Package metadata + editable install
├── requirements.txt           # Dev/test dependencies
├── docker-requirements.txt    # Runtime-only dependencies
└── README.md
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
| Prod | Gunicorn (Docker) | Disabled by default | Docker Postgres | Auto‑migrations + seeding |

---

## Diagnostics

### Hardware test

```bash
curl http://localhost:5000/api/geiger/test
```

### Poller status

```bash
curl http://localhost:5000/api/poller/status
```

### Healthcheck

```bash
curl http://localhost:5000/api/health
```

---

## Analytics Architecture

LogExp contains two analytics layers:

1. **Pure Analytics Engine** (`logexp.analytics.engine`)
   - deterministic
   - in‑memory
   - DB‑free
   - future ingestion/control‑plane foundation

2. **Legacy DB Analytics** (`logexp.app.services.analytics`)
   - SQLAlchemy queries
   - transitional compatibility layer

These layers must remain separate.

### Fixture Boundaries

- DB analytics tests → `reading_factory`
- Pure engine tests → `make_reading`, `make_batch`

### Do Not Merge These Worlds

- Do not feed DB models into the pure engine
- Do not feed `ReadingSample` into DB analytics
- Do not collapse the two layers

The pure engine is the future.

---

## Runtime Contract

### 1. Database Backend

- **Postgres 18** is canonical
- **SQLite** is test‑only

### 2. Required Environment Variables

| Variable | Description |
|---------|-------------|
| `SQLALCHEMY_DATABASE_URI` | Postgres connection string |
| `LOCAL_TIMEZONE` | Local timezone |

### 3. Optional Environment Variables

| Variable | Type | Purpose |
|----------|------|---------|
| `GEIGER_THRESHOLD` | float | Diagnostics threshold |
| `START_POLLER` | bool | Enable/disable poller |
| `LOGEXP_NODE_ID` | str | Node identifier |
| `TELEMETRY_ENABLED` | bool | Telemetry toggle |
| `TELEMETRY_INTERVAL_SECONDS` | int | Telemetry interval |

### 4. Containerized Startup

CI guarantees:

- Docker image builds
- `create_app()` boots
- Env vars parsed correctly
- No SQLite fallback in container

### 5. Migrations

- SQLite migrations validated via pytest
- Postgres migrations validated via CI
- Alembic env exercised under Postgres 18

### 6. Deterministic Config Layering

1. Defaults
2. Environment variables
3. Explicit overrides

---

## License

MIT License
