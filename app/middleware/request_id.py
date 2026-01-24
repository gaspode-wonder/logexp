# filename: app/middleware/request_id.py

from __future__ import annotations

from typing import cast

from flask import Flask, Response, request

from ..logging_setup import get_logger
from ..typing import LogExpRequest

logger = get_logger("beamfoundry.middleware.request_id")


def request_id_middleware(app: Flask) -> None:
    @app.before_request
    def attach_request_id() -> None:
        req = cast(LogExpRequest, request)
        req.request_id = req.headers.get("X-Request-ID", "unknown")

    @app.after_request
    def add_request_id_header(response: Response) -> Response:
        req = cast(LogExpRequest, request)
        response.headers["X-Request-ID"] = getattr(req, "request_id", "unknown")
        return response
