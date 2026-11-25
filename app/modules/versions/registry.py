from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.errors import DomainError
from app.modules.receipts.contract import Key, utc_text
from app.modules.receipts.money import cents


class Rule(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code: Key
    version: Key
    start: str
    end: str
    group: Key
    kind: Literal["fixed", "percent"]
    value: str | Annotated[int, Field(strict=True)]
    minimum: str = "0"
    rank: Annotated[int, Field(strict=True, ge=0, le=99)] = 10
    shops: Annotated[list[Key], Field(max_length=30)] = []
    categories: Annotated[list[Key], Field(max_length=30)] = []


class Rulebook(BaseModel):
    model_config = ConfigDict(extra="forbid")
    versions: Annotated[list[Rule], Field(max_length=150)]
    pairs: Annotated[list[tuple[Key, Key]], Field(max_length=500)] = []


def load(raw):
    try:
        book = Rulebook.model_validate(raw).model_dump()
        codes = {row["code"] for row in book["versions"]}
        pairs = set()
        for a, b in book["pairs"]:
            if a == b or a not in codes or b not in codes:
                raise ValueError("兼容边引用不存在或指向自身")
            pairs.add(tuple(sorted((a, b))))
        identities = set()
        for index, rule in enumerate(book["versions"], 1):
            rule.update(start=utc_text(rule["start"]), end=utc_text(rule["end"]), source_index=index,
                        minimum=cents(rule["minimum"]))
            key = (rule["code"], rule["version"])
            if key in identities or rule["start"] >= rule["end"]:
                raise ValueError("版本重名或时段无效")
            identities.add(key)
            value = rule["value"]
            if rule["kind"] == "fixed" and isinstance(value, str):
                rule["value"] = cents(value)
            elif rule["kind"] != "percent" or type(value) is not int or not 0 < value <= 10_000:
                raise ValueError("券面额或折扣率无效")
        return {"versions": book["versions"], "pairs": [list(pair) for pair in sorted(pairs)]}
    except (ValidationError, ValueError, OverflowError) as exc:
        raise DomainError("BAD_RULEBOOK", "券规则的字段、版本或兼容边无效") from exc
