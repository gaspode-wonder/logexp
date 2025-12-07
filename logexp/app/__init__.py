from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from logexp.config import Config

db = SQLAlchemy()

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    # Register routes
    from logexp.app.routes import bp as readings_bp
    app.register_blueprint(readings_bp)

    return app
