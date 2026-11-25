import re
import unicodedata
from decimal import Decimal


def cents(raw):
    value = unicodedata.normalize("NFKC", raw).strip().removeprefix("¥").strip()
    if not re.fullmatch(r"(?:[0-9]{1,8}|[0-9]{1,2}(?:,[0-9]{3}){1,2})(?:\.[0-9]{1,2})?", value):
        raise ValueError("金额须为最多两位小数的人民币")
    return int(Decimal(value.replace(",", "")) * 100)


def normalize(item):
    if item["type"] == "sale":
        item["paid"] = cents(item["paid"])
        seen = set()
        for line in item["lines"]:
            if line["id"] in seen:
                raise ValueError("小票明细键重复")
            seen.add(line["id"])
            line["price"] = cents(line["price"])
        item["lines"].sort(key=lambda line: line["id"])
        item["coupons"] = sorted(set(item["coupons"]))
    else:
        item["cash"] = cents(item["cash"])
    return item
