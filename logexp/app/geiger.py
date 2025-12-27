from __future__ import annotations

import serial
import serial.tools.list_ports
from typing import Dict, List


def read_geiger(port: str = "/dev/tty.usbserial-AB9R9IYS", baudrate: int = 9600) -> str:
    """Read one line of raw text from the Geiger counter."""
    with serial.Serial(port, baudrate, timeout=2) as ser:
        line = ser.readline().decode("utf-8").strip()
        return line


def list_serial_ports() -> List[str]:
    """Return a list of available serial ports."""
    return [p.device for p in serial.tools.list_ports.comports()]


def try_port(port: str, baudrate: int = 9600) -> str:
    """Attempt to read one line from a given port."""
    try:
        with serial.Serial(port, baudrate, timeout=2) as ser:
            line = ser.readline().decode("utf-8").strip()
            return line if line else "<no data>"
    except Exception as e:
        return f"<error: {e}>"


def parse_geiger_line(line: str, threshold: int = 50) -> Dict[str, object]:
    """
    Parse Geiger counter output into structured fields.

    Supports formats like:
      - "CPS=15, CPM=900, uSv/h=0.18"
      - "CPS, 1, CPM, 20, uSv/hr, 0.11, SLOW"

    Mode logic:
      - INST: CPS > 255 → CPM = CPS*60
      - FAST: CPS > threshold
      - SLOW: default
    """
    result = {
        "counts_per_second": 0,
        "counts_per_minute": 0,
        "microsieverts_per_hour": 0.0,
        "mode": "SLOW",
    }

    if not line:
        return result

    try:
        parts = [p.strip() for p in line.replace("=", ",").split(",")]

        for i, p in enumerate(parts):
            if p.upper().startswith("CPS"):
                result["counts_per_second"] = int(parts[i + 1]) if i + 1 < len(parts) else 0
            elif p.upper().startswith("CPM"):
                result["counts_per_minute"] = int(parts[i + 1]) if i + 1 < len(parts) else 0
            elif "USV" in p.upper():
                result["microsieverts_per_hour"] = float(parts[i + 1]) if i + 1 < len(parts) else 0.0
            elif p.upper() in ("SLOW", "FAST", "INST"):
                result["mode"] = p.upper()

        # Mode logic
        cps = result["counts_per_second"]
        if cps > 255:
            result["counts_per_minute"] = cps * 60
            result["mode"] = "INST"
        elif cps > threshold:
            result["mode"] = "FAST"
        else:
            result["mode"] = "SLOW"

    except Exception:
        # Fallback: keep defaults
        result["mode"] = "SLOW"

    return result