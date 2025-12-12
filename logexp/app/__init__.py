from flask import Flask, render_template, current_app
from logexp.app.config import Config
from logexp.app.poller import GeigerPoller
from logexp.app.extensions import db, migrate
from logexp.app.blueprints import register_blueprints

def create_app(config_object=Config):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Ensure a DB URI is set (tests may override later)
    if not app.config.get("SQLALCHEMY_DATABASE_URI"):
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    # init db + migrations
    db.init_app(app)
    migrate.init_app(app, db)

    # register all blueprints
    register_blueprints(app)

    # attach poller only if allowed
    if app.config.get("START_POLLER", True):
        app.poller = GeigerPoller(app)
        app.poller.start()

    @app.teardown_appcontext
    def shutdown_poller(exception=None):
        if app.config.get("TESTING", False):
            if hasattr(app, "poller") and app.poller:
                try:
                    app.poller.stop()
                except RuntimeError:
                    app.logger.debug("Poller stop called from within poller thread; skipping join.")

    # error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(403)
    def forbidden_error(error):
        return render_template("errors/403.html"), 403

    @app.errorhandler(500)
    def internal_error(error):
        return render_template("errors/500.html"), 500

    # CLI commands
    @app.cli.command("geiger-start")
    def geiger_start():
        """Start the Geiger poller manually."""
        poller = current_app.poller
        if poller and not poller._thread.is_alive():
            poller.start()
            print("Geiger poller started.")
        else:
            print("Poller already running.")

    @app.cli.command("geiger-stop")
    def geiger_stop():
        """Stop the Geiger poller manually."""
        poller = current_app.poller
        if poller and poller._thread.is_alive():
            poller.stop()
            print("Geiger poller stopped.")
        else:
            print("Poller not running.")

    @app.cli.command("seed")
    def seed():
        """Seed the database with sample data (manual only)."""
        from logexp.seeds import seed_data
        seed_data.run(app)   # ✅ pass the current app explicitly
        print("Database seeded.")

    @app.cli.command("clear-db")
    def clear_db():
        """Drop all tables and recreate an empty database."""
        with app.app_context():
            db.drop_all()
            db.create_all()
            print("Test database cleared and recreated.")

    return app
