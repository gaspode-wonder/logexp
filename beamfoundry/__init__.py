# filename: beamfoundry/__init__.py

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

"""
beamfoundry package root.

Exports create_app and wsgi_app lazily to avoid import-time side effects
during editable installs and CI bootstrap.
"""

if TYPE_CHECKING:
    # Only imported during type checking, never at runtime
    from flask import Flask


def create_app() -> "Flask":
    from app import create_app as _create_app

    return _create_app()


def wsgi_app() -> Callable[..., object]:
    from app import wsgi_app as _wsgi_app

    return _wsgi_app()


__all__ = ["create_app", "wsgi_app"]
