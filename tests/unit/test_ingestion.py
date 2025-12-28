import pytest
from logexp.app.ingestion import ingest_reading
from logexp.app.models import LogExpReading


def test_ingest_reading_persists_row(test_app, db_session):
    """
    Ingestion should persist a parsed reading into the database
    when INGESTION_ENABLED=True.
    """
    with test_app.app_context():
        parsed = {
            "counts_per_second": 1.0,
            "counts_per_minute": 60.0,
            "microsieverts_per_hour": 0.01,
            "mode": "test",
        }

        reading = ingest_reading(parsed)

        # Verify the returned model instance
        assert reading is not None
        assert isinstance(reading, LogExpReading)

        # Verify DB persistence
        result = db_session.query(LogExpReading).first()
        assert result is not None
        assert result.counts_per_second == 1.0
        assert result.counts_per_minute == 60.0
        assert result.microsieverts_per_hour == 0.01
        assert result.mode == "test"


def test_ingestion_disabled_skips_write(test_app, db_session):
    """
    When INGESTION_ENABLED=False, ingest_reading() should not write to the DB.
    """
    test_app.config_obj["INGESTION_ENABLED"] = False

    with test_app.app_context():
        parsed = {
            "counts_per_second": 2.0,
            "counts_per_minute": 120.0,
            "microsieverts_per_hour": 0.02,
            "mode": "disabled",
        }

        reading = ingest_reading(parsed)

        # Should return None when ingestion is disabled
        assert reading is None

        # DB should remain empty
        assert db_session.query(LogExpReading).count() == 0


def test_ingest_reading_rollback_on_error(test_app, db_session, monkeypatch):
    """
    If ingestion raises an exception during commit, the transaction should roll back.
    """

    # Force db.session.commit() to raise an exception
    def boom():
        raise RuntimeError("forced commit failure")

    monkeypatch.setattr("logexp.app.extensions.db.session.commit", boom)

    with test_app.app_context():
        parsed = {
            "counts_per_second": 3.0,
            "counts_per_minute": 180.0,
            "microsieverts_per_hour": 0.03,
            "mode": "error",
        }

        with pytest.raises(RuntimeError):
            ingest_reading(parsed)

        # Ensure rollback occurred and DB is still empty
        assert db_session.query(LogExpReading).count() == 0
