# LogExp Roadmap — Updated January 2026
**Status: Active Project**

# LogExp Roadmap — January 2026 (Post‑Integration Revision)
**Status:** Active
**Line in the Sand:** Type‑safety, live ingestion, and container resurrection are complete.
**Next:** Minimal auth → Tech‑Debt Sprint → Beamwarden.

---

# Minimal Authentication Layer (Next Active Work)

**Goal:**
Add minimal Flask‑Login authentication without contaminating ingestion or analytics.

**Deliverables:**
- User model + Alembic migration
- Login/logout flow
- Protected route (e.g., `/dashboard`)
- Deterministic import order
- No blueprint contamination

**Exit Criteria:**
- CI green
- Local + container auth verified
- Documentation updated

---

# Tech‑Debt Sprint (Immediately After Auth)

**Goal:**
Burn down accumulated architectural debt before Beamwarden integration.

### Schema & Migration Hygiene
- Remove legacy columns
- Normalize naming
- Freeze ingestion schema
- Document schema contract

### Analytics Hardening
- Enforce type contracts
- Remove dead code paths
- Add analytics invariants
- Expand deterministic tests

### Diagnostics & Observability
- Add ingestion heartbeat
- Add analytics health surface
- Add DB health surface
- Expand structured logs

### Repo Hygiene
- Remove stale directories
- Collapse legacy modules
- Enforce canonical project layout
- README + onboarding refresh

**Exit Criteria:**
- Zero Pylance warnings
- Zero mypy ignores
- No dead modules
- Deterministic test suite
- Clean architecture boundaries

---

# Beamwarden Integration Prep

**Goal:**
Prepare LogExp to become a component in the Beamwarden ecosystem.

**Deliverables:**
- `/api/telemetry` endpoint
- Node heartbeat emission
- Node identity surface
- Structured telemetry logs
- Compatibility contract for Beamwarden ingestion

**Exit Criteria:**
- LogExp can report telemetry upward
- Beamwarden can ingest LogExp telemetry
- Node identity stable and documented

---

# Beamwarden (New Django/Python Project)

**Goal:**
Create the unified fleet manager + LogExp orchestrator.

### Project Initialization
- Django project skeleton
- Postgres 18 alignment
- Docker + Makefile lanes
- CI‑HARD baseline

### Inventory Authority
- Node model
- Role model
- Registration API
- Inventory UI

### Telemetry Aggregation
- `/api/telemetry` ingestion
- Telemetry events table
- Node status computation
- Telemetry dashboard

### Deployment & Orchestration (Future)
- SSH key authority
- Deployment manifests
- Version tracking
- Rollout orchestration

### LogExp Integration
- LogExp node registration
- LogExp telemetry ingestion
- LogExp version tracking
- LogExp diagnostics proxy

---

# LogExp Architecture Simplification (Optional)
- Collapse legacy directories
- Unified `services/` layer
- Architecture tests enforce purity

---

# LogExp v1 Release Candidate
- Schema freeze
- API freeze
- Container images versioned
- Documentation complete
- Beamwarden integration hooks validated

---

# ✔ Completed Milestones

## Step 12 — Type‑Safety, Config Hygiene, Observability
- Strict typing across ingestion + analytics
- Config centralization + validation
- Structured logging
- Deterministic test harness
- CI‑HARD stability

## Step 14 — Pi → LogExp Full Integration
- Real ingestion from Beamrider‑0001
- Stable analytics under live load
- Diagnostics validated
- 30‑minute stability run achieved

## Step 15 — Container Resurrection + Postgres Alignment
- Postgres 18 aligned (local + container)
- ARM/x86 builds validated
- Pi‑to‑Pi networking confirmed
- LogExp container stable on Beamrider‑0002

---







# Everything below is superseded

**Line in the Sand:** Step 12 complete, container resurrection + Pi integration now the primary focus.

---

# Step 12 — Type‑Safety, Config Hygiene, Observability
**Status: ✔ Fully Completed**

## 12A — Mypy + Type‑Safety
- Added missing `__init__.py`
- Added `mypy.ini`
- Fixed duplicate module paths
- Added type hints to ingestion + analytics

## 12B — Config Hygiene
- Centralized config keys
- Added config validation + diagnostics
- Regenerated Makefile with deterministic lanes

## 12C — Logging + Observability
- Structured logging under `logexp.*`
- Request‑ID correlation
- Analytics debug logging

## 12D — Test Architecture Hardening
- Deterministic analytics tests
- Isolated poller tests
- Config override fixtures

## 12E — CI Stability Pass
**Status: ✔ Completed**
- CI‑HARD green
- GitHub green
- No timezone drift
- No flaky tests

---

# Step 13 — Minimal Authentication Layer
**Status: Pending**

## Goal
Introduce minimal Flask‑Login authentication without contaminating ingestion/analytics.

## Exit Criteria
- User model + migration
- Login/logout flow
- Protected route
- Deterministic import order
- No blueprint contamination

---

# Step 14 — Pi → LogExp Full Integration
**Status: Upcoming**

## Goal
Real ingestion from Beamrider‑0001 into containerized LogExp on Beamrider‑0002.

## Exit Criteria
- Pi‑Log sends real readings
- LogExp stores + analyzes correctly
- Diagnostics reflect ingestion state
- 10–30 minute stability run
- Integration documentation

---

# Step 15 — Container Resurrection + Postgres Alignment
**Status: Active**

## 15A — Align Postgres Versions
- Upgrade container to Postgres 18
- Align local Postgres.app
- Validate migrations

## 15B — Container Bring‑Up
- Build ARM/x86 images
- Deploy to Beamrider‑0002
- Validate healthchecks

## 15C — Pi‑to‑Pi Networking
- Beamrider‑0001 → Beamrider‑0002 ingestion
- Telemetry heartbeat
- Diagnostics integration

---

# Step 16 — Telemetry + Fleet Awareness
**Status: Planned**

## Deliverables
- `/api/telemetry` endpoint
- `telemetry_events` table
- Node heartbeat protocol
- Diagnostics node‑status surface
- Structured logs for telemetry

---

# Step 17 — Directory Consolidation & Architecture Simplification
**Status: Planned**

## Deliverables
- Collapse legacy analytics/ingestion/diagnostics
- Unified `services/` layer
- Remove duplicate entrypoints
- Architecture tests enforce purity

---

# Step 18 — Observability & Runtime Hardening
**Status: Planned**

## Deliverables
- Expanded diagnostics
- Runtime error isolation
- Health indicators
- Load testing
- Observability documentation

---

# Step 19 — UI/UX Refresh (Optional)
**Status: Deferred**

## Deliverables
- Dashboard cleanup
- Live telemetry panel
- Node status view
- Settings page hardening

---

# Step 20 — Release Candidate
**Status: Future**

## Deliverables
- Full Pi → LogExp → UI pipeline validated
- Container images versioned
- Documentation complete
- Beamwarden integration hooks defined
~~~~markdown

---

---

If you want, I can also gnerate:

- a **unified architecture diagram**
- a **fleet protocol spec**
- a **Beamwarden onboarding guide**
- a **LogExp v1 release plan**  e

Just say the word.

# Unified Architecture Diagram — Beamwarden, LogExp, Pi‑Log

```text
                       ┌─────────────────────────────┐
                       │         Beamwarden          │
                       │  (Fleet Manager / Control)  │
                       │                             │
                       │  - Inventory & roles        │
          Web UI       │  - Telemetry aggregation    │ REST API
   ┌──────────────────▶│  - Deployment orchestration │◀─────────────┐
   │                   │  - SSH key authority        │              │
   │                   └─────────────┬───────────────┘              │
   │                                 │                              │
   │                                 │                              │
   │                         Fleet Control &                        │
   │                         Telemetry APIs                         │
   │                                 │                              │
   │                                 ▼                              │
   │                   ┌─────────────────────────────┐              │
   │                   │           LogExp            │              │
   │                   │ (Per-node Processing App)   │              │
   │                   │                             │              │
   │  Dashboard &      │  - Ingestion API            │              │
   │  diagnostics  ┌──▶│  - Analytics engine         │              │
   │               │   │  - Diagnostics endpoints    │              │
   │               │   │  - Local telemetry output   │              │
   │               │   └─────────────┬───────────────┘              │
   │               │                 │                              │
   │               │                 │ HTTP ingestion + telemetry   │
   │               │                 │                              │
   │               │                 ▼                              │
   │               │   ┌─────────────────────────────┐              │
   │               │   │            Pi‑Log           │              │
   │               │   │ (Sensor / Edge Process)     │              │
   │               │   │                             │              │
   │               │   │  - Serial read from Geiger  │              │
   │               │   │  - Local buffering          │              │
   │               │   │  - HTTP POST to LogExp      │              │
   │               │   │  - Heartbeat to Beamwarden* │──────────────┘
   │               │   └─────────────┬───────────────┘
   │               │                 │
   │               │                 │ Serial
   │               │                 │
   │               │                 ▼
   │               │   ┌─────────────────────────────┐
   └───────────────┴──▶│       Geiger Counter        │
                       └─────────────────────────────┘
```

\* Pi‑Log may send heartbeats directly to Beamwarden, or LogExp may proxy node health upward. This is configurable per deployment.

---

## Responsibilities

### Beamwarden
- **Inventory:** Source of truth for nodes (Pi‑Log, LogExp instances, other roles).
- **Telemetry:** Receives and aggregates telemetry from LogExp and/or Pi‑Log.
- **Orchestration:** Manages deployments, upgrades, and configuration.
- **Security:** SSH keys, roles, audit trails.

### LogExp
- **Ingestion:** Accepts sensor readings via HTTP from Pi‑Log.
- **Analytics:** Computes CPS/CPM and higher‑order metrics.
- **Diagnostics:** Exposes health of ingestion, DB, analytics, and node state.
- **Local Telemetry:** Emits node‑level telemetry upward to Beamwarden.

### Pi‑Log
- **Hardware Integration:** Talks to Geiger counters and other sensors.
- **Local Logic:** Handles retries, backoff, and buffering when LogExp is unreachable.
- **Reporting:** Sends measurements and heartbeats to LogExp and/or Beamwarden.

~~~~markdown

~~~~markdown
# Fleet Protocol Specification — Beamwarden, LogExp, Pi‑Log

## 1. Identities and Roles

### 1.1 Node Identity
Each node has a stable identity:

- `node_id`: short, human‑friendly (e.g. `beamrider-0001`)
- `role`: one of `pi-log`, `logexp`, `beamwarden`, or future roles
- `hostname`: system hostname
- `ip_address`: primary LAN IP

These fields are **authoritative in Beamwarden** and **reported by nodes**.

---

## 2. HTTP APIs

All communication is over HTTP/JSON, LAN‑scoped.

### 2.1 LogExp Ingestion API

- **Method:** `POST`
- **Path:** `/api/readings`
- **Content-Type:** `application/json`

**Request body:**

```json
{
  "node_id": "beamrider-0001",
  "timestamp": "2026-01-05T15:30:00Z",
  "counts": 37,
  "cps": 12.3,
  "cpm": 740.0,
  "tube_type": "SBM-20",
  "firmware_version": "pi-log-0.3.1"
}
```

**Constraints:**

- `timestamp` is UTC ISO‑8601.
- `node_id` must be known or discoverable by LogExp.
- LogExp validates, stores, and logs ingestion.

---

### 2.2 Telemetry API (Beamwarden and/or LogExp)

- **Method:** `POST`
- **Path:** `/api/telemetry`
- **Content-Type:** `application/json`

**Request body:**

```json
{
  "node_id": "beamrider-0001",
  "role": "pi-log",
  "timestamp": "2026-01-05T15:30:00Z",
  "uptime_seconds": 12345,
  "software_version": "pi-log-0.3.1",
  "ip_address": "192.168.1.42",
  "metrics": {
    "cps": 12.3,
    "cpm": 740.0,
    "serial_ok": true,
    "serial_error_count": 0,
    "ingest_http_error_count": 1,
    "cpu_percent": 23.5,
    "mem_percent": 41.2,
    "disk_percent": 55.0
  },
  "tags": {
    "hostname": "beamrider-0001",
    "env": "dev"
  }
}
```

Beamwarden stores this in `telemetry_events` and uses it to compute node status.

---

### 2.3 Node Registration API (Beamwarden)

- **Method:** `POST`
- **Path:** `/api/nodes/register`

**Request body:**

```json
{
  "node_id": "beamrider-0002",
  "role": "logexp",
  "hostname": "beamrider-0002",
  "ip_address": "192.168.1.52",
  "software_version": "logexp-1.0.0",
  "tags": {
    "location": "lab",
    "notes": "logexp container host"
  }
}
```

Beamwarden creates or updates the node record.

---

## 3. Heartbeat Semantics

### 3.1 Interval and Timeouts

- **Heartbeat interval:** `TELEMETRY_INTERVAL_SECONDS` (e.g. 30 seconds).
- **Online threshold:** last heartbeat ≤ 2 × interval.
- **Degraded threshold:** last heartbeat ≤ 5 × interval.
- **Offline threshold:** last heartbeat > 5 × interval.

These thresholds are enforced by Beamwarden.

---

## 4. Versioning and Compatibility

### 4.1 Protocol Version

Each telemetry payload may optionally include:

```json
"protocol_version": "1.0"
```

Beamwarden uses this to:

- reject unsupported versions,
- log warnings for deprecated versions,
- guide UI behavior (feature flags).

### 4.2 Software Version

`software_version` fields are free‑form but should be semantic versions where possible:

- `logexp-1.0.0`
- `pi-log-0.3.1`
- `beamwarden-0.1.0`

---

## 5. Security (Initial Phase)

Early development phase:

- LAN‑only, no auth headers required.
- Rely on network isolation and physical security.

Future phase:

- Shared secret in `X-BW-Auth` header.
- Optionally mTLS between nodes and Beamwarden.

---

## 6. Error Handling

### 6.1 Node Behavior

If POST fails (non‑2xx):

- Log error with status + message.
- Backoff with exponential or capped retry.
- For ingestion: buffer recent readings for retry if feasible.

### 6.2 Server Behavior

- Return `400` for schema violations with JSON error body.
- Return `503` for temporary issues (DB down, overload).
- Always emit structured error logs with `node_id`, `role`, and `request_id`.

~~~~markdown

~~~~markdown
# Beamwarden Onboarding Guide (Operator‑Facing)

## 1. What Is Beamwarden?

Beamwarden is the **control plane** for your Beamrider fleet:

- Tracks all nodes (Pi‑Log, LogExp, future roles).
- Aggregates telemetry and health status.
- Orchestrates deployments and configuration.
- Manages SSH keys and (later) Ansible runs.

Think of it as: _“Beamwarden is the keeper of the Beamriders.”_

---

## 2. Core Concepts

- **Node:** A machine participating in the fleet (Pi, server, VM, etc.).
- **Role:** The node’s primary function (`pi-log`, `logexp`, `beamwarden`, …).
- **Telemetry:** Periodic JSON heartbeats describing health and metrics.
- **Inventory:** Canonical list of nodes and their attributes.
- **Deployment:** A versioned release pushed to one or more nodes.

---

## 3. Getting Started

### 3.1 Install and Run Beamwarden (Dev Mode)

- Clone the repo.
- Create a virtualenv.
- Install dependencies via `pip` or `poetry`.
- Run migrations.
- Start the dev server on `http://localhost:8000`.

(Detailed commands will live in the Beamwarden `README` and `Makefile`.)

---

## 4. Connecting Nodes

### 4.1 Register a Node

Nodes can:

- Self‑register via `POST /api/nodes/register`, or
- Be created via Beamwarden’s admin UI.

At minimum you need:

- `node_id`
- `role`
- `hostname`
- `ip_address`

### 4.2 Telemetry Setup

On each node (LogExp or Pi‑Log):

- Configure `BEAMWARDEN_URL` (e.g. `http://beamwarden.local:8000`).
- Enable telemetry with an interval (e.g. 30 seconds).
- Confirm that heartbeats appear in the Beamwarden UI.

---

## 5. Day‑to‑Day Tasks for Operators

### 5.1 Monitor Fleet Health

From the Beamwarden dashboard, an operator can:

- See all nodes and their status (`online`, `degraded`, `offline`).
- Drill into a node to view telemetry history.
- Filter by role (e.g. all `pi-log` nodes).

### 5.2 Manage Deployments

For LogExp deployments:

- Beamwarden tracks which nodes run which LogExp version.
- Operators can schedule or trigger an upgrade.
- Deployment status is visible in the UI.

### 5.3 Manage SSH Access (Future Epic)

- Generate and rotate keys.
- Assign keys to nodes.
- Audit who can access what.

---

## 6. Operator Mental Model

- **Pi‑Log:** Talks to hardware, sends readings + telemetry.
- **LogExp:** Processes readings, exposes diagnostics.
- **Beamwarden:** Watches everything, coordinates changes.

Operators primarily live in Beamwarden; Pi‑Log and LogExp are managed assets.

---

## 7. Guardrails for Future Maintainers

- Beamwarden must remain the **source of truth** for:
  - Nodes
  - Roles
  - Versions
  - Telemetry aggregation
- LogExp and Pi‑Log should NOT maintain their own conflicting inventory.

If in doubt: _“If it’s about the fleet, it belongs in Beamwarden.”_

~~~~markdown

~~~~markdown
# LogExp v1 Release Plan

## 1. Definition of LogExp v1

LogExp v1 is the first **fleet‑ready** release that:

- Runs stably in containers on Pi and Linux.
- Accepts ingestion from Pi‑Log.
- Computes analytics deterministically.
- Exposes diagnostics and health endpoints.
- Integrates cleanly with Beamwarden (now or via well‑defined hooks).

---

## 2. Preconditions

- Step 12 completed (type safety, config hygiene, observability basics).
- CI‑HARD green, GitHub green.
- Postgres version alignment finalized (container + dev).
- No known nondeterministic tests.
- Container builds verified for ARM and x86.

---

## 3. Milestones

### 3.1 M1 — Container & Postgres Alignment

- Upgrade container to `postgres:18`.
- Verify migrations against Postgres 18.
- Ensure local dev and container use the same schema.

### 3.2 M2 — Pi‑to‑Pi Integration (Beamrider‑0001 → Beamrider‑0002)

- Run LogExp in a container on Beamrider‑0002.
- Run Pi‑Log on Beamrider‑0001.
- Ingest real readings into LogExp for 10–30 minutes.
- Confirm analytics + diagnostics behave as expected.

### 3.3 M3 — Telemetry & Diagnostics Completion

- `/api/health` exposes DB, ingestion, and analytics status.
- Diagnostics include basic node health (e.g. uptime, ingest rate).
- Structured logs in place for ingestion, analytics, diagnostics.

### 3.4 M4 — API & Schema Freeze

- Freeze ingestion payload schema.
- Freeze diagnostics payload schema.
- Document both in the LogExp README.

### 3.5 M5 — v1 Tag and Release

- Tag the repo (e.g. `logexp-v1.0.0`).
- Build and publish container images (local registry, tarballs, or future registry).
- Capture release notes:
  - features
  - known limitations
  - supported environments

---

## 4. Scope for v1 (Included)

- Single‑tenant LogExp instance per host.
- Pi‑Log → LogExp ingestion.
- Basic telemetry to Beamwarden (or ready hooks).
- Deterministic analytics and diagnostics.

---

## 5. Explicitly Out of Scope for v1

- Multi‑tenant management (that’s Beamwarden’s job).
- Fancy UI beyond necessary dashboards.
- Advanced alerting (will live in Beamwarden).
- Complex role‑based access (simple auth is sufficient).

---

## 6. Success Criteria

- LogExp can run for 30+ minutes under live Pi‑Log ingestion without:
  - ingestion failures,
  - DB errors,
  - analytics exceptions,
  - UI 500s,
  - runaway logs.
- A new developer can:
  - clone the repo,
  - follow the README,
  - run LogExp in Docker with Postgres 18,
  - replay a sample ingestion trace,
  - see analytics and diagnostics populate.

---

## 7. Post‑v1: Handoff to Beamwarden

After v1:

- LogExp becomes a **component** in the Beamwarden ecosystem.
- Future changes prioritize:
  - stability,
  - backward compatibility,
  - observability,
  - clean integration with Beamwarden control flows.
~~~~markdown

---

### Back to Postgres Work

Now, pivoting cleanly back to Postgres, here’s the concrete next step list for `feature/container-update`:

1. **Confirm versions:**
   - Inspect current container Postgres: `postgres:15` in your existing compose.
   - Target: move both container and local to Postgres 18.

2. **Update compose for Postgres 18:**
   - In your Mac and Linux/Pi compose files, change `image: postgres:15` → `image: postgres:18`.

3. **Blow away old container DB volume (on the feature branch only):**
   - `docker compose down -v` for the old stack so you’re not carrying a 15‑era data dir into 18.

4. **Run migrations against Postgres 18 locally:**
   - Bring up the new stack.
   - Run your migration command (e.g. `flask db upgrade` or equivalent).
   - Verify schema and basic app startup.

5. **Run full test suite pointing at Postgres 18:**
   - Use your CI‑HARD lane locally against the containerized Postgres.
   - Confirm no SQLite assumptions remain.

If you want, next turn we can walk file‑by‑file through updating your current `docker-compose.yml` on `feature/container-update` to a Postgres‑18‑aligned, telemetry‑ready version that’s safe to run on your Mac as the canonical reference.
