# CHANGELOG.md

# LogExp Changelog

All notable changes to this project are documented here.
This project follows a stability‑first model: every change must preserve deterministic behavior, reproducibility, and CI correctness.

---

## [Unreleased]

### Added
- Placeholder for upcoming changes.

---

## [2026‑01‑22] — Architecture Stabilization Release

### Added
- Canonical `logexp/` package root replacing legacy `beamfoundry/`
- Pure analytics engine (`logexp.analytics.engine`)
- Typed analytics models (`ReadingSample`, `Batch`)
- Deterministic config layer with strict env var parsing
- Multi‑stage Dockerfile with non‑root runtime user
- Healthchecks for both Postgres and Flask
- Pi‑specific, macOS‑specific, and Linux‑specific compose files
- Runtime‑only dependency set (`docker-requirements.txt`)
- Full dependency pinning across dev and runtime
- New project structure documentation
- Deterministic WSGI entrypoint (`logexp.app.wsgi:app`)
- Updated README to reflect new architecture

### Changed
- Replaced legacy DB analytics with transitional compatibility layer
- Updated all imports to use `logexp.*` namespace
- Updated Docker entrypoint and Gunicorn command
- Updated CI to validate import‑time correctness
- Updated migrations to support Postgres 18
- Updated poller lifecycle (disabled by default in Docker)
- Updated environment variable contract

### Removed
- Legacy `beamfoundry` runtime package
- Old nested package layout
- Deprecated analytics paths
- Unused or obsolete Docker assets
- Legacy CI workflows

---

## [2025‑12‑XX] — Pre‑Stabilization Cleanup

### Added
- Initial analytics tests
- Early Docker support
- Basic CI pipeline

### Changed
- Refactored poller behavior
- Improved logging and diagnostics

### Removed
- Deprecated scripts and unused modules

---

## [2025‑11‑XX] — Initial Public Commit

### Added
- Flask application
- Poller thread
- Postgres integration
- Web UI
- Basic analytics
- Initial documentation
