# filename: app/extensions.py

from __future__ import annotations

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from app.db_types import Base

db: SQLAlchemy = SQLAlchemy(model_class=Base)
migrate: Migrate = Migrate()
