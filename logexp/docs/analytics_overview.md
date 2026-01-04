# Analytics Architecture Overview (Step‑12D)

This document defines the canonical architecture for analytics in LogExp.

It formalizes the separation between:

1. The **pure in‑memory analytics engine** (`logexp.analytics.engine`)
2. The **legacy DB‑backed analytics pipeline** (`logexp.app.services.analytics`)

These layers serve different purposes and must not be merged.

---

## 1. Pure Analytics Engine (Authoritative Future Layer)

**Module:** `logexp.analytics.engine`
**Type:** Stateless, deterministic, side‑effect‑free
**Input:** `ReadingSample` objects
**Output:**

- Windowed list of samples (`run()`)
- Rollup metrics (`compute_metrics()`)

### 1.1 Responsibilities

- Maintain an in‑memory list of `ReadingSample`
- Enforce timezone‑aware timestamps
- Apply inclusive sliding windows
- Sort readings deterministically
- Compute min/max/avg/count metrics
- Provide a stable API for future ingestion pipelines

### 1.2 Non‑Responsibilities

- Database access
- Flask context
- SQLAlchemy models
- Configuration
- Logging side effects
- Backward compatibility with legacy analytics

The pure engine is the **future** of analytics in LogExp.

---

## 2. Legacy DB Analytics Pipeline (Compatibility Layer)

**Module:** `logexp.app.services.analytics`
**Type:** Transitional adapter
**Input:** SQLAlchemy `LogExpReading` rows
**Output:** Legacy dict shape:

```python
{
    "count": ...,
    "avg_cps": ...,
    "first_timestamp": ...,
    "last_timestamp": ...,
}
```

### 2.1 Responsibilities

- Query DB for readings inside the configured window
- Compute legacy rollup metrics
- Emit legacy logging events (`analytics_start`, `analytics_complete`)
- Maintain backward compatibility with existing API consumers

### 2.2 Non‑Responsibilities

- Pure analytics logic
- Window semantics
- Sorting
- Future ingestion pipelines

This layer will shrink over time and eventually be removed.

---

## 3. Why These Layers Must Stay Separate

- The pure engine is deterministic and testable without a DB.
- The legacy pipeline is tied to SQLAlchemy and Flask.
- Mixing them introduces nondeterminism, test fragility, and architectural drift.

Separation ensures:

- Reproducible tests
- Clean fixture boundaries
- Future‑proof ingestion pipelines
- Maintainable code paths

---

## 4. Analytics Layer Map (DB vs In‑Memory)

This map clarifies the two analytics layers and their boundaries.

### 4.1 Pure In‑Memory Engine (Future Layer)

**Module:** `logexp.analytics.engine`
**Fixtures:**

- `make_reading`
- `make_batch`

**Tests:**

- `tests/test_analytics.py`

**Data Flow:**

`ReadingSample` → `AnalyticsEngine` → window list → metrics (via `compute_metrics()`)

**Characteristics:**

- No DB
- No Flask
- No side effects
- Deterministic
- Fast
- Fully unit‑testable

---

### 4.2 Legacy DB Analytics (Compatibility Layer)

**Module:** `logexp.app.services.analytics`
**Functions:**

- `compute_window`
- `run_analytics`

**Fixtures:**

- `reading_factory` (creates `LogExpReading` rows)
- `db_session`
- `test_app`

**Tests:**

- `tests/unit/test_analytics.py`
- `tests/unit/test_analytics_load.py`

**Data Flow:**

`LogExpReading` (DB) → `compute_window()` → `run_analytics()` → legacy dict

**Characteristics:**

- SQLAlchemy queries
- Flask app context required
- Transitional
- Will be removed after ingestion migration

---

## 5. Fixture Boundary Documentation

This section defines the canonical fixture boundaries for analytics tests.

---

### 5.1 DB‑Backed Fixtures (Integration‑Style Analytics Tests)

#### `reading_factory`

- Creates `LogExpReading` rows in the test database.
- Normalizes timestamps.
- Computes `counts_per_minute` when not provided.
- Adds rows to the active SQLAlchemy session.

**Used by:**

- `tests/unit/test_analytics.py`
- `tests/unit/test_analytics_load.py`

#### `db_session`

- Provides a clean SQLAlchemy session.
- Clears tables between tests.

#### `test_app` / `test_client`

- Provide Flask app + DB context for DB‑backed tests.

---

### 5.2 Pure In‑Memory Fixtures (Engine Tests)

#### `make_reading`

- Creates `ReadingSample` objects for the pure engine.
- Normalizes timestamps to timezone‑aware.
- Sets `.value` from the provided CPS.

#### `make_batch`

- Accepts a list of `(timestamp, cps)` tuples.
- Returns a list of `ReadingSample` using `make_reading`.

**Used by:**

- `tests/test_analytics.py`

---

### 5.3 Why These Fixtures Must Not Mix

- DB tests require SQLAlchemy models (`LogExpReading`).
- Pure engine tests require in‑memory dataclasses (`ReadingSample`).

Mixing them breaks:

- Window semantics
- Timestamp comparisons
- Sorting assumptions
- Rollup metrics behavior
- Test determinism and isolation

---

### 5.4 `conftest.py` Import Rules

Fixtures must be imported by **name** so pytest registers them.
Ruff must be explicitly silenced, because pytest uses fixtures implicitly.

Example from `tests/conftest.py`:

```python
from tests.fixtures.reading_factory import (  # noqa: F401
    reading_factory,
    make_reading,
    make_batch,
)

from tests.fixtures.analytics_engine import analytics_engine  # noqa: F401
from tests.fixtures.analytics import ts_base, shift  # noqa: F401
from tests.fixtures.poller_factory import make_poller  # noqa: F401
```

- `# noqa: F401` is required because Ruff sees these imports as unused.
- Pytest discovers fixtures by the imported names, so they are intentionally “unused” in regular Python terms.

---

## 6. Contract Summary

| Layer           | Input           | Output                         | Purpose                    |
|----------------|-----------------|--------------------------------|----------------------------|
| Pure Engine    | `ReadingSample` | window list + metrics          | deterministic analytics    |
| Legacy Pipeline| `LogExpReading` | legacy metrics dict            | backward compatibility     |

---

## 7. Migration Path (High‑Level)

1. New ingestion/control‑plane code uses the pure engine (`AnalyticsEngine`).
2. Legacy DB analytics continues to operate unchanged through `run_analytics`.
3. Over time, consumers of the legacy dict API are migrated to use the pure engine (via a thin adapter if needed).
4. Once no production code depends on `run_analytics`, the legacy DB layer is removed.
5. The pure engine becomes the sole analytics implementation.


