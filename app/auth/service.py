# filename: app/auth/service.py
from __future__ import annotations

from typing import Optional

from ..extensions import db
from ..models import User


def authenticate(username: str, password: str) -> Optional[User]:
    user = db.session.query(User).filter_by(username=username).first()

    if user is None:
        return None
    if not user.check_password(password):
        return None
    return user


def get_user_by_id(user_id: int) -> Optional[User]:
    # SQLAlchemy 2.0‑native get()
    return db.session.get(User, user_id)


def create_user(username: str, password: str) -> User:
    user = User(username=username, password_hash="")
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user
