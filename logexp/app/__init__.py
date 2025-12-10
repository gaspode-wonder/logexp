from flask import Flask, render_template, current_app
from logexp.app.config import Config
from logexp.app.poller import GeigerPoller
from logexp.app.extensions import db, migrate
from logexp.app.blueprints import register_blueprints

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # init db + migrations
    db.init_app(app)
    migrate.init_app(app, db)

    # register all blueprints
    register_blueprints(app)

    # attach poller to app instance
    app.poller = GeigerPoller(app)
    app.poller.start()

    @app.teardown_appcontext
    def shutdown_poller(exception=None):
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

    return app
