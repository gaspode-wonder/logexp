# Architecture Test Suite Manifest

This directory contains **architecture‑level tests** — tests that enforce
structural invariants of the application rather than behavior of individual
functions. These tests exist to prevent entire classes of regressions that
are difficult to detect through normal unit or integration tests.

Architecture tests are allowed to be opinionated, strict, and high‑level.
They protect the *shape* of the system.

---

## Goals of the Architecture Test Suite

1. **Ensure blueprint identity stability**
   Blueprints must be defined once, imported consistently, and never
   redefined or shadowed. Duplicate module identities or blueprint
   redefinitions can silently remove routes.

2. **Ensure blueprint registration integrity**
   Every blueprint must register at least one route. If a blueprint
   registers zero routes, it usually indicates an import‑time failure or
   duplicate module identity.

3. **Ensure import‑time safety**
   No module in `logexp.app.services` should raise an exception at import
   time. Import‑time failures silently break blueprints and diagnostics.

4. **Ensure diagnostics stability**
   Diagnostics routes must always exist. Diagnostics is a cross‑cutting
   subsystem and is especially sensitive to import‑time failures.

5. **Ensure module identity uniqueness**
   A module should only be imported under a single identity. Multiple
   identities (e.g., `logexp.app.bp.diagnostics` vs `logexp.bp.diagnostics`)
   create duplicate namespaces and break blueprint registration.

6. **Ensure blueprint definitions live in the correct place**
   Blueprints must be defined in `__init__.py` and never redefined in
   `routes.py`.

---

## Current Tests

### 1. `test_blueprint_singleton.py`
Ensures the blueprint object in `__init__.py` is the same object used in
`routes.py`. Prevents the “duplicate blueprint identity” bug.

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

## How to Extend This Suite Over Time

Architecture tests should be added whenever:

### **A. A new subsystem is introduced**
Examples:
- A new blueprint
- A new service module
- A new analytics subsystem
- A new diagnostics surface

Add tests that assert:
- The subsystem imports cleanly
- The subsystem registers routes (if applicable)
- The subsystem exposes expected invariants

### **B. A regression occurs due to structural issues**
If a bug is caused by:
- import‑time exceptions
- circular imports
- blueprint misregistration
- module identity duplication
- route disappearance
- configuration split‑brain

…then add a test that would have caught it.

Architecture tests are *regression traps*.

### **C. A new architectural rule is established**
Examples:
- “All blueprints must use absolute imports”
- “All services must be pure at import time”
- “All diagnostics functions must be app‑context safe”
- “All analytics modules must expose a `summarize_*` function”

Add a test that enforces the rule.

### **D. A new directory or namespace is added**
If you add:
- `logexp/app/tasks/`
- `logexp/app/metrics/`
- `logexp/app/observability/`

Add:
- import‑integrity tests
- module‑identity tests
- structural invariants

### **E. A maintainer expresses confusion**
If onboarding friction occurs, add a test that encodes the expectation.

Architecture tests are documentation that executes.

---

## Principles for Writing Architecture Tests

- **Be explicit**
  Architecture tests should state exactly what invariant they enforce.

- **Be stable**
  These tests should not break due to normal refactoring.

- **Be high‑signal**
  When they fail, they should point directly to a structural problem.

- **Be minimal**
  One invariant per test file.

- **Be future‑maintainer friendly**
  Tests should explain *why* the invariant matters.

---

## When *Not* to Add Architecture Tests

Avoid adding architecture tests for:
- stylistic preferences
- naming conventions
- formatting rules
- trivial behaviors
- tests that duplicate linting or type checking

Architecture tests should protect the **shape** of the system, not its
surface details.

---

## Summary

This directory is the system’s **structural firewall**.
It prevents regressions that normal tests cannot detect and ensures the
application remains stable, predictable, and maintainable as it evolves.

When in doubt:
**If a bug was structural, add an architecture test.**
