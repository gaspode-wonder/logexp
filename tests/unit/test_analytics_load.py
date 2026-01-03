import datetime
import random

from logexp.app.extensions import db
from logexp.app.services.analytics import compute_window, run_analytics


def test_high_volume_readings(test_app, reading_factory):
    """
    Analytics should handle large numbers of readings without errors.
    """
    with test_app.app_context():
        now = datetime.datetime.now(datetime.timezone.utc)

        for _ in range(1000):
            ts = now - datetime.timedelta(seconds=random.randint(0, 120))
            reading_factory(ts, cps=random.randint(1, 100))

        db.session.commit()

        result = run_analytics()

        assert result is not None
        assert result["count"] > 0


def test_randomized_timestamps(test_app, reading_factory):
    """
    Analytics should correctly sort and process out-of-order timestamps.
    """
    with test_app.app_context():
        now = datetime.datetime.now(datetime.timezone.utc)

        timestamps = [
            now
            - datetime.timedelta(
                seconds=random.randint(
                    0, test_app.config_obj["ANALYTICS_WINDOW_SECONDS"] - 1
                )
            )
            for _ in range(200)
        ]
        random.shuffle(timestamps)

        for ts in timestamps:
            reading_factory(ts, cps=10)

        db.session.commit()

        result = run_analytics()

        assert result["count"] == len(timestamps)
        assert result["first_timestamp"] < result["last_timestamp"]


def test_large_window(test_app, reading_factory):
    """
    Analytics should respect large window sizes without performance issues.
    """
    with test_app.app_context():
        test_app.config_obj["ANALYTICS_WINDOW_SECONDS"] = 3600  # 1 hour

        now = datetime.datetime.now(datetime.timezone.utc)

        for _ in range(300):
            ts = now - datetime.timedelta(seconds=random.randint(0, 3500))
            reading_factory(ts, cps=5)

        db.session.commit()

        result = run_analytics()

        assert result["count"] > 0


def test_exact_cutoff_boundary(test_app, reading_factory):
    """
    A reading exactly at the cutoff timestamp should be included.
    """
    with test_app.app_context():
        window = test_app.config_obj["ANALYTICS_WINDOW_SECONDS"]
        now = datetime.datetime.now(datetime.timezone.utc)

        inside = now - datetime.timedelta(seconds=window)
        outside = now - datetime.timedelta(seconds=window + 1)

        reading_factory(inside, cps=10)
        reading_factory(outside, cps=20)

        db.session.commit()

        readings = compute_window(now=now)

        assert len(readings) == 1
        assert readings[0].counts_per_second == 10


def test_mixed_cps_values(test_app, reading_factory):
    """
    Analytics should compute correct averages even with noisy CPS values.
    """
    with test_app.app_context():
        now = datetime.datetime.now(datetime.timezone.utc)

        values = [1, 5, 10, 50, 100, 200, 500]
        for v in values:
            reading_factory(now, cps=v)

        db.session.commit()

        result = run_analytics()

        assert result["avg_cps"] == sum(values) / len(values)
