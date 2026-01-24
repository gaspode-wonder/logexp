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

# Configuration Architecture (Two‑Layer Model)

LogExp uses a **two‑layer configuration model**:

1. **`app.config_obj`** — the canonical, typed, validated configuration  
2. **`app.config`** — Flask’s runtime configuration dictionary  

This structure is intentional and exists to support deterministic behavior across development, CI, and production.

## Why Two Layers?

### 1. Canonical Configuration (`app.config_obj`)

`config_obj` is the single source of truth for all application settings. It is produced by the `load_config()` function, which applies configuration in a deterministic order:

1. **Defaults** (defined in `DEFAULTS`)  
2. **Environment variables** (typed via `ENV_MAP`)  
3. **Explicit overrides** (tests, CI, local dev)

This layer provides:

- Typed values  
- Schema stability  
- Predictable override behavior  
- Isolation from Flask’s implicit defaults  
- A clean separation between *application* config and *framework* config  

All internal subsystems (analytics, ingestion, logging, poller control) are designed to read from this canonical layer.

### 2. Flask Runtime Configuration (`app.config`)

Flask extensions and some third‑party integrations expect configuration to be present in `app.config`. To support this, the application factory mirrors the canonical configuration into Flask’s config:

```
app.config.update(app.config_obj)
```

This ensures:

- SQLAlchemy receives the correct database URI  
- Flask’s built‑in behaviors (e.g., `TESTING`, `SECRET_KEY`) work as expected  
- Analytics and ingestion subsystems can read from either layer  
- Tests that rely on `app.config` continue to function  

This mirroring step is deliberate and required for compatibility with Flask’s extension ecosystem.

## Rationale

This architecture avoids the pitfalls of relying solely on `app.config`, which:

- stores everything as strings  
- does not enforce types  
- merges environment variables implicitly  
- has no schema  
- can be mutated by extensions  
- makes deterministic testing difficult  

By contrast, `app.config_obj` provides:

- a stable, typed, validated configuration  
- explicit layering  
- predictable behavior across environments  
- a clean contract for internal subsystems  

The mirroring step (`app.config.update(app.config_obj)`) ensures compatibility without sacrificing determinism.

## How to Use These Layers

### Internal application code  
Use:

```
current_app.config_obj["ANALYTICS_ENABLED"]
```

### Flask extensions  
Use:

```
current_app.config["SQLALCHEMY_DATABASE_URI"]
```

### Tests  
Override configuration via the application factory:

```
create_app({
    "ANALYTICS_ENABLED": True,
    "ANALYTICS_WINDOW_SECONDS": 60,
})
```

The override is applied to both layers automatically.

## Summary

LogExp maintains two configuration layers by design:

- **`config_obj`** for deterministic, typed, schema‑driven application behavior  
- **`app.config`** for Flask compatibility  

This hybrid model provides the reliability of a modern configuration system while preserving full compatibility with Flask and its extensions.

# Configuration Quickstart

Welcome to LogExp! Here’s the fast path to understanding how configuration works.

## Where configuration comes from

LogExp builds configuration in three deterministic layers:

1. **Defaults** (`DEFAULTS`)
2. **Environment variables** (typed via `ENV_MAP`)
3. **Overrides** (tests, CI, local dev)

These layers are merged by `load_config()` into a canonical configuration dictionary.

## Two configuration layers

- **`app.config_obj`** — canonical, typed, validated  
- **`app.config`** — Flask’s runtime config (mirrored from `config_obj`)

Most internal code should read from `config_obj`.  
Flask extensions read from `app.config`.

## Overriding configuration in tests

```
app = create_app({
    "ANALYTICS_ENABLED": True,
    "ANALYTICS_WINDOW_SECONDS": 120,
})
```

Overrides apply to both layers automatically.

## When in doubt

- Internal subsystems → `config_obj`  
- Flask extensions → `app.config`  
- Tests → pass overrides to `create_app()`  
