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
### Timezone Handling

LogExp normalizes all timestamps to **UTC** before storing and emitting them.

- **Backend:**
  - `LogExpReading.timestamp` is defined with `db.DateTime(timezone=True)`.
  - Default uses `datetime.now().astimezone(timezone.utc)` to convert the system’s local clock (often Central) into true UTC.
  - JSON serialization (`to_dict`) always emits ISO 8601 with `Z` suffix (e.g. `"2025-12-12T16:53:42Z"`).

- **Frontend:**
  - The browser parses UTC (`Z`) and converts to the user’s local timezone automatically.
  - For consistent Central display, use:
    ```js
    new Date(tsString).toLocaleString("en-US", { timeZone: "America/Chicago" });
    ```

**Important:** Do not stamp rows with local timezones. Always store UTC in the database and emit UTC in the API.

📘 Developer Docs 

## Timestamp and Timezone Policy

LogExp enforces UTC for all readings:

- **Creation:**
  Readings are stamped with `datetime.now().astimezone(timezone.utc)` to ensure correct conversion from the system’s local clock (Central) into UTC.

- **Database:**
  `db.DateTime(timezone=True)` preserves tzinfo. This prevents naive datetimes from being mislabeled as UTC.

- **Serialization:**
  `to_dict()` emits ISO 8601 strings with `Z` (UTC). Example:
  ```json
  {
    "id": 42,
    "timestamp": "2025-12-12T16:53:42Z",
    "counts_per_minute": 123
  }

- Frontend:
The browser converts UTC into local time. If you want to force Central display regardless of client location:
```javascript
new Date(tsString).toLocaleString("en-US", { timeZone: "America/Chicago" });
```

Why UTC?

Storing UTC avoids ambiguity and ensures consistent behavior across servers, clients, and collaborators in different time zones.

---

## 🧪 Regression Test (pytest style)

Add this to your test suite to catch any future regressions:

```python
from datetime import datetime, timezone
from logexp.app.models import LogExpReading

def test_timestamp_serialization_is_utc():
    # Simulate a reading created at local Central time
    local = datetime(2025, 12, 12, 10, 30).astimezone()  # 10:30 CST
    reading = LogExpReading(
        timestamp=local.astimezone(timezone.utc),
        counts_per_second=1,
        counts_per_minute=60,
        microsieverts_per_hour=0.1,
        mode="test"
    )
    data = reading.to_dict()
    # JSON should show UTC (16:30Z)
    assert data["timestamp"].endswith("16:30:00Z")
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

## 🛠 Troubleshooting Timezone Issues
Symptom

    JSON shows timestamps like "2025-12-12T10:53:42Z".

    Frontend chart displays values six hours behind (e.g. 04:53 CST instead of 10:53 CST).

Root Cause

The backend was stamping local Central time and then labeling it as UTC (Z). This happened because datetime.now(timezone.utc) was used while the system clock was set to Central. That call does not convert local time into UTC — it simply tags the local wall‑clock with a UTC tzinfo.

Fix

    Use datetime.now().astimezone(timezone.utc) everywhere a timestamp is created. This converts the system’s local time into the correct UTC instant.

    Ensure the model column is defined with db.DateTime(timezone=True) so tzinfo is preserved.

    JSON serialization should always emit UTC with Z.

Verification

At 10:30 CST:

    Backend should store 2025‑12‑12 16:30:00+00:00.

    API should emit "2025-12-12T16:30:00Z".

    Browser should display 10:30 CST.

Regression Test
```python
def test_timestamp_serialization_is_utc():
    local = datetime(2025, 12, 12, 10, 30).astimezone()  # 10:30 CST
    reading = LogExpReading(timestamp=local.astimezone(timezone.utc), ...)
    data = reading.to_dict()
    assert data["timestamp"].endswith("16:30:00Z")
```

This way, anyone who sees the “six‑hour offset” bug will immediately know: the backend is mislabeling local time as UTC.

---
## 📜 License
MIT License