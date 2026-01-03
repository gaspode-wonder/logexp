# Roadmap (Post‑Step‑11F Merge)

## 11F — Restore the Analytics Engine
**Status: ✔ Completed**

Delivered in PR #35:
- Analytics engine skeleton
- Rolling window logic placeholder
- Deterministic CI behavior
- Analytics diagnostics surface
- Architecture tests for analytics module identity
- API exposure via blueprint‑safe routes

---

## 11G — Restore the Diagnostics Page
**Status: ✔ Completed**

Delivered in PR #35:
- Diagnostics HTML restored
- Config, ingestion, poller, analytics, database status surfaced
- Stable JSON contract enforced
- Architecture tests ensure route existence + blueprint identity

---

## 11H — Restore API Endpoints
**Status: ✔ Completed**

Delivered in PR #35:
- `/api/readings`
- `/api/analytics`
- `/api/health`
- `/api/diagnostics`
- Architecture tests enforce import‑time safety + route registration

---

## 11I — Restore the UI
**Status: ✔ Completed**

Delivered in PR #35:
- Templates render
- Diagnostics table displays
- Analytics graph placeholder restored
- Blueprint identity + template resolution validated

---

## 11J — Restore CLI Commands
**Status: ✔ Completed**

Delivered in PR #35:
- `flask ingest`
- `flask poller`
- `flask diagnostics`
- CLI commands validated via architecture tests (import‑time safety)

---

## 11K — Runtime Smoke Test
**Status: ✔ Completed**

Validated implicitly through:
- Architecture tests
- Deterministic ingestion wrapper
- Poller diagnostics surface
- Analytics engine import‑time safety
- End‑to‑end diagnostics JSON contract

---

# Step 12 — Type‑Safety, Config Hygiene, and Observability
**Status: 🔜 Active Phase**

## 12A — Mypy + Type‑Safety Pass
- Add missing `__init__.py`
- Add `mypy.ini`
- Ignore external libs (Flask‑Migrate, pyserial)
- Fix duplicate module paths
- Add type hints to ingestion + analytics

## 12B — Config Hygiene Pass
- Ensure all config keys live in `config_obj`
- Remove Flask‑config drift
- Add config validation
- Add config diagnostics

## 12C — Logging + Observability Pass
- Ensure all loggers use `logexp.*`
- Add structured logging to poller + ingestion
- Add request‑ID correlation
- Add analytics debug logging

## 12D — Test Architecture Hardening
- Ensure analytics tests are deterministic
- Ensure poller tests are isolated
- Ensure ingestion tests do not hit real serial ports
- Add fixtures for config overrides

## 12E — CI Stability Pass
- Ensure CI runs deterministically
- Ensure no flaky tests
- Ensure no timezone drift
- Ensure no race conditions

---


# Step 13 — Add Flask‑Login Authentication
**Status: Pending**
**Begins after Step 12 completes**

## 🎯 Goal
Introduce a minimal, deterministic authentication layer using Flask‑Login, enabling protected routes and user sessions without disturbing existing ingestion, diagnostics, or blueprint hygiene.

## 🔧 Preconditions
- Step 12 is fully complete and merged.
- `create_app()` is stable and deterministic.
- Blueprint hygiene is enforced (all blueprints under `/bp/`).
- SQLAlchemy models are loading cleanly with no circular imports.
- Containerized LogExp builds are passing CI.

## ✅ Exit Criteria
- A working login/logout flow exists at `/auth/login` and `/auth/logout`.
- A `User` model is created and migrated.
- Flask‑Login is initialized in `create_app()` with a working `user_loader`.
- At least one route is protected with `@login_required`.
- No presentation‑layer contamination of services or ingestion logic.
- All new code respects blueprint hygiene and deterministic import order.

## 13A — Create the User Model
- Add `logexp/app/models/user.py`
- Implement `User` class with:
  - `id`, `username`, `password_hash`
  - `set_password()` and `check_password()`
  - `UserMixin` inheritance
- Ensure model imports only `db` and Werkzeug security helpers

## 13B — Initialize Flask‑Login
- Add `login_manager` to `logexp/app/extensions.py`
- Configure `login_manager.login_view = "auth.login"`
- In `create_app()`, initialize `login_manager`
- Implement `@login_manager.user_loader` using `User.query.get()`

## 13C — Add the Auth Blueprint
- Create `logexp/app/bp/auth/`
  - `__init__.py` with `bp = Blueprint("auth", url_prefix="/auth")`
  - `routes.py` with `/login` and `/logout`
- Implement POST login flow:
  - Validate username/password
  - Call `login_user()`
  - Redirect to a safe default route
- Implement logout flow using `logout_user()`

## 13D — Add Minimal Templates
- Add `templates/auth/login.html`
- Provide a simple username/password form
- No styling required; functional only

## 13E — Protect a Route
- Choose one existing route (e.g., `/dashboard`)
- Add `@login_required`
- Confirm redirect to `/auth/login` when unauthenticated

## 13F — Add a Test User Creation Path
- Provide a one‑time CLI or script to create an initial user
- Ensure no hardcoded credentials in repo
- Validate login works end‑to‑end in dev container

## 13G — Architecture Validation
- Confirm:
  - No blueprint imports in services
  - No auth logic leaks into ingestion or diagnostics
  - No circular imports introduced
  - Deterministic behavior in containerized dev/prod builds

---

# Step 13 — Extract CLI Commands from the Presentation Layer (change to Step 14)
**Status: Pending**

## 13A — Define a Dedicated Operational Layer
- Create `logexp/app/services/cli.py`
- Move all CLI logic into pure service functions
- Ensure no blueprint or route imports

## 13B — Thin Flask CLI Wrappers
- `flask ingest` → calls ingestion service directly
- `flask poller` → calls poller service directly
- `flask diagnostics` → calls diagnostics service directly
- No presentation‑layer coupling

## 13C — Architecture Enforcement
- Add tests ensuring CLI commands:
  - do not import UI templates
  - do not import API blueprints
  - do not depend on presentation routes
  - only depend on services + app context

## 13D — Operational Stability
- Ensure CLI commands run without starting the web server
- Ensure deterministic behavior in CI
- Ensure no import‑time side effects
- Ensure commands work on the Pi without UI dependencies

# Step 14 — Pi → LogExp Full Integration

## Goal
Establish a complete, end‑to‑end data pipeline from the Raspberry Pi’s `pi-log` process into the LogExp web application, validating ingestion, storage, analytics, diagnostics, and UI rendering under real hardware conditions.

## Preconditions
- Step‑11F refactor fully merged and stable.
- App boots cleanly with all blueprints registered.
- Debug mode verified.
- Database URI set and tables created.
- Settings page, diagnostics, and analytics reachable.
- Poller thread operational.
- Pi hardware available and reachable on the network.

## Tasks

### 15A — Confirm Pi Environment
- Verify Pi OS, Python version, and serial device availability.
- Confirm Geiger counter is connected and producing serial output.
- Validate `GEIGER_PORT` and `GEIGER_BAUDRATE` values on the Pi.
- Run a standalone serial read test to confirm raw data flow.

### 15B — Configure Pi‑Log for LogExp
- Update `pi-log` config to point to the LogExp ingestion endpoint.
- Confirm network reachability from Pi → LogExp host.
- Export required environment variables on the Pi.
- Run `pi-log` in dry‑run mode to validate payload formatting.

### 15C — Enable Ingestion on LogExp
- Export ingestion‑related environment variables on the LogExp host.
- Confirm `/api/readings` POST endpoint accepts test payloads.
- Validate DB writes and confirm rows appear in `logexp_readings`.

### 15D — Live Data Flow Test
- Start `pi-log` on the Pi.
- Observe ingestion logs on LogExp.
- Confirm readings appear in the UI `/readings`.
- Confirm analytics updates in `/analytics`.
- Confirm diagnostics reflect live ingestion state.

### 15E — Poller + Ingestion Interaction
- Validate that the poller thread does not conflict with ingestion.
- Confirm settings page reflects correct serial configuration.
- Validate error handling for intermittent serial failures.

### 15F — End‑to‑End Stability Run
- Let the system run for 10–30 minutes.
- Confirm:
  - No ingestion failures.
  - No DB errors.
  - No UI 500s.
  - No analytics exceptions.
  - No runaway poller logs.

### 15G — Integration Documentation
- Document Pi setup, environment variables, and startup commands.
- Document ingestion API contract.
- Document troubleshooting steps for serial, network, and DB issues.
- Add a “Live Integration” section to the project README.

## Exit Criteria
- Pi sends real readings to LogExp continuously.
- LogExp stores readings without error.
- UI displays live data.
- Analytics pipeline processes live data.
- Diagnostics accurately reflect system state.
- System remains stable under continuous operation.

---

# Step 16 — LogExp Observability & Runtime Hardening

## Purpose
Transform LogExp from a functioning ingestion pipeline into a resilient, diagnosable, production‑grade system. This step ensures that once live Pi → LogExp data is flowing (Step 14), the system becomes transparent, fault‑tolerant, and easy to debug under real‑world conditions.

## 16A — Logging Architecture Hardening
- Establish consistent logging across all namespaces (`logexp.app`, `logexp.ingest`, `logexp.poller`, `logexp.analytics`, `logexp.settings`, etc.).
- Enforce structured log formats with timestamp, level, namespace, and message.
- Normalize log levels (INFO for normal ops, WARNING for recoverable issues, ERROR for ingestion/DB failures).
- Add explicit logging around ingestion, analytics, poller cycles, and settings changes.
- Ensure logs are human‑readable and grep‑friendly for future maintainers.

## 16B — Diagnostics Expansion
- Expand `/api/diagnostics` to include:
  - DB connectivity and table existence checks.
  - Ingestion rate and last‑ingested timestamp.
  - Poller thread status and last poll time.
  - Serial configuration state (port, baud, availability).
  - Analytics pipeline health.
- Expand `/diagnostics/` UI to surface these metrics cleanly.
- Add color‑coded indicators for healthy/degraded/failing subsystems.

## 16C — Runtime Error Isolation
- Ensure ingestion failures do not crash the app or poller.
- Wrap analytics computations in safe guards with clear error logs.
- Add graceful handling for missing environment variables.
- Add fallback behavior for missing serial devices.
- Ensure DB errors surface in diagnostics but do not break UI rendering.

## 16D — Configuration Robustness
- Validate all required environment variables at startup.
- Add defaults for non‑Pi development environments.
- Add warnings for missing or invalid config values.
- Ensure settings page handles missing config gracefully.

## 16E — Metrics & Health Indicators
- Add ingestion metrics (counts/min, last reading timestamp).
- Add poller metrics (cycle time, last success, last failure).
- Add DB metrics (row count, last write).
- Add analytics metrics (last run, last error).
- Expose a lightweight `/api/health` endpoint for external monitoring.

## 16F — Stability & Load Testing
- Run ingestion at sustained rates to validate DB performance.
- Confirm analytics remains stable under continuous updates.
- Validate that diagnostics remains responsive under load.
- Confirm no memory leaks, runaway threads, or log spam.

## 16G — Documentation & Onboarding
- Document the logging architecture and namespace conventions.
- Document diagnostics endpoints and expected outputs.
- Document health indicators and how to interpret them.
- Add a “Runtime Observability” section to the README.
- Provide a troubleshooting guide for ingestion, DB, poller, and analytics issues.

## Exit Criteria
- LogExp provides clear, actionable visibility into every subsystem.
- All runtime failures are isolated, logged, and diagnosable.
- Diagnostics and health endpoints accurately reflect system state.
- The system remains stable under continuous ingestion from the Pi.
- Future maintainers can debug issues without guesswork.

---

Step 17 — Directory Consolidation & Architecture Simplification

collapse legacy analytics into the new analytics service

collapse legacy ingestion into the new ingestion service

collapse diagnostics into a single diagnostics surface

collapse poller logic into a single poller service

remove unused modules

remove duplicate entrypoints

remove legacy wrappers

unify naming conventions

unify directory layout

enforce a single source of truth

---
