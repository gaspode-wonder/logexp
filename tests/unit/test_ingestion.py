import pytest
from logexp.app.ingestion import ingest_reading
from logexp.app.models import LogExpReading


@pytest.fixture
def parsed_factory():
    def _make(**overrides):
        base = {
            "counts_per_second": 1.0,
            "counts_per_minute": 60.0,
            "microsieverts_per_hour": 0.01,
            "mode": "test",
        }
        base.update(overrides)
        return base
    return _make


def test_ingest_reading_persists_row(test_app, db_session, parsed_factory):
    with test_app.app_context():
        reading = ingest_reading(parsed_factory())

        assert reading is not None
        assert isinstance(reading, LogExpReading)

        stored = db_session.query(LogExpReading).first()
        assert stored.counts_per_second == 1.0
        assert stored.mode == "test"


def test_ingestion_disabled_skips_write(test_app, db_session, parsed_factory):
    test_app.config_obj["INGESTION_ENABLED"] = False

    with test_app.app_context():
        reading = ingest_reading(parsed_factory(mode="disabled"))

        assert reading is None
        assert db_session.query(LogExpReading).count() == 0


def test_ingest_reading_rollback_on_error(test_app, db_session, monkeypatch, parsed_factory):
    def boom():
        raise RuntimeError("forced commit failure")

    monkeypatch.setattr("logexp.app.extensions.db.session.commit", boom)

    with test_app.app_context():
        with pytest.raises(RuntimeError):
            ingest_reading(parsed_factory(mode="error"))

        assert db_session.query(LogExpReading).count() == 0
