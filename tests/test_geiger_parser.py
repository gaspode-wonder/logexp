# tests/test_geiger_parser.py
"""
Tests for Geiger counter parsing logic.
"""

from logexp.app.geiger import parse_geiger_line


def test_parse_basic_format():
    line = "CPS=15, CPM=900, uSv/h=0.18"
    parsed = parse_geiger_line(line)

    assert parsed["counts_per_second"] == 15
    assert parsed["counts_per_minute"] == 900
    assert parsed["microsieverts_per_hour"] == 0.18
    assert parsed["mode"] == "SLOW"  # 15 <= threshold


def test_parse_alt_format_with_mode():
    line = "CPS, 1, CPM, 20, uSv/hr, 0.11, SLOW"
    parsed = parse_geiger_line(line)

    assert parsed["counts_per_second"] == 1
    assert parsed["counts_per_minute"] == 20
    assert parsed["microsieverts_per_hour"] == 0.11
    assert parsed["mode"] == "SLOW"


def test_fast_mode_threshold():
    # threshold default = 50
    line = "CPS=75, CPM=4500, uSv/h=0.22"
    parsed = parse_geiger_line(line)

    assert parsed["counts_per_second"] == 75
    assert parsed["mode"] == "FAST"


def test_inst_mode_high_cps():
    line = "CPS=300, CPM=0, uSv/h=0.15"
    parsed = parse_geiger_line(line)

    assert parsed["counts_per_second"] == 300
    assert parsed["counts_per_minute"] == 300 * 60  # INST override
    assert parsed["mode"] == "INST"


def test_empty_line_returns_defaults():
    parsed = parse_geiger_line("")
