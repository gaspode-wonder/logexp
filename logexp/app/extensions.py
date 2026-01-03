# filename: logexp/app/extensions.py

from __future__ import annotations

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# SQLAlchemy and Migrate extensions used across the application.
db: SQLAlchemy = SQLAlchemy()
migrate: Migrate = Migrate()
