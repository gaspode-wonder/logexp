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
├── wsgi.py                     # entrypoint, calls create_app()
├── app/
│   ├── init.py                 # create_app(), poller lifecycle, error handlers, CLI
│   ├── config.py               # Config class (DB URL, settings)
│   ├── extensions.py           # db, migrate instances
│   ├── poller.py               # GeigerPoller class
│   ├── blueprints/
│   │   ├── routes_ui.py        # UI routes (home, readings, docs, about)
│   │   ├── readings_api.py     # API routes for readings JSON
│   │   ├── diagnostics_api.py  # hardware diagnostics
│   │   ├── poller_api.py       # poller control endpoints
│   │   └── init.py             # register_blueprints(app)
│   └── templates/
│       ├── base.html           # nav bar
│       ├── index.html          # home page
│       ├── readings.html       # readings page (table + chart)
│       ├── docs.html           # docs page
│       ├── about.html          # about page
│       └── errors/
│           ├── 403.html
│           ├── 404.html
│           └── 500.html
```

---

## ⚙️ Features

- **Hardware ingestion**: Reads Geiger counter output via USB‑serial.
- **Background poller**: Threaded service for continuous data collection.  
  - Starts automatically when the app launches (unless disabled with `START_POLLER=False`).  
  - Runs until explicitly stopped via API or CLI.
- **API endpoints**:
  - `/api/readings.json` → JSON of stored readings
  - `/api/poller/status` → Poller health check
  - `/api/poller/start` → Start poller
  - `/api/poller/stop` → Stop poller
  - `/api/geiger/test` → Diagnostic endpoint
- **UI endpoints**:
  - `/` → Home page
  - `/readings` → Readings page (table + chart)
  - `/docs` → Documentation page
  - `/about` → About page
- **Database schema**: Stores counts per second/minute, microsieverts/hour, mode, and timestamp.
- **Timestamp localization**: UTC stored in DB, displayed in `America/Chicago` timezone with 24‑hour clock.
- **CLI commands**:
  - `flask geiger-start` → Start poller manually
  - `flask geiger-stop` → Stop poller gracefully
  - `flask seed` → Seed database with sample data
  - `flask clear-db` → Drop and recreate database

---
## 🧩 Blueprints

- **routes_ui** → UI pages
  - `/` → Home page
  - `/readings` → Readings page (table + chart)
  - `/docs` → Documentation page
  - `/about` → About page

- **readings_api** → Readings JSON
  - `/api/readings.json` → JSON of stored readings

- **poller_api** → Poller control
  - `/api/poller/status` → Poller health check
  - `/api/poller/start` → Start poller
  - `/api/poller/stop` → Stop poller

- **diagnostics_api** → Hardware diagnostics
  - `/api/geiger/test` → Diagnostic endpoint

- **docs_ui** → Documentation page
  - `/docs` → Docs page

- **about_ui** → About page
  - `/about` → About page

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
```
### 6. Test endpoints
- UI Readings: http://localhost:5000/readings
- API Readings JSON: http://localhost:5000/api/readings.json
- Poller Status: http://localhost:5000/api/poller/status
- Diagnostics: http://localhost:5000/api/geiger/test
---
🗄️ Database & Migrations

LogExp uses Postgres with Flask‑Migrate (Alembic) for schema evolution.

- Generate migration
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
🕒 Timestamp Localization
- Storage: UTC (`datetime.now(timezone.utc)`)
- Presentation: Localized to configured timezone (`America/Chicago` by default) with 24‑hour clock.
---
🔄 System Architecture
```mermaid
flowchart TD
    subgraph Hardware
        GC[Geiger Counter]
    end

    subgraph App
        Poller[Background Poller Thread]
        Routes[UI + API Blueprints]
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
    Routes -->|JSON + HTML| Client[Web UI / API Consumer]
```
---
🔁 Reading Lifecycle
```mermaid
sequenceDiagram
    participant GC as Geiger Counter
    participant Poller as GeigerPoller Thread
    participant DB as Postgres (logexp_readings)
    participant API as Flask API (/api/readings.json)
    participant Client as Web UI / Consumer

    GC->>Poller: Emit raw data string
    Poller->>Poller: Parse into structured fields
    Poller->>DB: Insert row (UTC timestamp, CPS, CPM, uSv/h, mode)
    Client->>API: GET /api/readings.json
    API->>DB: Query latest readings
    DB-->>API: Return rows
    API-->>Client: JSON with localized timestamp
```
---
📡 Sample JSON Response
```json
[
  {
    "id": 1,
    "timestamp": "2025-12-09T17:30:00Z",
    "counts_per_second": 0.7,
    "counts_per_minute": 42,
    "microsieverts_per_hour": 0.12,
    "mode": "normal"
  },
  {
    "id": 2,
    "timestamp": "2025-12-09T17:31:00Z",
    "counts_per_second": 0.8,
    "counts_per_minute": 47,
    "microsieverts_per_hour": 0.14,
    "mode": "normal"
  }
]
```
---
🖥️ CLI Usage
Start the poller:
```bash
flask geiger-start
```

Stop the poller
```bash
flask geiger-stop
```
Seed the database
```bash
flask seed
```
Clear and recreate database:
```bash
flask clear-db
```
Database commands
```bash
flask db migrate -m "Add new field"
flask db upgrade
flask db downgrade
```
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