from datetime import datetime, timedelta
from logexp.app import create_app, db
from logexp.app.models import LogExpReading

def run():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()

        base = datetime.utcnow().replace(second=0, microsecond=0)
        samples = [
            LogExpReading(counts_per_second=12, counts_per_minute=720, microsieverts_per_hour=0.15, mode="normal",  timestamp=base),
            LogExpReading(counts_per_second=18, counts_per_minute=1080, microsieverts_per_hour=0.22, mode="normal",  timestamp=base + timedelta(minutes=1)),
            LogExpReading(counts_per_second=25, counts_per_minute=1500, microsieverts_per_hour=0.35, mode="alert",   timestamp=base + timedelta(minutes=2)),
            LogExpReading(counts_per_second=8,  counts_per_minute=480, microsieverts_per_hour=0.10, mode="normal",  timestamp=base + timedelta(minutes=3)),
            LogExpReading(counts_per_second=40, counts_per_minute=2400, microsieverts_per_hour=0.60, mode="critical",timestamp=base + timedelta(minutes=4)),
        ]

        db.session.add_all(samples)
        db.session.commit()
        print("Seeded 5 readings.")

if __name__ == "__main__":
    run()
