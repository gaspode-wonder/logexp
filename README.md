# LogExp

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/flask-2.3-lightgrey.svg)
![Postgres](https://img.shields.io/badge/postgres-15-blue.svg)
![Build](https://img.shields.io/badge/build-passing-brightgreen.svg)
![License](https://img.shields.io/badge/license-MIT-yellow.svg)

# LogExp  
A **Flask + Postgres** application for ingesting, storing, and visualizing Geiger counter readings.  
Includes a background poller, REST API, UI dashboard, and hardware diagnostics.

---

## 🚀 Features

- **USB‑serial ingestion** from supported Geiger counters  
- **Background poller thread** with API + CLI control  
- **REST API** for readings, diagnostics, and poller management  
- **UI dashboard** with charts and tables  
- **Postgres-backed storage** with timezone‑correct UTC timestamps  
- **Flask‑Migrate** for schema evolution  
- **Developer utilities** for seeding, clearing, and resetting the database  

---

## 📦 Project Structure

```
logexp/
├── wsgi.py
├── app/
│   ├── __init__.py          # create_app(), poller lifecycle, CLI
│   ├── config.py            # environment + DB config
│   ├── extensions.py        # db, migrate
│   ├── poller.py            # GeigerPoller thread
│   ├── blueprints/
│   │   ├── routes_ui.py
│   │   ├── readings_api.py
│   │   ├── diagnostics_api.py
│   │   ├── poller_api.py
│   │   └── __init__.py
│   └── templates/
│       ├── base.html
│       ├── index.html
│       ├── readings.html
│       ├── docs.html
│       ├── about.html
│       └── errors/
```

---

## ⚙️ Setup

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure environment
```bash
export DATABASE_URL="postgresql://loginname@localhost:5432/Experiments"
export LOCAL_TIMEZONE="America/Chicago"
export START_POLLER=True
```

### 3. Initialize the database
```bash
flask db upgrade
```

### 4. Run the app
```bash
flask run
```

---

## 📡 API Endpoints

### Readings
- `GET /api/readings.json` — latest readings as JSON

### Poller Control
- `GET /api/poller/status`
- `POST /api/poller/start`
- `POST /api/poller/stop`

### Diagnostics
- `GET /api/geiger/test`

---
## 📄 CSV Export Endpoint

LogExp provides a CSV export endpoint for external analysis, spreadsheets, and debugging.

### **GET /api/readings.csv**

Returns all stored readings in CSV format with the following columns:

```
id,timestamp,counts_per_second,counts_per_minute,microsieverts_per_hour,mode
```

Example usage:

```bash
curl -o readings.csv http://localhost:5000/api/readings.csv
```

This endpoint is useful for:

- importing data into Excel or Google Sheets  
- offline analysis  
- charting in external tools  
- debugging ingestion or timestamp issues  

---

## 🖥️ UI Pages

- `/` — Home  
- `/readings` — Table + chart  
- `/docs` — Documentation  
- `/about` — About  

---

## 🧰 CLI Commands

```bash
flask geiger-start     # Start poller
flask geiger-stop      # Stop poller
flask seed             # Seed DB with sample data
flask clear-db         # Drop + recreate DB
```

---

## 🕒 Timestamp Policy

- All timestamps are stored in **UTC**  
- API emits ISO 8601 with `Z` suffix  
- UI converts to local time (default: America/Chicago)  

This ensures consistent behavior across systems and avoids timezone drift.

---

# 🗄️ Database Reset & Migration Guide

Use this when upgrading Postgres or resetting your environment.

---

## ✅ 1. Verify Flask Is Using the Correct `DATABASE_URL`

```bash
echo $DATABASE_URL
flask shell -c "import os; print(os.getenv('DATABASE_URL'))"
```

---

## ✅ 2. Recreate the Database Cleanly

```bash
dropdb -U loginname Experiments
createdb -U loginname Experiments
```

---

## ✅ 3. Reset Migrations (Optional)

```bash
rm -rf migrations/
flask db init
flask db migrate -m "initial schema for Experiments"
flask db upgrade
```

---

## 🧪 Testing

Example regression test for timestamp correctness:

```python
def test_timestamp_is_utc():
    data = client.get("/api/readings.json").json[0]
    assert data["timestamp"].endswith("Z")
```

---

## 📜 License
MIT License
