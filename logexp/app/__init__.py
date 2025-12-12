from flask import Flask, render_template, current_app
from logexp.app.config import Config
from logexp.app.poller import GeigerPoller
from logexp.app.extensions import db, migrate
from logexp.app.app_blueprints import register_blueprints


def create_app(config_object: type = Config) -> Flask:
    """Application factory for LogExp."""
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Ensure a DB URI is set (tests may override later)
    app.config.setdefault("SQLALCHEMY_DATABASE_URI", "sqlite:///:memory:")

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register all blueprints
    register_blueprints(app)

    # Attach poller only if allowed
    if app.config.get("START_POLLER", True):
        app.poller = GeigerPoller(app)
        app.poller.start()

    # --- Error handlers ---
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500

    # --- Teardown ---
    @app.teardown_appcontext
    def shutdown_poller(exception=None):
        """Stop poller cleanly in testing contexts."""
        if app.config.get("TESTING", False) and getattr(app, "poller", None):
            try:
                app.poller.stop()
            except RuntimeError:
                app.logger.debug(
                    "Poller stop called from within poller thread; skipping join."
                )

    # --- CLI commands ---
    @app.cli.command("geiger-start")
    def geiger_start():
        """Start the Geiger poller manually."""
        poller = getattr(current_app, "poller", None)
        if poller and not poller._thread.is_alive():
            poller.start()
            print("Geiger poller started.")
        else:
            print("Poller already running.")

    @app.cli.command("geiger-stop")
    def geiger_stop():
        """Stop the Geiger poller manually."""
        poller = getattr(current_app, "poller", None)
        if poller and poller._thread.is_alive():
            poller.stop()
            print("Geiger poller stopped.")
        else:
            print("Poller not running.")

    @app.cli.command("seed")
    def seed():
        """Seed the database with sample data (manual only)."""
        from logexp.seeds import seed_data
        seed_data.run(app)  # pass the current app explicitly
        print("Database seeded.")

    @app.cli.command("clear-db")
    def clear_db():
        """Drop all tables and recreate an empty database."""
        with app.app_context():
            db.drop_all()
            db.create_all()
            print("Test database cleared and recreated.")

    return app
