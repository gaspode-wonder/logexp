# CONFIGURATION
LogExp uses a centralized, deterministic configuration system designed for clarity, reproducibility, and onboarding ease. All configuration values flow through a single loader:
```
from logexp.app.config import load_config
config = load_config()
```
This document describes every configuration key, its default value, type, and override mechanisms for development, testing, and production.

---
## 1. Design Goals
The configuration system is built around four principles:
### 1. Single Source of Truth
All config values originate from:
-    defaults.py (canonical defaults)
-    environment variables (optional)
-    explicit overrides (tests, scripts)

### 2. Deterministic Behavior
The application behaves identically across:
-    macOS
-    Linux
-    Docker
-    CI
-    production

### 3. Test‑Friendly
Tests override config via:
```
load_config(overrides={...})
```
No environment hacks. No global state.

### 4. Operational Transparency
The diagnostics page (/diagnostics) displays the full active configuration.

---
## 2. Loading Order
Configuration is loaded in three layers:

###    1. Defaults  
    Defined in logexp/app/config/defaults.py.

###    2. Environment Variables  
    Parsed and type‑coerced by env.py.

###    3. Overrides  
    Passed explicitly to load_config() (used in tests and scripts).

Final config = defaults → env → overrides.

---
## 3. Configuration Keys
### Environment & Application
| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `LOGEXP_ENV` | string | `"development"` | Application environment label. |
| `SQLALCHEMY_DATABASE_URI` | string | `"sqlite:///:memory:"` | Database connection string. |
| `TIMEZONE` | string | `"UTC"` | Database connection string. |
| `LOCAL_TIMEZONE` | string | `"UTC"` | UI‑facing timezone for display. |
---
### Poller
| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `START_POLLER` | bool | `True` | Whether to start the Geiger poller. |
| `POLL_INTERVAL ` | int | `5` | Polling interval in seconds. |
| `GEIGER_DEVICE_PATH` | string | `"/dev/ttyUSB0"` | Serial device path. |
---
### Analytics
| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `ANALYTICS_ENABLED` | bool | `True` | Enables analytics calculations. |
| `ANALYTICS_WINDOW` | int | `60` | Rolling window size in seconds. |
---
### Ingestion
| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `INGESTION_ENABLED` | bool | `True` | Enables ingestion pipeline. |
| `INGESTION_BATCH_SIZE` | int | `100` | Batch size for ingestion. |
---
### UI Toggles
| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `SHOW_DIAGNOSTICS` | bool | `True` | Enables diagnostics page. |
| `SHOW_ANALYTICS` | bool | `True` | Enables analytics UI. |
---
### Testing
| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `TESTING` | bool | `False` | Ensures deterministic test behavior. |
---
## 4. Override Mechanisms
### 1. Environment Variables
Any config key can be overridden via environment variable:
```
export POLL_INTERVAL=10
export START_POLLER=false
```
Booleans accept: `true`, `false`, `1`, `0`, `yes`, `no`.

---
### 2. Test Overrides
Tests override config explicitly:
```python
app.config_obj = load_config(overrides={
    "TESTING": True,
    "START_POLLER": False,
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
})
```
This ensures:
- poller never starts
- DB is always in‑memory
- tests are deterministic
---
### 3. Runtime Overrides (rare)
Scripts or CLI commands may override config:
```python
config = load_config(overrides={"ANALYTICS_ENABLED": False})
```
Runtime mutation of `config_obj` is allowed but discouraged.

---
### 5. Diagnostics Integration
The diagnostics page displays the full active configuration:
```
/diagnostics
```
This includes:
- defaults
- environment overrides
- test overrides
- final merged values

This is invaluable for debugging and onboarding.

---
### 6. Adding New Configuration Keys
To add a new config key:

1. Add default to defaults.py
2. Add type coercion (if needed) to env.py
3. Add validation to validators.py
4. Use `config_obj["KEY"]` in application code
5.  Add to diagnostics table
6. Document it in this file

This ensures consistency and prevents drift.

---
### 7. Anti‑Patterns (Do Not Do)
- ❌ Do not use os.getenv() anywhere in the app
- ❌ Do not use app.config[...] for application logic
- ❌ Do not mutate config inside blueprints or services
- ❌ Do not rely on implicit defaults in code
- ❌ Do not override config via environment in tests

The only correct access pattern is:
```
current_app.config_obj["KEY"]
```
---
