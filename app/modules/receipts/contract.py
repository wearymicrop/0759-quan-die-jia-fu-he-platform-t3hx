from datetime import datetime, timezone
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

Key = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=40)]
Quantity = Annotated[int, Field(strict=True, ge=1, le=10_000)]


def utc_text(value):
    instant = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if instant.utcoffset() is None:
        raise ValueError("时间须带偏移")
    try:
        return instant.astimezone(timezone.utc).isoformat(timespec="microseconds")
    except OverflowError as exc:
        raise ValueError("时间超出可表示范围") from exc


class Item(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: Key
    category: Key
    qty: Quantity
    price: str


class Sale(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["sale"]
    id: Key
    at: str
    shop: Key
    coupons: Annotated[list[Key], Field(max_length=12)]
    lines: Annotated[list[Item], Field(min_length=1, max_length=50)]
    paid: str

    @field_validator("at")
    @classmethod
    def timestamp(cls, value):
        return utc_text(value)


class Return(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: Literal["return"]
    id: Key
    at: str
    order: Key
    line: Key
    qty: Quantity
    cash: str

    _timestamp = field_validator("at")(utc_text)
