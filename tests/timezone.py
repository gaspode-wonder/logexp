from datetime import datetime, timezone
from logexp.app.models import LogExpReading

def test_timestamp_serialization_is_utc():
    # Simulate a reading created at local Central time
    local = datetime(2025, 12, 12, 10, 30).astimezone()  # 10:30 CST
    reading = LogExpReading(
        timestamp=local.astimezone(timezone.utc),
        counts_per_second=1,
        counts_per_minute=60,
        microsieverts_per_hour=0.1,
        mode="test"
    )
    data = reading.to_dict()
    # JSON should show UTC (16:30Z)
    assert data["timestamp"].endswith("16:30:00Z")