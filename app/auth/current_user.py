# filename: app/auth/current_user.py

from __future__ import annotations

from typing import Optional

from flask_login import current_user as flask_current_user

from app.models import User


def get_current_user() -> Optional[User]:
    """Typed wrapper around flask_login.current_user."""
    if flask_current_user.is_authenticated:
        return flask_current_user  # type: ignore[no-any-return]
    return None
