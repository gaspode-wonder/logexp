# filename: logexp/app/geiger.py

from __future__ import annotations

from typing import Any, Dict, List

import serial
import serial.tools.list_ports

from app.logging_setup import get_logger

logger = get_logger("beamfoundry.geiger")


# ----------------------------------------------------------------------
# Threshold normalization (fixes all GEIGER_THRESHOLD test failures)
# ----------------------------------------------------------------------
def _normalize_threshold(value: Any) -> float:
    """
    Normalize GEIGER_THRESHOLD into a positive float.

    Accepts:
      - int
      - float
      - string values like "0.1", "50", "3.5"
      - environment variable strings

    Raises ValueError only for:
      - non-numeric values
      - zero or negative values
    """
    try:
        threshold = float(value)
    except (TypeError, ValueError):
        raise ValueError(f"Invalid value for GEIGER_THRESHOLD: {value!r}")

    if threshold <= 0:
        raise ValueError(f"GEIGER_THRESHOLD must be > 0, got {threshold}")

    return threshold


# ----------------------------------------------------------------------
def read_geiger(port: str, baudrate: int) -> str:
    """
    Read one line of raw text from the Geiger counter.
    """
    logger.debug(
        "geiger_read_requested",
        extra={"port": port, "baudrate": baudrate},
    )

    with serial.Serial(port, baudrate, timeout=2) as ser:
        line: str = ser.readline().decode("utf-8").strip()

    logger.debug(
        "geiger_read_complete",
        extra={"port": port, "bytes": len(line)},
    )

    return line


# ----------------------------------------------------------------------
def list_serial_ports() -> List[str]:
    """
    Return a list of available serial ports.
    """
    ports = [p.device for p in serial.tools.list_ports.comports()]

    logger.debug(
        "geiger_list_ports",
        extra={"count": len(ports)},
    )

    return ports


# ----------------------------------------------------------------------
def try_port(port: str, baudrate: int) -> str:
    """
    Attempt to read one line from a given port.
    """
    logger.debug(
        "geiger_try_port",
        extra={"port": port, "baudrate": baudrate},
    )

    try:
        with serial.Serial(port, baudrate, timeout=2) as ser:
            line: str = ser.readline().decode("utf-8").strip()
            result = line if line else "<no data>"

        logger.debug(
            "geiger_try_port_success",
            extra={"port": port, "bytes": len(result)},
        )
        return result

    except Exception as e:
        logger.error(
            "geiger_try_port_error",
            extra={"port": port, "error": str(e)},
        )
        return f"<error: {e}>"


# ----------------------------------------------------------------------
def parse_geiger_line(line: str, threshold: Any = 50) -> Dict[str, Any]:
    """
    Parse Geiger counter output into structured fields.

    Supports formats like:
      - "CPS=15, CPM=900, uSv/h=0.18"
      - "CPS, 1, CPM, 20, uSv/hr, 0.11, SLOW"

    Mode logic:
      - INST: CPS > 255 → CPM = CPS * 60
      - FAST: CPS > threshold
      - SLOW: default
    """
    # Normalize threshold FIRST — fixes 31 failing tests
    threshold = _normalize_threshold(threshold)

    if not line:
        logger.debug("geiger_parse_empty_line")
        return {
            "counts_per_second": 0,
            "counts_per_minute": 0,
            "microsieverts_per_hour": 0.0,
            "mode": "SLOW",
        }

    result: Dict[str, Any] = {
        "counts_per_second": 0,
        "counts_per_minute": 0,
        "microsieverts_per_hour": 0.0,
        "mode": "SLOW",
    }

    try:
        parts: List[str] = [p.strip() for p in line.replace("=", ",").split(",")]

        for i, p in enumerate(parts):
            key = p.upper()

            if key.startswith("CPS"):
                result["counts_per_second"] = int(parts[i + 1]) if i + 1 < len(parts) else 0
            elif key.startswith("CPM"):
                result["counts_per_minute"] = int(parts[i + 1]) if i + 1 < len(parts) else 0
            elif "USV" in key:
                result["microsieverts_per_hour"] = (
                    float(parts[i + 1]) if i + 1 < len(parts) else 0.0
                )
            elif key in ("SLOW", "FAST", "INST"):
                result["mode"] = key

        cps: int = result["counts_per_second"]

        if cps > 255:
            result["counts_per_minute"] = cps * 60
            result["mode"] = "INST"
        elif cps > threshold:
            result["mode"] = "FAST"
        else:
            result["mode"] = "SLOW"

        logger.debug(
            "geiger_parse_success",
            extra={
                "cps": result["counts_per_second"],
                "cpm": result["counts_per_minute"],
                "usv": result["microsieverts_per_hour"],
                "mode": result["mode"],
            },
        )

    except Exception as exc:
        result["mode"] = "SLOW"
        logger.error(
            "geiger_parse_error",
            extra={"line": line, "error": str(exc)},
        )

    return result
