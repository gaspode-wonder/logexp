# 🚧 WIP: Centralized Config System, Poller Hardening, and Ingestion Pipeline Refactor

This PR introduces a multi‑stage refactor that centralizes configuration, unifies logging, hardens the Geiger poller lifecycle, and formalizes the ingestion pipeline. These changes are part of the architecture roadmap and prepare the codebase for Step 8 (Analytics Hardening), which will follow in a subsequent PR.

---

## ✅ Summary of Changes

### **Step 4 — Centralized Configuration System**
- Added `logexp/app/config/` module with:
  - `defaults.py`, `env.py`, `validators.py`, `loaders.py`
- Replaced all `os.getenv` and legacy `Config` class usage.
- `create_app()` now loads a deterministic, validated config object.
- Test suite now uses `load_config(overrides=...)` for safe, isolated overrides.
- Diagnostics page now displays the full merged configuration.
- Added `CONFIG.md` documenting all config keys, defaults, and override mechanisms.

### **Step 5 — Logging Unification**
- Added `configure_logging(app)` for consistent, stdout‑only logging.
- Removed all `print()` calls in favor of structured logging.
- Standardized log levels across poller, ingestion, and diagnostics.

### **Step 6 — Poller Lifecycle Hardening**
- Added lifecycle state flags (`_running`, `_stopping`) to prevent double‑start/stop.
- Added guards for:
  - TESTING mode
  - Gunicorn workers
  - Docker build layers
- Ensured clean shutdown and thread‑safe teardown.
- Added structured lifecycle logging.

### **Step 7 — Ingestion Pipeline Finalization**
- Added `logexp/app/ingestion.py` with `ingest_reading(parsed)`:
  - single write path for all live readings
  - config‑driven (`INGESTION_ENABLED`)
  - structured logging
  - safe rollback behavior
- Poller now delegates persistence to ingestion helper.
- Added `test_ingestion.py` covering:
  - ingestion persistence
  - ingestion disabled
  - rollback on commit failure

---

## 🧾 Reviewer Checklist

### **Architecture & Structure**
- [ ] Centralized config system (`config_obj`) used consistently
- [ ] No remaining `os.getenv` or legacy `Config` references
- [ ] Diagnostics page correctly displays merged config
- [ ] Logging unified via `configure_logging(app)`

### **Poller Lifecycle**
- [ ] Prevents double‑start and double‑stop
- [ ] Respects TESTING, Gunicorn, and Docker build guards
- [ ] Clean, thread‑safe shutdown
- [ ] Delegates DB writes to ingestion helper

### **Ingestion Pipeline**
- [ ] `ingest_reading()` is the single write path
- [ ] Respects `INGESTION_ENABLED`
- [ ] Structured ingestion logging
- [ ] Correct rollback behavior

### **Tests**
- [ ] Test suite uses `load_config(overrides=...)`
- [ ] Ingestion tests cover persistence, disabled mode, and rollback
- [ ] No poller threads start during tests
- [ ] Tests deterministic across macOS, Linux, CI

### **Documentation**
- [ ] CONFIG.md accurately documents config keys and behavior
- [ ] PR description matches implementation
- [ ] No stale references to removed config paths

---

## 📌 Status

- [x] Centralized config system  
- [x] Logging unification  
- [x] Poller lifecycle hardening  
- [x] Ingestion pipeline refactor  
- [ ] Analytics hardening (Step 8) — **coming next**  

This PR remains **WIP** until Step 8 is completed.

---

## 🏷️ Suggested Labels

- `refactor`
- `enhancement`
- `architecture`
- `backend`
- `observability`
- `testing`
- `WIP`
