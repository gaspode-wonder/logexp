# filename: logexp/app/schemas.py

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ReadingCreate(BaseModel):
    counts_per_second: int = Field(..., gt=0)
    counts_per_minute: int = Field(..., gt=0)
    microsieverts_per_hour: float = Field(..., gt=0)
    mode: str = Field(..., min_length=1)


class ReadingResponse(BaseModel):
    id: int
    timestamp: datetime
    counts_per_second: int
    counts_per_minute: int
    microsieverts_per_hour: float
    mode: str
