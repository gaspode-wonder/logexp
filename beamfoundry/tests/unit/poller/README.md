# tests/unit/poller/README.md

# Poller Test Suite

This directory contains **pure, deterministic tests** for `logexp.poller.Poller`.

## Goals

- No real serial ports
- No real ingestion pipeline
- No Flask, no threads, no DB
- Deterministic, repeatable, CI‑safe

## Fixtures

- `FakeSerial` — programmable sequence of frames and exceptions
- `FakeIngestion` — captures frames and can simulate ingestion failures
- `make_poller` — factory that wires config, fake serial, and fake ingestion

## What we test

- `poll_once` in fake and serial modes
- `poll_forever` respecting `MAX_FRAMES`
- ingestion failures and frame counters
- diagnostics correctness (`get_diagnostics`)

The Flask `GeigerPoller` in `logexp/app/poller.py` is **not** tested here;
it is runtime infrastructure and should be covered by higher‑level integration tests.
