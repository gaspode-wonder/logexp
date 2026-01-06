
# Pi‑Log → LogExp Integration v2 Checklist
Distributed Architecture — No Local Serial Dependencies

## Goal
Stand up LogExp as a clean network service and connect Pi‑Log to it over the LAN, validating ingestion, storage, analytics, and diagnostics under real hardware conditions.

---

## 1. Prepare LogExp (Host Machine)

### 1.1. Remove all local serial/bridge references
- Delete any `GEIGER_PORT` pointing to `/dev/ttyUSB0` or a macOS PTY.
- Remove any `devices:` or bind‑mounts referencing `~/.geiger-bridge`.
- Ensure LogExp runs without expecting local hardware.

### 1.2. Start the LogExp stack
~~~bash
docker compose down --volumes
docker compose up --build -d
~~~

### 1.3. Confirm health
- `db` reports: **database system is ready to accept connections**
- `logexp_app` healthcheck passes

### 1.4. Confirm LogExp is reachable on the LAN
~~~bash
curl http://localhost:5000/api/health
curl http://<host-ip>:5000/api/health
~~~

Find host IP:
~~~bash
ipconfig getifaddr en0
~~~

---

## 2. Prepare Pi‑Log (Beamrider‑0001)

### 2.1. Confirm Pi‑Log hardware is functional
- `/dev/ttyUSB0` exists
- Geiger counter produces serial output
- Pi‑Log can read raw lines locally

### 2.2. Configure Pi‑Log to point to LogExp
~~~bash
LOGEXP_URL=http://<host-ip>:5000/api/readings
LOGEXP_NODE_ID=beamrider-0001
~~~

### 2.3. Restart Pi‑Log
~~~bash
sudo systemctl restart pi-log
~~~

### 2.4. Watch Pi‑Log logs
~~~bash
journalctl -u pi-log -f
~~~

Look for:
- successful HTTP POSTs
- no connection errors

---

## 3. Validate Ingestion on LogExp

### 3.1. Watch LogExp logs
~~~bash
docker compose logs -f logexp
~~~

Expect:
- inbound POSTs from Pi‑Log
- ingestion success messages

### 3.2. Validate DB writes
~~~bash
docker compose exec db psql -U logexp -d logexp \
  -c "SELECT * FROM readings ORDER BY id DESC LIMIT 5;"
~~~

Expect:
- rows with `node_id = 'beamrider-0001'`
- timestamps matching Pi‑Log output

---

## 4. Validate Analytics + Diagnostics

### 4.1. Hit analytics endpoint
~~~bash
curl http://<host-ip>:5000/api/analytics
~~~

### 4.2. Hit diagnostics endpoint
~~~bash
curl http://<host-ip>:5000/api/diagnostics
~~~

Expect:
- valid JSON
- no 500s
- live ingestion reflected in metrics

---

## 5. Stability Run

### 5.1. Let the system run for 10–30 minutes
Confirm:
- no ingestion failures
- no DB errors
- no UI 500s
- no analytics exceptions
- no runaway logs

### 5.2. Validate long‑running ingestion
~~~bash
docker compose exec db psql -U logexp -d logexp \
  -c "SELECT COUNT(*) FROM readings;"
~~~

Expect:
- steadily increasing count

---

## 6. Integration Documentation

### 6.1. Document Pi‑Log → LogExp network configuration
- required env vars
- ingestion endpoint
- node identity

### 6.2. Document troubleshooting
- network reachability
- DB validation
- log locations
- common failure modes

### 6.3. Add “Distributed Integration” section to README

---

## Exit Criteria
- Pi‑Log sends real readings to LogExp continuously
- LogExp stores readings without error
- UI displays live data
- Analytics pipeline processes live data
- Diagnostics accurately reflect system state
- System remains stable under continuous operation




# Pi‑Log → LogExp Integration v1 Checklist

## Purpose
Validate the full, real‑hardware ingestion pipeline from the Raspberry Pi’s `pi-log` process into the LogExp application, ensuring stable, continuous, correct data flow across serial, network, API, database, analytics, diagnostics, and UI layers.

## 1. Raspberry Pi Environment Verification
- Confirm Pi boots cleanly and is reachable over SSH.
- Validate Python version and virtual environment on the Pi.
- Confirm Geiger counter is connected and producing serial output.
- Run a raw serial read test (`cat /dev/ttyUSB0` or equivalent) to confirm live data.
- Verify correct device path (`GEIGER_PORT`) and baud rate (`GEIGER_BAUDRATE`).

## 2. Pi‑Log Configuration
- Set `PI_LOG_TARGET_URL` to LogExp’s ingestion endpoint (`/api/readings`).
- Export all required environment variables for pi‑log.
- Run pi‑log in dry‑run mode to validate payload formatting.
- Confirm pi‑log can reach LogExp over the network (curl test).

## 3. LogExp Ingestion Enablement
- Ensure `SQLALCHEMY_DATABASE_URI` is set and DB tables created.
- Export ingestion‑related environment variables on LogExp host.
- Hit `/api/readings` with a manual POST to confirm ingestion path works.
- Validate DB writes and confirm rows appear in `logexp_readings`.

## 4. Live Integration Test
- Start pi‑log on the Pi with real serial input.
- Observe ingestion logs on LogExp for successful POSTs.
- Confirm readings appear in `/readings` UI.
- Confirm analytics update in `/analytics`.
- Confirm diagnostics reflect ingestion state and serial config.

## 5. Poller + Ingestion Interaction
- Validate poller thread does not conflict with ingestion.
- Confirm settings page reflects correct serial configuration.
- Validate error handling for intermittent serial failures.
- Confirm no runaway poller logs or repeated KeyErrors.

## 6. Stability Run
- Let the system run for 10–30 minutes.
- Confirm:
  - No ingestion failures.
  - No DB errors.
  - No UI 500s.
  - No analytics exceptions.
  - No poller instability.
- Validate that LogExp remains responsive under continuous ingestion.

## 7. Documentation
- Document Pi setup, environment variables, and startup commands.
- Document ingestion API contract and expected payloads.
- Document troubleshooting steps for serial, network, and DB issues.
- Add a “Live Integration” section to the LogExp README.
