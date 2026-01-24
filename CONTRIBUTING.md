# CONTRIBUTING.md

# Contributing to LogExp

Thank you for your interest in contributing to LogExp!
This project is built on strict reproducibility, deterministic behavior, and a clean architecture.
All contributions must follow the standards below to ensure long‑term stability and maintainability.

---

## Branching Model

All work must occur on feature branches:

```
git checkout -b feature/<step>-<description>
```

Examples:

- `feature/12d-analytics-cleanup`
- `feature/docker-hardening`
- `feature/fix-poller-timeouts`

Never commit directly to `main`.

---

## Pull Request Requirements

A PR may be merged only when:

- CI is green
- All imports resolve cleanly
- Tests pass in a clean environment
- No unpinned dependencies are introduced
- No environment‑specific assumptions are added
- Code follows the canonical project structure
- No debug prints or commented‑out code remain
- Migrations (if any) are correct and deterministic

PRs should be small, focused, and scoped to a single concern.

---

## Development Environment

To ensure your environment matches CI:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pytest
```

This prevents environment drift and ensures reproducibility.

---

## Code Style

- Follow existing patterns and conventions
- Use explicit imports
- Avoid circular dependencies
- Keep modules small and purpose‑specific
- Do not introduce hidden side effects
- Do not collapse analytics layers (pure vs DB)

Linting is enforced via CI using `ruff`.

---

## Tests

All new functionality must include tests.

### DB Analytics Tests

Use:

- `reading_factory`
- SQLAlchemy models
- Postgres/SQLite fixtures

### Pure Analytics Tests

Use:

- `make_reading`
- `make_batch`
- `ReadingSample` types

Never mix DB models with pure analytics types.

---

## Migrations

If your change modifies the database schema:

```bash
flask db migrate -m "description"
flask db upgrade
```

Ensure:

- The migration is deterministic
- The migration works on SQLite (tests)
- The migration works on Postgres 18 (CI)

---

## Docker & Deployment

If your change affects runtime behavior:

- Ensure the Dockerfile still builds
- Ensure `create_app()` boots inside the container
- Ensure environment variables are parsed correctly
- Ensure no SQLite fallback occurs in Docker

Use:

```bash
docker compose up --build
```

---

## Commit Hygiene

- Write clear, descriptive commit messages
- Keep commits logically grouped
- Avoid mixing refactors with functional changes
- Do not include unrelated formatting changes

---

## Documentation

If your change affects behavior, update:

- README.md
- Any relevant docs in `beamfoundry/docs/` (internal only)

Documentation must reflect the new architecture.

---

## Thank You

Your contributions help keep LogExp deterministic, maintainable, and production‑ready.
We appreciate your effort and attention to detail!
