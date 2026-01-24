# Logging Tests: Design Rationale

This document explains how logging is tested and why the tests are
written the way they are.

Understanding this prevents accidental regressions.

---

## What pytest caplog Captures

pytest `caplog` captures:

- raw `LogRecord` objects
- pre‑formatted messages
- logger name and level

It does NOT capture:
- handler output
- formatter output
- stderr streams

This behavior is by design.

---

## What caplog Does NOT Capture

caplog never sees:
- JSON emitted by handlers
- formatted log strings
- stderr output

Attempting to parse JSON from `caplog` will always fail.

---

## Testing Strategy

Logging tests assert:

- semantic intent (`record.getMessage()`)
- correct logger namespace
- correct log level
- correct event ordering

They do NOT assert:
- JSON formatting
- timestamp structure
- handler output

Formatter correctness is validated separately.

---

## Why Propagation Is Enabled

Application loggers propagate to the root logger so that:

- caplog can observe records
- tests remain deterministic
- no test‑only logging hacks are required

The root logger itself is never modified.

---

## Why This Matters

This design ensures:

- stable tests
- predictable logging behavior
- no coupling between tests and formatter internals
- no rediscovery of logging mechanics by future maintainers
