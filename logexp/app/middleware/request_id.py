# filename: logexp/app/middleware/request_id.py

from __future__ import annotations

import uuid
from typing import cast

from flask import Flask, Response, request

from logexp.app.logging_setup import get_logger
from logexp.app.typing import LogExpRequest

logger = get_logger("logexp.middleware.request_id")


def request_id_middleware(app: Flask) -> None:
    """
    Assigns a unique request ID to each request and exposes it via
    request.request_id and the X-Request-ID response header.
    """

    def assign_request_id() -> None:
        req_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        cast(LogExpRequest, request).request_id = req_id
        logger.debug("request_id_assigned", extra={"request_id": req_id})

    def add_request_id_header(response: Response) -> Response:
        req_id = getattr(request, "request_id", None)
        if req_id:
            response.headers["X-Request-ID"] = req_id
        return response

    app.before_request(assign_request_id)
    app.after_request(add_request_id_header)
