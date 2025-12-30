from logexp.app import create_app
from logexp.app.extensions import db
from logexp.app.services.analytics import run_analytics


def main():
    app = create_app({
        "TESTING": True,
        "START_POLLER": False,
    })

    with app.app_context():
        result = run_analytics(db.session)

    print("Analytics demo complete:", result)


if __name__ == "__main__":
    main()
