# Roadmap (Post‑Step‑12B Merge)

This is the current, authoritative roadmap for LogExp after completing **Step 12B — Config Hygiene Pass**.

---

# Step 11 — System Restoration (Completed)

## 11F — Restore the Analytics Engine
**Status: ✔ Completed**
Delivered in PR #35.

- Analytics engine skeleton
- Rolling window placeholder
- Deterministic CI behavior
- Analytics diagnostics surface
- Architecture tests for analytics module identity
- API exposure via blueprint‑safe routes

---

## 11G — Restore the Diagnostics Page
**Status: ✔ Completed**
Delivered in PR #35.

- Diagnostics HTML restored
- Config, ingestion, poller, analytics, DB status surfaced
- Stable JSON contract
- Architecture tests for route existence + blueprint identity

---

## 11H — Restore API Endpoints
**Status: ✔ Completed**
Delivered in PR #35.

Endpoints restored:
- `/api/readings`
- `/api/analytics`
- `/api/health`
- `/api/diagnostics`

Architecture tests enforce:
- import‑time safety
- route registration correctness

---

## 11I — Restore the UI
**Status: ✔ Completed**
Delivered in PR #35.

- Templates render
- Diagnostics table displays
- Analytics graph placeholder restored
- Blueprint identity + template resolution validated

---

## 11J — Restore CLI Commands
**Status: ✔ Completed**
Delivered in PR #35.

- `flask ingest`
- `flask poller`
- `flask diagnostics`
- Architecture tests validate import‑time safety

---

## 11K — Runtime Smoke Test
**Status: ✔ Completed**

Validated through:
- Architecture tests
- Deterministic ingestion wrapper
- Poller diagnostics
- Analytics import‑time safety
- End‑to‑end diagnostics JSON contract

---

# Step 12 — Type‑Safety, Config Hygiene, and Observability
**Status: 🔥 Active Phase**

## 12A — Mypy + Type‑Safety Pass
**Status: ✔ Completed**

Delivered:
- Added missing `__init__.py`
- Added `mypy.ini`
- Ignored external libs (Flask‑Migrate, pyserial)
- Fixed duplicate module paths
- Added type hints to ingestion + analytics

---

## 12B — Config Hygiene Pass
**Status: ✔ Completed**

Delivered:
- Centralized config keys into `config_obj`
- Removed Flask‑config drift
- Added config validation
- Added config diagnostics
- Regenerated Makefile with:
  - colorized output
  - timing instrumentation
  - `dev-fast`
  - deterministic bootstrap lanes
  - CI parity lane

---

## 12C — Logging + Observability Pass
**Status: 🔜 Next**

Goals:
- Normalize logging under `logexp.*`
- Add structured logging to ingestion, poller, analytics
- Add request‑ID correlation
- Add analytics debug logging

---

## 12D — Test Architecture Hardening

Goals:
- Deterministic analytics tests
- Isolated poller tests
- Ingestion tests without real serial ports
- Fixtures for config overrides

---

## 12E — CI Stability Pass

Goals:
- Fully deterministic CI
- No flaky tests
- No timezone drift
- No race conditions

---

# Step 13 — Flask‑Login Authentication Layer
**Status: Pending**

## 🎯 Goal
Introduce minimal, deterministic authentication using Flask‑Login.

## 🔧 Preconditions
- Step 12 complete
- `create_app()` stable
- Blueprint hygiene enforced
- SQLAlchemy models clean
- CI green

## ✅ Exit Criteria
- Working login/logout flow
- `User` model + migration
- `login_manager` initialized
- `user_loader` implemented
- At least one protected route
- No contamination of ingestion/analytics/services
- Deterministic import order

---

## 13A — Create the User Model
- Add `logexp/app/models/user.py`
- Implement `User` with:
  - `id`, `username`, `password_hash`
  - `set_password()`, `check_password()`
  - `UserMixin`

---

## 13B — Initialize Flask‑Login
- Add `login_manager` to `extensions.py`
- Set `login_view = "auth.login"`
- Initialize in `create_app()`
- Implement `user_loader`

---

## 13C — Add the Auth Blueprint
- Create `logexp/app/bp/auth/`
- Add `/login` and `/logout`
- Implement POST login flow
- Implement logout

---

## 13D — Add Minimal Templates
- Add `templates/auth/login.html`
- Simple username/password form

---

## 13E — Protect a Route
- Protect `/dashboard` or similar
- Confirm redirect to `/auth/login`

---

## 13F — Add Test User Creation Path
- One‑time CLI or script
- No hardcoded credentials
- Validate login end‑to‑end

---

## 13G — Architecture Validation
- No blueprint imports in services
- No auth logic in ingestion/diagnostics
- No circular imports
- Deterministic behavior in containers

---
# Step 14 — Extract CLI Commands from Presentation Layer
**Status: Pending**

## 🎯 Goal
Separate all operational CLI logic from the presentation/UI layer by introducing a dedicated service layer for CLI commands, ensuring deterministic imports, clean architecture boundaries, and Pi‑safe execution.

## 🔧 Preconditions
- Step 13 fully merged and stable
- `create_app()` deterministic and side‑effect free
- All blueprints registered cleanly under `/bp/`
- Services layer exists and is import‑safe
- CI green with no import‑time failures

## ✅ Exit Criteria
- All CLI commands (`ingest`, `poller`, `diagnostics`) call pure service functions
- No CLI command imports UI templates or API blueprints
- No circular imports introduced
- CLI commands run without starting the web server
- CLI commands run deterministically on the Pi
- Architecture tests enforce service‑layer purity

---

## 14A — Define Operational Layer
- Create `services/cli.py`
- Move CLI logic into pure service functions

---

## 14B — Thin Flask CLI Wrappers
- `flask ingest` → calls ingestion service
- `flask poller` → calls poller service
- `flask diagnostics` → calls diagnostics service

---

## 14C — Architecture Enforcement
Tests ensure CLI commands:
- do not import UI templates
- do not import API blueprints
- depend only on services + app context

---

## 14D — Operational Stability
- Commands run without web server
- Deterministic in CI
- Pi‑safe

---

# Step 15 — Pi → LogExp Full Integration
**Status: Pending**

## 🎯 Goal
Establish a complete, stable, end‑to‑end ingestion pipeline from the Raspberry Pi’s `pi-log` process into LogExp, validating ingestion, analytics, diagnostics, and UI rendering under real hardware conditions.

## 🔧 Preconditions
- Step 14 complete and merged
- LogExp ingestion endpoint stable and deterministic
- Poller thread operational and import‑safe
- Database schema migrated and validated
- Pi hardware available with functioning Geiger counter
- Network connectivity between Pi and LogExp host

## ✅ Exit Criteria
- Pi sends real readings to LogExp continuously
- LogExp stores readings without error
- UI displays live readings and analytics
- Diagnostics reflect ingestion, poller, and analytics state accurately
- System remains stable during a 10–30 minute live run
- Integration documentation written and validated

---

## 15A — Confirm Pi Environment
- Validate OS, Python, serial device
- Confirm Geiger counter output
- Validate serial config
- Run raw serial test

---

## 15B — Configure Pi‑Log
- Point to LogExp ingestion endpoint
- Validate network reachability
- Export env vars
- Dry‑run payload formatting

---

## 15C — Enable Ingestion on LogExp
- Export ingestion env vars
- Validate `/api/readings` POST
- Confirm DB writes

---

## 15D — Live Data Flow Test
- Start `pi-log`
- Observe ingestion logs
- Confirm UI updates
- Confirm analytics updates
- Confirm diagnostics reflect ingestion

---

## 15E — Poller + Ingestion Interaction
- Validate no conflicts
- Confirm settings page correctness
- Validate serial error handling

---

## 15F — End‑to‑End Stability Run
- Run 10–30 minutes
- Confirm no ingestion failures
- No DB errors
- No UI 500s
- No analytics exceptions
- No runaway logs

---

## 15G — Integration Documentation
- Document Pi setup
- Document ingestion API
- Document troubleshooting
- Add “Live Integration” section to README

---

# Step 16 — Observability & Runtime Hardening
**Status: Pending**

## 🎯 Goal
Transform LogExp into a fully observable, diagnosable, and fault‑tolerant system with structured logging, expanded diagnostics, runtime safeguards, and clear health indicators.

## 🔧 Preconditions
- Step 15 complete with stable Pi → LogExp ingestion
- Logging infrastructure functional at basic level
- Diagnostics endpoint reachable and returning JSON
- No outstanding import‑time or circular‑dependency issues

## ✅ Exit Criteria
- All subsystems emit structured logs under `logexp.*`
- Diagnostics endpoint exposes DB, ingestion, poller, serial, and analytics health
- Runtime failures are isolated and logged without crashing the app
- Configuration validation prevents silent misconfiguration
- Health indicators available for ingestion, poller, DB, and analytics
- System stable under sustained ingestion load
- Observability documentation complete

---

## 16A — Logging Architecture Hardening
- Normalize namespaces
- Structured logs
- Level normalization
- Add logging around ingestion, analytics, poller

---

## 16B — Diagnostics Expansion
Add diagnostics for:
- DB connectivity
- Ingestion rate
- Poller status
- Serial config
- Analytics health

---

## 16C — Runtime Error Isolation
- Ingestion failures isolated
- Analytics guarded
- Missing env vars handled
- Serial fallback behavior
- DB errors surfaced but non‑fatal

---

## 16D — Configuration Robustness
- Validate env vars
- Add defaults
- Add warnings
- Settings page resilience

---

## 16E — Metrics & Health Indicators
- Ingestion metrics
- Poller metrics
- DB metrics
- Analytics metrics
- `/api/health` endpoint

---

## 16F — Stability & Load Testing
- Sustained ingestion
- Analytics stability
- Diagnostics responsiveness
- No memory leaks

---

## 16G — Documentation & Onboarding
- Logging architecture
- Diagnostics
- Health indicators
- Troubleshooting

---

# Step 17 — Directory Consolidation & Architecture Simplification
**Status: Pending**

## 🎯 Goal
Unify LogExp’s directory structure and service boundaries by collapsing legacy modules, removing duplicates, and enforcing a single source of truth across analytics, ingestion, diagnostics, and poller logic.

## 🔧 Preconditions
- Step 16 complete with stable observability and diagnostics
- All services (ingestion, analytics, poller, diagnostics) validated as import‑safe
- No outstanding architectural drift or shadow modules
- CI green with deterministic imports

## ✅ Exit Criteria
- Legacy analytics, ingestion, diagnostics, and poller modules collapsed into unified services
- Duplicate entrypoints removed
- Legacy wrappers removed
- Directory layout simplified and consistent
- Naming conventions unified across the codebase
- Architecture tests enforce the new structure
- A single, authoritative source of truth for each subsystem

---

## 17A — Collapse Legacy Analytics
- Remove old analytics modules under deprecated paths
- Move all analytics logic into `services/analytics.py`
- Ensure no UI or blueprint imports
- Validate deterministic import order

---

## 17B — Collapse Legacy Ingestion
- Remove legacy ingestion modules and wrappers
- Consolidate ingestion logic into `services/ingestion.py`
- Ensure ingestion service is import‑safe and Pi‑safe
- Update CLI and API endpoints to call the unified service

---

## 17C — Collapse Diagnostics Surfaces
- Remove legacy diagnostics modules
- Consolidate diagnostics logic into `services/diagnostics.py`
- Ensure `/api/diagnostics` and `/diagnostics/` UI call the unified service
- Validate JSON contract stability

---

## 17D — Collapse Poller Logic
- Remove legacy poller modules and wrappers
- Consolidate poller logic into `services/poller.py`
- Ensure poller thread uses the unified service
- Validate import‑time safety and thread‑safety

---

## 17E — Remove Duplicate Entrypoints
- Identify and remove redundant CLI commands, scripts, and wrappers
- Ensure a single authoritative entrypoint for each subsystem
- Validate that CI and dev workflows use the new entrypoints

---

## 17F — Remove Unused Modules
- Identify dead code, unused helpers, and abandoned prototypes
- Remove them with architecture tests ensuring no regressions
- Validate import graph cleanliness

---

## 17G — Unify Naming Conventions
- Standardize naming across services, modules, and directories
- Ensure consistency in imports, filenames, and namespaces
- Update architecture tests to enforce naming rules

---

## 17H — Unify Directory Layout
- Restructure directories to reflect the new service‑oriented architecture
- Ensure all blueprints live under `/bp/`
- Ensure all services live under `/services/`
- Ensure all models live under `/models/`

---

## 17I — Enforce Single Source of Truth
- Validate that each subsystem has exactly one authoritative module
- Remove any remaining shadow modules or duplicates
- Add architecture tests to enforce single‑source rules

---

## 17J — Final Architecture Validation
- Run full architecture test suite
- Validate import‑time safety across all modules
- Validate deterministic behavior in dev, CI, and Pi environments
- Update documentation to reflect the final architecture
