# CI Failure Triage Guide

LogExp uses a three‑lane CI architecture designed for clarity, speed, and deterministic developer workflows. Each lane isolates a different class of failure so issues can be diagnosed quickly and reproduced locally.

## 1. Lint Lane Failures (lint.yml)

### Common causes
- Black formatting drift
- isort import‑ordering drift
- flake8 violations (unused imports, undefined names, complexity issues)

### How to fix
- `make format`
- `make lint`

### Typical symptoms
- “would reformat …”
- “imports are incorrectly sorted”
- “F401 unused import”
- “E501 line too long”

---

## 2. Typecheck Lane Failures (typecheck.yml)

### Common causes
- Missing type annotations
- Incorrect return types
- SQLAlchemy dynamic attribute issues
- Incorrect imports or module paths
- Optional values not handled
- Signature mismatches

### How to fix
- `make typecheck`

### Typical symptoms
- “Argument X to Y has incompatible type …”
- “Name ‘db.Model’ is not defined [name-defined]”
- “Missing return statement”
- “Item of type Optional[…] has no attribute …”

---

## 3. Application Lane Failures (application-ci.yml)

### Common causes
- Failing pytest tests
- Migration failures
- Environment parity mismatches
- Runtime import errors
- Analytics timestamp drift (UTC vs local)

### How to fix
- `make ci-local`

### Typical symptoms
- “OperationalError: no such table”
- “FAILED tests/...”
- “Environment variable mismatch”
- “Flask app failed to initialize”

---

## 4. Reproducing CI Locally

### Full CI parity
- `make ci-local`

### Individual lanes
- `make lint`
- `make typecheck`
- `make test`

---

## 5. When All Lanes Pass Locally but CI Still Fails

### Likely causes
- GitHub Actions using a different Python version
- Upstream dependency changes
- Missing or stale migration files
- Tests relying on local state
- Timezone‑sensitive analytics behavior

### Fix
- Confirm Python versions in workflows
- Pin dependencies
- Rebuild test DB
- Clear caches

---

## 6. When to Escalate

Escalate when:
- CI fails intermittently
- CI fails only on one Python version
- CI fails only on GitHub but not locally
- CI failures involve timezone or analytics drift

These indicate deeper architectural issues requiring investigation.
