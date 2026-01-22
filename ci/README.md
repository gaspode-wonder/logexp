# ci/README.md

# CI Architecture Overview

LogExp uses a three‑lane CI architecture designed for clarity, determinism, and fast failure isolation. Each lane runs independently and validates a specific dimension of correctness.

## Lanes

### 1. Lint Lane (`lint.yml`)
Ensures formatting and import hygiene are consistent across the codebase.

- Python 3.11
- Runs flake8
- Fails fast on style violations
- No database or application boot required

### 2. Typecheck Lane (`typecheck.yml`)
Enforces strict mypy type safety.

- Python 3.11
- Uses `mypy.ini` for project‑wide strictness
- Validates all modules under `logexp/`
- No runtime environment required

### 3. Application CI Lane (`application-ci.yml`)
Validates runtime correctness, migrations, and tests.

- Python 3.10 and 3.11 matrix
- Uses SQLite (`SQLALCHEMY_DATABASE_URI=sqlite:///ci.db`)
- Runs environment parity checks
- Applies Alembic migrations
- Executes pytest suite

## Trigger Rules

All lanes run on:

- Pull requests targeting `main`
- Direct pushes to `main`

## Local Parity

Use the Makefile wrapper:
```bash
make ci
```

This runs lint, typecheck, and application tests locally using the same commands as CI.

## Philosophy

- No hidden magic
- No split‑brain config
- Deterministic, reproducible, onboarding‑friendly workflows
- CI failures must be isolated, actionable, and fast to diagnose

