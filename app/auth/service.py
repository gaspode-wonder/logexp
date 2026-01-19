# filename: app/auth/service.py

from __future__ import annotations

from typing import Optional, cast

from app.extensions import db
from app.models import User


def authenticate(username: str, password: str) -> Optional[User]:
    result = User.query.filter_by(username=username).first()
    user = cast(Optional[User], result)

    if user is None:
        return None
    if not user.check_password(password):
        return None
    return user


def get_user_by_id(user_id: int) -> Optional[User]:
    result = User.query.get(user_id)
    return cast(Optional[User], result)


def create_user(username: str, password: str) -> User:
    user = User(username=username, password_hash="")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user
