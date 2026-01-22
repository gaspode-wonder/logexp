# app/stubs/flask_login/__init__.pyi

from typing import Any, Callable, Optional, TypeVar

from .mixins import UserMixin

_T = TypeVar("_T")

class LoginManager:
    login_view: Optional[str]
    def __init__(self, app: Any | None = None) -> None: ...
    def init_app(self, app: Any) -> None: ...
    def user_loader(self, callback: Callable[[str], Any]) -> Callable[[str], Any]: ...
    def request_loader(self, callback: Callable[[Any], Any]) -> Callable[[Any], Any]: ...

def login_required(func: _T) -> _T: ...
def login_user(
    user: Any, remember: bool = False, duration: Any = None, force: bool = False, fresh: bool = True
) -> None: ...
def logout_user() -> None: ...

current_user: Any

__all__ = [
    "UserMixin",
    "LoginManager",
    "login_required",
    "login_user",
    "logout_user",
    "current_user",
]
