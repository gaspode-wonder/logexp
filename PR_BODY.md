# Step 9F: App Init Hardening, Logging Cleanup, and Removal of Legacy Modules

This PR completes **Step 9F** of the logging + initialization hardening roadmap.  
It finalizes the transition to a single deterministic logging system, removes legacy modules, and eliminates all stray debug scaffolding.

## Summary of Changes

### Application Initialization Hardening
- [x] Consolidated initialization logic in `logexp/app/__init__.py`
- [x] Removed stray `print()` calls and replaced lifecycle messages with structured logging
- [x] Ensured ingestion and poller initialization paths are deterministic and test‑safe
- [x] Cleaned up config object exposure and startup diagnostics

### Logging System Cleanup
- [x] Removed legacy modules:
  - `logexp/app/logging.py`
  - `logexp/app/logging_setup.py`
- [x] Finalized `logging_loader.py` as the single source of truth
- [x] Enabled propagation for `logexp.*` namespace
- [x] Added datetime serialization to JSON formatter
- [x] Ensured all logexp loggers emit JSON to stderr (pytest‑capturable)

### Analytics Logging Contract
- [x] Restored and validated the analytics logging test
- [x] Ensured `extra=result` dicts serialize cleanly
- [x] Verified contract fields: `count`, `avg_cps`, `first_timestamp`, `last_timestamp`
- [x] Confirmed deterministic behavior under frozen time

### Debug Scaffolding Removal
- [x] Removed all stray `print()` statements across the codebase
- [x] Converted meaningful operational prints to `logger.debug()`
- [x] Cleaned ingestion debug output
- [x] Removed temporary test instrumentation

### Blueprint & Structure Updates
- [x] Added `bp/health` blueprint directory
- [x] Added `tests/__init__.py` for namespace hygiene
- [x] Cleaned up blueprint registration ordering

### Test & Config Updates
- [x] Updated `pytest.ini` to reflect new logging behavior
- [x] Cleaned `tests/conftest.py` to remove debug scaffolding
- [x] Ensured full suite passes (26/26)

## Related Steps

- **Step 9A:** Environment defaults + CI analytics config  
- **Step 9B:** Logging namespace isolation  
- **Step 9C:** JSON handler + stderr routing  
- **Step 9D:** Flask logger mutation cleanup  
- **Step 9E:** (Upcoming) Timezone policy documentation  
- **Step 9F:** _This PR — app init hardening + cleanup_

## Reviewer Notes

This PR is intentionally structured as a **single cohesive unit** because the changes are tightly coupled:

- Removing legacy logging modules required updating imports across the app.
- Hardening app initialization required cleaning ingestion and poller startup paths.
- Finalizing the JSON logging contract required updating tests and datetime serialization.
- Removing debug scaffolding required touching several modules.

All changes are isolated to the `step9F-app-init-hardening` branch and do not affect unrelated subsystems.

## Reviewer‑Friendly Diff Summary

### Major deletions
- `logexp/app/logging.py`
- `logexp/app/logging_setup.py`
- All stray debug prints across ingestion, app init, and tests

### Major modifications
- `logexp/app/logging_loader.py`  
  → datetime serialization, propagation fix, handler isolation  
- `logexp/app/__init__.py`  
  → init hardening, removal of debug prints  
- `logexp/app/ingestion.py`  
  → cleanup of config debug output  
- `logexp/app/poller.py`  
  → structured debug logging  
- `tests/test_logging_analytics.py`  
  → restored contract test, removed instrumentation  
- `tests/conftest.py`  
  → cleanup of debug scaffolding  

### Additions
- `logexp/app/bp/health/`  
- `tests/__init__.py`

## Status

**All tests passing: 26/26**  
**Branch:** `step9F-app-init-hardening`  
**Ready for review**
