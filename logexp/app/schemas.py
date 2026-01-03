# filename: logexp/app/schemas.py

from __future__ import annotations

from datetime import datetime

from typing import Any

from pydantic import BaseModel, Field

from logexp.app.logging_setup import get_logger

logger = get_logger("logexp.schemas")


class ReadingCreate(BaseModel):
    counts_per_second: int = Field(..., gt=0)
    counts_per_minute: int = Field(..., gt=0)
    microsieverts_per_hour: float = Field(..., gt=0)
    mode: str = Field(..., min_length=1)

    def model_post_init(self, __context: Any) -> None:
        logger.debug(
            "reading_create_validated",
            extra={
                "cps": self.counts_per_second,
                "cpm": self.counts_per_minute,
                "usv": self.microsieverts_per_hour,
                "mode": self.mode,
            },
        )


class ReadingResponse(BaseModel):
    id: int
    timestamp: datetime
    counts_per_second: int
    counts_per_minute: int
    microsieverts_per_hour: float
    mode: str

    def model_post_init(self, __context: Any) -> None:
        logger.debug(
            "reading_response_serialized",
            extra={
                "id": self.id,
                "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            },
        )
