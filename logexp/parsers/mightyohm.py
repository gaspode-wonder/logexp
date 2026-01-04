# filename: logexp/parsers/mightyohm.py

from __future__ import annotations

VALID_MODES = {"SLOW", "FAST", "INST"}


def parse_mightyohm_csv(raw):
    if not isinstance(raw, str) or not raw.strip():
        return None

    parts = [p.strip() for p in raw.split(",")]
    if len(parts) != 7:
        return None

    if parts[0] != "CPS":
        return None
    if parts[2] != "CPM":
        return None

    # tolerant uSv/hr check
    if parts[4].lower().replace(" ", "") != "usv/hr":
        return None

    try:
        cps = int(parts[1])
        cpm = int(parts[3])
        usv = float(parts[5])
    except ValueError:
        return None

    if cps < 0 or cpm < 0 or usv < 0:
        return None

    mode = parts[6].upper()
    if mode not in VALID_MODES:
        return None

    print("DEBUG RAW:", repr(raw))
    print("DEBUG PARTS:", [p.strip() for p in raw.split(",")])

    return {
        "raw": raw,
        "cps": cps,
        "cpm": cpm,
        "usv": usv,
        "mode": mode,
    }
