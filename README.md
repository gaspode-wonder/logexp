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
