# Configuration System

LogExp uses a **two‑layer configuration model** designed for deterministic behavior across development, CI, and production:

1. **`app.config_obj`** — canonical, typed, validated configuration  
2. **`app.config`** — Flask’s runtime configuration dictionary  

This architecture ensures that internal subsystems (analytics, ingestion, logging, poller control) receive stable, typed configuration values, while Flask extensions continue to operate using the framework’s expected configuration interface.

## Layer 1: Canonical Configuration (`app.config_obj`)

`config_obj` is produced by `load_config()` using a deterministic layering strategy:

1. **Defaults** (from `DEFAULTS`)  
2. **Environment variables** (typed via `ENV_MAP`)  
3. **Explicit overrides** (tests, CI, local dev)

This layer provides:

- Typed values  
- Schema stability  
- Predictable override behavior  
- Isolation from Flask’s implicit defaults  
- A clean separation between application config and framework config  

Internal subsystems should read from this layer.

## Layer 2: Flask Runtime Configuration (`app.config`)

Flask extensions and some third‑party integrations expect configuration to be present in `app.config`. To support this, the application factory mirrors the canonical configuration:

```
app.config.update(app.config_obj)
```

This ensures:

- SQLAlchemy receives the correct database URI  
- Flask’s built‑in behaviors (e.g., `TESTING`, `SECRET_KEY`) work as expected  
- Analytics and ingestion subsystems can read from either layer  
- Tests that rely on `app.config` continue to function  

## Why Two Layers?

Relying solely on `app.config` introduces several issues:

- All values are strings  
- No schema enforcement  
- Implicit environment variable merging  
- Extensions may mutate config  
- Deterministic testing becomes difficult  

By contrast, `config_obj` provides:

- Typed, validated configuration  
- Explicit layering  
- Predictable behavior across environments  

The mirroring step preserves compatibility without sacrificing determinism.

## Usage Guidelines

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

Overrides apply to both layers automatically.

## Summary

LogExp maintains two configuration layers by design:

- **`config_obj`** for deterministic, typed, schema‑driven application behavior  
- **`app.config`** for Flask compatibility  

This hybrid model provides the reliability of a modern configuration system while preserving full compatibility with Flask and its extensions.


                          +----------------------+
                          |      DEFAULTS        |
                          |  (single source of   |
                          |        truth)        |
                          +----------+-----------+
                                     |
                                     v
                          +----------------------+
                          |  ENVIRONMENT VARS    |
                          |   (typed via ENV_MAP)|
                          +----------+-----------+
                                     |
                                     v
                          +----------------------+
                          |     OVERRIDES        |
                          | (tests, CI, dev)     |
                          +----------+-----------+
                                     |
                                     v
                     +----------------------------------+
                     |        load_config()             |
                     |  produces canonical config_obj   |
                     +----------------+-----------------+
                                      |
                                      v
                     +----------------------------------+
                     |     app.config_obj (canonical)   |
                     +----------------+-----------------+
                                      |
                                      v
                     +----------------------------------+
                     |     app.config.update(...)       |
                     |  (mirror into Flask config)      |
                     +----------------+-----------------+
                                      |
                                      v
                     +----------------------------------+
                     |     app.config (Flask runtime)   |
                     +----------------------------------+

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

# Configuration Troubleshooting Guide

## Symptom: Analytics always returns None

**Cause:** `ANALYTICS_ENABLED` override not applied to Flask config.  
**Fix:** Ensure the application factory mirrors canonical config:

```
app.config.update(app.config_obj)
```

## Symptom: Tests ignore override values

**Cause:** Overrides passed to `create_app()` do not match schema keys.  
**Fix:** Use exact keys from `DEFAULTS` (case‑sensitive).

## Symptom: Environment variables not taking effect

**Cause:** Missing or incorrect entry in `ENV_MAP`.  
**Fix:** Add or correct the mapping:

```
"ANALYTICS_ENABLED": ("ANALYTICS_ENABLED", lambda v: v.lower() == "true")
```

## Symptom: Flask extensions behave inconsistently

**Cause:** Extension reads from `app.config`, but value only exists in `config_obj`.  
**Fix:** Confirm `app.config.update(app.config_obj)` is present.

## Symptom: Local timezone incorrect

**Cause:** `LOCAL_TIMEZONE` override not applied or environment variable missing.  
**Fix:** Set override explicitly in `create_app()` or export `LOCAL_TIMEZONE`.

## Symptom: SQLAlchemy engine not using timezone support

**Cause:** `configure_sqlite_timezone_support()` must run before `db.init_app()`.  
**Fix:** Ensure ordering in `create_app()` matches the documented sequence.
