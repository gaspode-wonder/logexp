# logexp/app/ingestion.py
"""
Compatibility shim for legacy imports.

The real ingestion implementation now lives in:
    logexp.app.services.ingestion

This file exists only to preserve older import paths used by tests and
internal modules (e.g., poller) until Step 11E updates all callers.
"""

from logexp.app.services.ingestion import (  # noqa: F401
    ingest_batch,
    ingest_reading,
    ingest_readings,
)
