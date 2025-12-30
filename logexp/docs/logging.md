# Logging Architecture

This project uses deterministic, structured JSON logging for all
application‑level observability.

The logging system is designed to be:
- predictable across environments
- testable without brittle parsing
- safe for CI and production
- understandable without reading the entire codebase

---

## Guarantees

The following guarantees are enforced by design:

- All application logs are structured JSON
- All timestamps are UTC
- Logging output is deterministic
- No modification of the root logger
- No environment‑specific logging behavior
- Logging works identically in local, CI, and production

---

## Namespaced Loggers

Structured logging is enabled for the following namespaces:

- `logexp.app`
- `logexp.ingestion`
- `logexp.analytics`

Each namespace has:
- a dedicated handler
- a shared structured formatter
- propagation enabled for test visibility

---

## Structured Log Format

Every structured log entry contains the following fields:

- `ts` — ISO‑8601 UTC timestamp
- `level` — log level (INFO, WARNING, ERROR)
- `name` — logger namespace
- `msg` — semantic message

Example:
```json
{"ts":"2025-01-01T00:00:00+00:00","level":"INFO","name":"logexp.analytics","msg":"analytics_start"}
```

---

## Formatter Contract

The structured formatter guarantees:

- UTC timestamps only
- No implicit formatting
- No environment‑dependent fields
- No mutation of the root logger
- Compatibility with pytest logging capture

---

## Propagation Model

All application loggers propagate to the root logger.

This is intentional and required for:
- pytest `caplog` visibility
- deterministic test behavior
- CI observability

Handlers are attached at the namespace level.
The root logger is never modified.

---

## Output Sink

Structured logs are written to stderr.

This ensures:
- compatibility with container runtimes
- compatibility with CI log capture
- compatibility with log aggregation systems

