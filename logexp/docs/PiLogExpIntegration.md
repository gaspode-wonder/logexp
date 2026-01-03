
# Pi‑Log → LogExp Integration Checklist

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
