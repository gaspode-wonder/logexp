# Test Architecture

## Fresh App Per Test

All tests use a function-scoped `test_app` fixture that creates a brand-new
Flask application, config_obj, and in-memory SQLite database for each test.

This ensures:

- no cross-test contamination
- deterministic ingestion behavior
- reliable monkeypatching of SQLAlchemy session methods
- reproducible CI runs

### Key Guarantees

- `db.create_all()` and `db.drop_all()` run for every test
- `db.session.remove()` clears the scoped_session registry
- `config_obj` is rebuilt from defaults for each test
- ingestion tests never need to manually reset `INGESTION_ENABLED`

### Why This Matters

Flask-SQLAlchemy uses a scoped_session proxy that can leak state across tests
unless the app and session are recreated per test. This fixture pattern prevents
that entire class of bugs.
