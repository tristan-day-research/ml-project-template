from __future__ import annotations

from pydantic import BaseModel, Field


class Item(BaseModel):
    id: int = Field(ge=0)
    value: float


def validate_item(payload: dict) -> Item:
    """Validate a single item dict using pydantic."""
    return Item(**payload)

