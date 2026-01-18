# Observability Contracts

This document defines the observability guarantees for ingestion
and analytics pipelines.

These guarantees allow operators and maintainers to reason about
system behavior without inspecting code.

---

## Ingestion Observability

The ingestion pipeline emits the following structured events:

### ingestion_start
Emitted when ingestion begins.

Guarantees:
- ingestion process has started
- database session is active

### ingestion_complete
Emitted when ingestion finishes successfully.

Guarantees:
- ingestion logic completed
- database writes committed

---

## Analytics Observability

The analytics pipeline emits the following structured events:

### analytics_start
Emitted when analytics processing begins.

Guarantees:
- analytics pipeline invoked
- database session active

### analytics_complete
Emitted when analytics processing finishes.

Guarantees:
- analytics logic completed
- results written or evaluated

---

## Demo Commands

The following commands provide one‑command sanity checks:

### Logging demo
```bash
make log-demo
```
### Analytics demo
```bash
make analytics-demo
```

These commands:
- run real application code
- emit structured logs
- exit cleanly
- require no test harness

---

## Expected Output

A successful analytics demo emits logs similar to:
```json
{"ts":"...","level":"INFO","name":"logexp.analytics","msg":"analytics_start"}
{"ts":"...","level":"INFO","name":"logexp.analytics","msg":"analytics_complete"}
```

This confirms:
- logger wiring
- formatter correctness
- database lifecycle
- clean execution
