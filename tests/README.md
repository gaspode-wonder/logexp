# Test Architecture

## Fresh App Per Test

All tests use a function-scoped `test_app` fixture that creates a brand-new
Flask application, config_obj, and in-memory SQLite database for each test.

This ensures:

- no cross-test contamination
- deterministic ingestion behavior
- reliable monkeypatching of SQLAlchemy session methods
- reproducible CI runs

### Key Guarantees

- `db.create_all()` and `db.drop_all()` run for every test
- `db.session.remove()` clears the scoped_session registry
- `config_obj` is rebuilt from defaults for each test
- ingestion tests never need to manually reset `INGESTION_ENABLED`

### Why This Matters

Flask-SQLAlchemy uses a scoped_session proxy that can leak state across tests
unless the app and session are recreated per test. This fixture pattern prevents
that entire class of bugs.

## Environment Variables

LogExp reads configuration from environment variables using a deterministic defaults → environment → overrides model.

Copy `.env.example` to `.env` to get started:

```bash
cp .env.example .env
```

### Required Variables

| Variable | Description |
|---------|-------------|
| `DATABASE_URL` | SQLAlchemy connection string. Required for Postgres. |
| `LOCAL_TIMEZONE` | UI-facing timezone (e.g., America/Chicago). |

### Analytics

| Variable | Default | Description |
|----------|---------|-------------|
| `ANALYTICS_ENABLED` | `true` | Enables rolling-window analytics. |
| `ANALYTICS_WINDOW_SECONDS` | `60` | Window size in seconds. |

### Ingestion

| Variable | Default | Description |
|----------|---------|-------------|
| `INGESTION_ENABLED` | `true` | Enables ingestion pipeline. |
| `INGESTION_BATCH_SIZE` | `100` | Batch size for DB writes. |

### Poller (Hardware)

| Variable | Default | Description |
|----------|---------|-------------|
| `START_POLLER` | `false` | Whether to start the Geiger poller. |
| `GEIGER_PORT` | `/dev/tty.usbserial-AB9R9IYS` | Serial device path. |
| `GEIGER_BAUDRATE` | `9600` | Baudrate for serial device. |
| `GEIGER_THRESHOLD` | `0.1` | Noise threshold. |

All variables are optional; missing values fall back to defaults defined in `logexp/app/config/defaults.py`.

## Configuration Keys

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| DATABASE_URL | string | sqlite:///logexp.db | SQLAlchemy connection string. |
| LOCAL_TIMEZONE | string | UTC | UI-facing timezone. |
| ANALYTICS_ENABLED | bool | true | Enables analytics engine. |
| ANALYTICS_WINDOW_SECONDS | int | 60 | Rolling window size. |
| INGESTION_ENABLED | bool | true | Enables ingestion pipeline. |
| INGESTION_BATCH_SIZE | int | 100 | Batch size for ingestion. |
| START_POLLER | bool | false | Whether to start Geiger poller. |
| GEIGER_PORT | string | /dev/tty.usbserial-AB9R9IYS | Serial device path. |
| GEIGER_BAUDRATE | int | 9600 | Serial baudrate. |
| GEIGER_THRESHOLD | float | 0.1 | Noise threshold. |
