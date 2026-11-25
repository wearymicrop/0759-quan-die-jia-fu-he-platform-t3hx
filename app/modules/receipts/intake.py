from collections import Counter, defaultdict

from pydantic import ValidationError

from app.errors import DomainError
from app.manifest import canonical
from app.modules.receipts.contract import Return, Sale
from app.modules.receipts.money import normalize
from app.sources import json_rows


def read(text):
    rows = []
    groups = defaultdict(list)
    events = {"sale": [], "return": []}
    for line, raw, value, code in json_rows(text):
        if line > 400:
            raise DomainError("RECEIPT_LIMIT", "一个批次最多四百行流水")
        evidence = {"line": line, "raw": raw, "code": code}
        rows.append(evidence)
        if code:
            continue
        try:
            model = {"sale": Sale, "return": Return}.get(str(value.get("type")))
            if model is None:
                raise ValueError("未知流水类型")
            event = normalize(model.model_validate(value).model_dump())
        except (ValidationError, ValueError) as exc:
            evidence.update(code="BAD_EVENT", detail=str(exc).splitlines()[0])
            continue
        evidence.update(id=event["id"], type=event["type"])
        groups[event["type"], event["id"]].append((evidence, event))
    for entries in groups.values():
        if len({canonical(item) for _, item in entries}) > 1:
            for evidence, _ in entries:
                evidence["code"] = "DUPLICATE_CONFLICT"
            continue
        first, event = entries[0]
        first["code"] = "ACCEPTED"
        events[event["type"]].append({**event, "source_line": first["line"]})
        for evidence, _ in entries[1:]:
            evidence["code"] = "DUPLICATE_REPLAY"
    by_code = Counter(row["code"] for row in rows)
    counts = {"input": len(rows), "accepted": by_code["ACCEPTED"], "duplicates": by_code["DUPLICATE_REPLAY"],
              "empty": by_code["EMPTY_ROW"], "isolated": sum(by_code[k] for k in ("BAD_JSON", "BAD_EVENT", "DUPLICATE_CONFLICT"))}
    return {"rows": rows, "sales": events["sale"], "returns": events["return"], "counts": counts}
