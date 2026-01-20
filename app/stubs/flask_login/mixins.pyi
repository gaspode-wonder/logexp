from typing import Any, Protocol

class UserMixin(Protocol):
    id: Any
    is_authenticated: bool
    is_active: bool
    is_anonymous: bool

    def get_id(self) -> str: ...
