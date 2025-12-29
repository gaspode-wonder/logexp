# tests/test_models.py
"""
Model-level tests for LogExpReading.
"""

from datetime import datetime, timezone

from logexp.app.models import LogExpReading


def test_to_dict_returns_expected_fields(test_app, db_session):
    with test_app.app_context():
        r = LogExpReading(
            timestamp=datetime.now(timezone.utc).isoformat(),
            counts_per_second=1.5,
            counts_per_minute=90.0,
            microsieverts_per_hour=0.02,
            mode="normal",
        )
        db_session.add(r)
        db_session.commit()

        as_dict = r.to_dict()

        assert set(as_dict.keys()) == {
            "id",
            "timestamp",
            "counts_per_second",
            "counts_per_minute",
            "microsieverts_per_hour",
            "mode",
        }
        assert as_dict["counts_per_second"] == 1.5
        assert as_dict["mode"] == "normal"


def test_logexp_reading_model(test_app, db_session):
    with test_app.app_context():
        r = LogExpReading(
            timestamp=datetime.now(timezone.utc).isoformat(),
            counts_per_second=2.0,
            counts_per_minute=120.0,
            microsieverts_per_hour=0.03,
            mode="test",
        )
        db_session.add(r)
        db_session.commit()

        fetched = db_session.query(LogExpReading).first()
        assert fetched is not None
        assert fetched.counts_per_second == 2.0
        assert fetched.mode == "test"
        assert fetched.timestamp_dt.tzinfo is not None
