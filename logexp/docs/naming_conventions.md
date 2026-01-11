# Naming Conventions — Beamwarden Ecosystem
# January 2026 — Canonical Reference

This document defines the official naming conventions for all nodes, roles, services, and identifiers in the Beamwarden ecosystem.

---

# 1. Node Classes

## 1.1 Emitters
Physical radiation sources.
- No hostname
- No identity
- No software

## 1.2 Beamriders
Edge devices that read sensors and send BEAMS upstream.
- Hostname format: `beamrider-XXXX`
- Example: `beamrider-0001`
- Role: `pi-log`
- Responsibilities:
  - Serial read from Geiger tube
  - Normalize + timestamp
  - POST to KEEP
  - Local buffering
  - Heartbeat (future)

## 1.3 KEEP (Central Hub)
The fortified ingestion + analytics node.
- Hostname format: `keep-XXXX`
- Example: `keep-0001`
- Role: `logexp`
- Responsibilities:
  - Run LogExp
  - Ingestion API
  - Analytics engine
  - Diagnostics
  - Local telemetry
  - Postgres 18
  - Automatic restart on reboot

## 1.4 Beamwarden (Control Plane)
Fleet manager and orchestration layer.
- Hostname format: `beamwarden-XXXX`
- Example: `beamwarden-0001`
- Role: `beamwarden`
- Responsibilities:
  - Inventory of all nodes
  - Telemetry aggregation
  - Deployment orchestration
  - Node health + status
  - Future OTA + RBAC

---

# 2. Service Names

## 2.1 Pi‑Log Service
- Systemd unit: `pi-log.service`
- Runs on Beamriders

## 2.2 LogExp Service
- Systemd unit: `logexp.service`
- Runs on KEEP nodes
- Must restart automatically on reboot

## 2.3 Beamwarden Service
- Systemd unit: `beamwarden.service`
- Runs on Beamwarden nodes

---

# 3. API Naming

## 3.1 Ingestion
- Path: `/api/readings`
- Producer: Beamrider
- Consumer: KEEP (LogExp)

## 3.2 Telemetry
- Path: `/api/telemetry`
- Producer: Beamrider or KEEP
- Consumer: Beamwarden

## 3.3 Node Registration
- Path: `/api/nodes/register`
- Producer: Beamrider or KEEP
- Consumer: Beamwarden

---

# 4. Versioning

## 4.1 Software Versions
- `pi-log-X.Y.Z`
- `logexp-X.Y.Z`
- `beamwarden-X.Y.Z`

## 4.2 Protocol Versions
- Optional field: `"protocol_version": "1.0"`

---

# 5. Hostname Rules

- Lowercase only
- Hyphen‑separated
- Zero‑padded numeric suffix
- Stable for lifetime of device
- Never reused after decommissioning

Examples:
- `beamrider-0001`
- `keep-0001`
- `beamwarden-0001`

---

# 6. Identity Rules

Each node reports:
- `node_id`
- `role`
- `hostname`
- `ip_address`
- `software_version`

Beamwarden is the **source of truth** for:
- node inventory
- roles
- versions
- telemetry history

---

# 7. Line in the Sand (Architecture Boundary)

After LogExp Step 13 + Step 14 + automatic restart support:

**LogExp becomes a stable component, not a platform.**
All future fleet‑level features move to Beamwarden.

This naming convention document reflects that boundary.
