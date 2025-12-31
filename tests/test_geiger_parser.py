# tests/test_geiger_parser.py
from logexp.app.geiger import parse_geiger_line


def test_slow_mode_default():
    line = "CPS=10, CPM=600, uSv/h=0.12"
    parsed = parse_geiger_line(line, threshold=50)
    assert parsed["counts_per_second"] == 10
    assert parsed["counts_per_minute"] == 600
    assert parsed["microsieverts_per_hour"] == 0.12
    assert parsed["mode"] == "SLOW"


def test_fast_mode_threshold():
    line = "CPS=80, CPM=4800, uSv/h=0.25"
    parsed = parse_geiger_line(line, threshold=50)
    assert parsed["counts_per_second"] == 80
    assert parsed["mode"] == "FAST"


def test_inst_mode_high_cps():
    line = "CPS=300, CPM=0, uSv/h=0.5"
    parsed = parse_geiger_line(line, threshold=50)
    # CPS > 255 triggers INST mode and CPM = CPS*60
    assert parsed["mode"] == "INST"
    assert parsed["counts_per_minute"] == 300 * 60


def test_fallback_on_bad_line():
    line = "garbled output string"
    parsed = parse_geiger_line(line)
    # Should not crash, fallback mode is SLOW
    assert parsed["mode"] == "SLOW"
