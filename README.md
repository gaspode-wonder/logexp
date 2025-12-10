# LogExp

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3-lightgrey.svg)
![Postgres](https://img.shields.io/badge/postgres-15-blue.svg)
![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

LogExp is a **Flask + Postgres application** for ingesting and displaying Geiger counter readings. It integrates hardware via USB‑serial, stores readings in a structured database, and exposes both API endpoints and background services for continuous monitoring.

---

## 📂 Project Structure
```
logexp/
├── wsgi.py                  # entrypoint, calls create_app()
├── app/
│   ├── __init__.py          # create_app(), poller lifecycle, error handlers, CLI
│   ├── config.py            # Config class (DB URL, settings)
│   ├── extensions.py        # db, migrate instances
│   ├── poller.py            # GeigerPoller class
│   ├── routes.py            # main UI blueprint (bp = Blueprint("main", __name__))
│   ├── readings.py          # readings API blueprint (bp = Blueprint("readings", __name__))
│   ├── diagnostics.py       # diagnostics blueprint (bp = Blueprint("diagnostics", __name__))
│   ├── docs.py              # docs blueprint (bp = Blueprint("docs", __name__))
│   ├── about.py             # about blueprint (bp = Blueprint("about", __name__))
│   ├── blueprints/
│   │   └── __init__.py      # register_blueprints(app) imports and registers all bp
│   └── templates/
│       ├── base.html        # nav bar with url_for('routes.index'), etc.
│       ├── index.html       # home page
│       ├── about.html       # about page
│       ├── docs.html        # docs page (FAQ, hardware, diagram, sample output)
│       └── errors/
│           ├── 403.html
│           ├── 404.html
│           └── 500.html
```

---

## ⚙️ Features

- **Hardware ingestion**: Reads Geiger counter output via USB‑serial.
- **Background poller**: Threaded service for continuous data collection.
- **API endpoints**:
  - `/readings` → JSON of stored readings.
  - `/geiger/test` → Diagnostic endpoint for port health.
- **Database schema**: Stores counts per second/minute, microsieverts/hour, mode, and timestamp.
- **Timestamp localization**: UTC stored in DB, localized at presentation with GMT reference.
- **CLI commands**:
  - `flask geiger-start` → Start poller manually.
  - `flask geiger-stop` → Stop poller gracefully.
  - `flask geiger-restart` → Restart poller safely.

---
🧩 Blueprints

- main → UI routes (routes.py)
  - / → Home page
  - /poller/status → Poller health check
- readings → API routes (readings.py)
  - /readings → JSON of stored readings
- diagnostics → Hardware diagnostics (diagnostics.py)
  - /geiger/test → Diagnostic endpoint
- docs → Documentation page (docs.py)
  - /docs → Docs page
- about → About page (about.py)
  - /about → About page

All blueprints are registered centrally in `logexp/app/blueprints/__init__.py` and loaded via `register_blueprints(app)` in `create_app()`.
---
## 🚀 Quickstart

### 1. Install dependencies
```bash
pip install -r requirements.txt
```
### 2. Configure environment
```bash
export DATABASE_URL="postgresql://user:password@localhost/logexp_dev"
export LOCAL_TIMEZONE="America/Chicago"
```
### 3. Initialize database
```bash
flask db init
flask db migrate -m "Initial schema"
flask db upgrade
```
### 4. Run the app
```bash
flask run
```
### 5. Control the poller
```bash
flask geiger-start
flask geiger-stop
flask geiger-restart
```
### 6. Test endpoints
- Readings: http://localhost:5000/readings
- Diagnostics: http://localhost:5000/geiger/test
---
## 🗄️ Database & Migrations
LogExp uses Postgres with Flask‑Migrate (Alembic) for schema evolution.
- Generate migration:
    ```bash
    flask db migrate -m "Add new field"
    ```
- Apply migration
    ```bash
    flask db upgrade
    ```
- Reset migrations (if stale versions occur):
    ```sql
    DELETE FROM alembic_version;
    ```
    ```bash
    rm -rf migrations/
    flask db init
    flask db migrate -m "Initial schema"
    flask db upgrade
    ```
---
## 🕒 Timestamp Localization
- Storage: UTC (datetime.now(timezone.utc)).
- Presentation: Localized to configured timezone with GMT reference.
```
2025-12-09T05:30:00-06:00 (2025-12-09T11:30:00+00:00 GMT)
```
## Configuring Local Timezone

Set the `LOCAL_TIMEZONE` environment variable:
```bash
export LOCAL_TIMEZONE="America/New_York"
```
Defaults to `America/Chicago`.
---
📡 Hardware

LogExp integrates with the [MightyOhm Geiger Counter](https://mightyohm.com/blog/products/geiger-counter/).

- USB‑serial interface for easy ingestion
- Outputs counts per minute and microsieverts/hour
- Open hardware design with accessible documentation
---
## 🔄 System Architecture
```mermaid
flowchart TD
    subgraph Hardware
        GC[Geiger Counter]
    end

    subgraph App
        Poller[Background Poller Thread]
        Routes[API Routes]
        Models[SQLAlchemy Models]
    end

    subgraph DB
        Table[logexp_readings Table]
        Alembic[alembic_version Table]
    end

    GC -->|USB-Serial Data| Poller
    Poller --> Models
    Models --> Table
    Routes --> Models
    Alembic --> Table
    Routes -->|JSON Responses| Client[Web UI / API Consumer]
```
---
## 🔁 Reading Lifecycle
```mermaid
sequenceDiagram
    participant GC as Geiger Counter
    participant Poller as GeigerPoller Thread
    participant DB as Postgres (logexp_readings)
    participant API as Flask API (/readings)
    participant Client as Web UI / Consumer

    GC->>Poller: Emit raw data string
    Poller->>Poller: Parse into structured fields
    Poller->>DB: Insert row (UTC timestamp, CPS, CPM, uSv/h, mode)
    Client->>API: GET /readings
    API->>DB: Query latest readings
    DB-->>API: Return rows
    API-->>Client: JSON with localized timestamp (Local + GMT)
```
---
## 📡 Sample JSON Response
```json
[
  {
    "id": 1,
    "timestamp": "2025-12-09T08:30:00-06:00 (2025-12-09T14:30:00+00:00 GMT)",
    "counts_per_second": 42,
    "counts_per_minute": 2520,
    "microsieverts_per_hour": 0.15,
    "mode": "normal"
  },
  {
    "id": 2,
    "timestamp": "2025-12-09T08:31:00-06:00 (2025-12-09T14:31:00+00:00 GMT)",
    "counts_per_second": 45,
    "counts_per_minute": 2700,
    "microsieverts_per_hour": 0.16,
    "mode": "normal"
  }
]
```
---
## 🖥️ CLI Usage
Start the Poller
```bash
flask geiger-start
```
Stop the Poller
```bash
flask geiger-stop
```
Restart the Poller
```bash
flask geiger-restart
```
Database Commands
```bash
flask db migrate -m "Add new field"
flask db upgrade
flask db downgrade
```
---
## 🧰 Troubleshooting
- Stale Alembic revision:
Clear the `alembic_version` table and re‑init migrations.

- Circular imports:
Use `extensions.py` to centralize `db` and `migrate`.

- Poller shutdown error (cannot join current thread):
Add a guard in `stop()` to avoid joining the current thread.

- Timezone issues: Ensure `LOCAL_TIMEZONE` is set correctly in your environment.
---
## 📜 License
MIT License