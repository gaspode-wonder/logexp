# filename: logexp/app/auth/service.py

from typing import Optional

from logexp.app.models import User


def authenticate(username: str, password: str) -> Optional[User]:
    """
    Look up a user and verify their password.
    Returns the User instance if valid, otherwise None.
    """
    user: User | None = User.query.filter_by(username=username).first()
    if user is None:
        return None

    if not user.check_password(password):
        return None

    return user
