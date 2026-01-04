# filename: tests/unit/parser/test_mightyohm_parser.py

from logexp.parsers.mightyohm import parse_mightyohm_csv


def test_mightyohm_valid_line():
    raw = "CPS, 12, CPM, 720, uSv/hr, 0.12, SLOW"
    out = parse_mightyohm_csv(raw)
    assert out == {
        "raw": raw,
        "cps": 12,
        "cpm": 720,
        "usv": 0.12,
        "mode": "SLOW",
    }


def test_mightyohm_whitespace_tolerance():
    raw = "  CPS ,12 , CPM ,720 , uSv/hr ,0.12 , FAST "
    out = parse_mightyohm_csv(raw)
    assert out["mode"] == "FAST"
    assert out["cps"] == 12
    assert out["cpm"] == 720
    assert out["usv"] == 0.12


def test_mightyohm_mode_case_insensitive():
    raw = "CPS, 5, CPM, 300, uSv/hr, 0.05, inst"
    out = parse_mightyohm_csv(raw)
    assert out["mode"] == "INST"


def test_mightyohm_invalid_literals():
    assert parse_mightyohm_csv("XYZ, 1, CPM, 60, uSv/hr, 0.1, SLOW") is None
    assert parse_mightyohm_csv("CPS, 1, XYZ, 60, uSv/hr, 0.1, SLOW") is None
    assert parse_mightyohm_csv("CPS, 1, CPM, 60, XYZ, 0.1, SLOW") is None


def test_mightyohm_wrong_field_count():
    assert parse_mightyohm_csv("CPS, 1, CPM, 60, uSv/hr, 0.1") is None


def test_mightyohm_non_numeric_values():
    assert parse_mightyohm_csv("CPS, x, CPM, 60, uSv/hr, 0.1, SLOW") is None
    assert parse_mightyohm_csv("CPS, 1, CPM, y, uSv/hr, 0.1, SLOW") is None
    assert parse_mightyohm_csv("CPS, 1, CPM, 60, uSv/hr, z, SLOW") is None


def test_mightyohm_negative_usv_rejected():
    assert parse_mightyohm_csv("CPS, 1, CPM, 60, uSv/hr, -0.1, SLOW") is None


def test_mightyohm_invalid_mode():
    assert parse_mightyohm_csv("CPS, 1, CPM, 60, uSv/hr, 0.1, TURBO") is None


def test_mightyohm_empty_or_non_string():
    assert parse_mightyohm_csv("") is None
    assert parse_mightyohm_csv(None) is None
    assert parse_mightyohm_csv(123) is None
