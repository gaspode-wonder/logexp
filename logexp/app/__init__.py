from flask import Flask
from logexp.app.config import Config
from logexp.app.poller import GeigerPoller
from logexp.app.extensions import db, migrate

poller = None  # global reference

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # init db + migrations
    db.init_app(app)
    migrate.init_app(app, db)

    from logexp.app.routes import bp as readings_bp
    app.register_blueprint(readings_bp)

    global poller
    poller = GeigerPoller(app)
    poller.start()

    @app.teardown_appcontext
    def shutdown_poller(exception=None):
        if poller:
            try:
                poller.stop()
            except RuntimeError:
                # Ignore "cannot join current thread" if teardown is inside poller thread
                app.logger.debug("Poller stop called from within poller thread; skipping join.")



    # ✅ CLI commands
    @app.cli.command("geiger-start")
    def geiger_start():
        """Start the Geiger poller manually."""
        global poller
        if poller and not poller._thread.is_alive():
            poller.start()
            print("Geiger poller started.")
        else:
            print("Poller already running.")

    @app.cli.command("geiger-stop")
    def geiger_stop():
        """Stop the Geiger poller manually."""
        global poller
        if poller:
            poller.stop()
            print("Geiger poller stopped.")
        else:
            print("No poller instance found.")

    return app
