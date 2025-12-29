# Logging Architecture

## Guarantees
- All application logs are structured JSON
- All timestamps are UTC
- No root logger modification
- Deterministic output across environments

## Namespaces
- logexp.app
- logexp.ingestion
- logexp.analytics

## Formatter Contract
- ts
- level
- name
- msg

## Propagation Model
- Loggers propagate to root for test visibility
- Handlers are attached at namespace level
- pytest caplog captures pre-format records by design
