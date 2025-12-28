import os


from flask import Flask, render_template, current_app
from logexp.app.config import load_config
from logexp.app.poller import GeigerPoller
from logexp.app.extensions import db, migrate
from logexp.app.blueprints import register_blueprints
from logexp.app.logging import configure_logging


"""
Application factory and high-level wiring.

Package layout:

- blueprints/: Flask route blueprints
- services/:  Core business logic and helpers
- models.py:  Database models
- extensions.py: Flask extensions (db, migrate, etc.)
"""

def create_app() -> Flask:
    app = Flask(__name__)

    # configure logging
    configure_logging(app)

    # Load centralized config
    app.config_obj = load_config()

    # Ensure a DB URI is set (tests may override later)
    app.config["SQLALCHEMY_DATABASE_URI"] = app.config_obj["SQLALCHEMY_DATABASE_URI"]

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register all blueprints
    register_blueprints(app)

    # ----------------------------------------------------------------------
    # POLLER-SAFE LOGIC FOR DOCKER + GUNICORN
    #
    # Gunicorn uses multiple workers unless configured otherwise.
    # We enforce workers=1 in gunicorn.conf.py, but we ALSO guard here
    # so the poller never starts accidentally in:
    #   - Docker builds
    #   - Gunicorn preload
    #   - Multiple workers
    #   - Environments where START_POLLER=False
    # ----------------------------------------------------------------------

    start_poller = app.config_obj["START_POLLER"]

    # Detect if running under Gunicorn
    running_under_gunicorn = "gunicorn" in os.environ.get("SERVER_SOFTWARE", "").lower()

    if start_poller and not running_under_gunicorn:
        app.logger.info("Starting GeigerPoller (safe mode).")
        app.poller = GeigerPoller(app)
        app.poller.start()
    else:
        app.logger.info("Poller disabled (START_POLLER=False or running under Gunicorn).")

    # ----------------------------------------------------------------------

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
        if app.config_obj["TESTING"] and getattr(app, "poller", None):
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
            current_app.logger.info("Geiger poller started.")
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

    # ----------------------------------------------------------------------
    # DOCKER-FRIENDLY SEED COMMAND
    #
    # This is the command your entrypoint.sh will call:
    #     flask seed-data
    #
    # It is idempotent and safe to run on every container start.
    # ----------------------------------------------------------------------
    @app.cli.command("seed-data")
    def seed_data():
        """Seed the database with sample data (idempotent)."""
        from logexp.seeds import seed_data
        seed_data.run(app)
        current_app.logger.info("Database seeded (idempotent).")

    @app.cli.command("clear-db")
    def clear_db():
        """Drop all tables and recreate an empty database."""
        with app.app_context():
            db.drop_all()
            db.create_all()
            current_app.logger.info("Test database cleared and recreated.")

    @app.context_processor
    def inject_globals():
        from datetime import datetime
        return {"current_year": datetime.now().year}

    return app
