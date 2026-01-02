# Architecture Tests

These tests enforce structural invariants of the logexp application.

They are not unit tests and not behavior tests.
They are *architecture guardians* — ensuring that core project assumptions
remain true as the codebase evolves.

## Why these tests exist

- Prevent blueprint identity duplication
- Ensure all blueprints register at least one route
- Detect import‑time exceptions in service modules
- Ensure diagnostics routes never silently disappear again
- Prevent accidental blueprint redefinition inside `routes.py`
- Detect multiple module identities for the same package

## Test Suite Contents

### 1. `test_blueprint_singleton.py`
Ensures that the blueprint object defined in `__init__.py` is the same object
used in `routes.py`. Prevents the “duplicate blueprint identity” bug.

### 2. `test_blueprint_registration.py`
Ensures every blueprint registers at least one route.

### 3. `test_import_integrity.py`
Ensures no service module raises an exception at import time.

### 4. `test_diagnostics_routes_exist.py`
Ensures diagnostics routes are present and correctly registered.

### 5. `test_module_identity.py`
Ensures diagnostics is imported under exactly one module identity.

### 6. `test_blueprint_definition.py`
Ensures no blueprint is redefined inside `routes.py`.

---

These tests protect the architectural spine of the application and prevent
entire classes of regressions.
