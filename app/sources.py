from io import StringIO
import json

from app.config import ROOT, SOURCES
from app.errors import DomainError


def load_sample(sample):
    if sample not in {"clean", "dirty"}:
        raise DomainError("SAMPLE_NOT_FOUND", "找不到指定样例", 404)
    folder = ROOT / "sample_data" / sample
    return {SOURCES[0]: (folder / (SOURCES[0] + ".jsonl")).read_bytes().decode("utf-8"),
            SOURCES[1]: json.loads((folder / (SOURCES[1] + ".json")).read_text())}


def choose_source(payload):
    if set(payload) == {"sample"} and isinstance(payload["sample"], str):
        return load_sample(payload["sample"]), payload["sample"]
    if set(payload) == set(SOURCES):
        if isinstance(payload[SOURCES[0]], str) and isinstance(payload[SOURCES[1]], dict):
            if len(payload[SOURCES[0]].encode("utf-8")) > 400_000:
                raise DomainError("INPUT_LIMIT", "流水文本超过四十万字节")
            return payload, "自备数据"
    raise DomainError("CHOOSE_SOURCE", "请选择样例或提供完整输入")


def json_rows(text):
    def reject_constant(value):
        raise ValueError(value)

    for line, physical in enumerate(StringIO(text.removeprefix("\ufeff")), 1):
        raw = physical.rstrip("\r\n")
        if not raw.strip():
            yield line, raw, None, "EMPTY_ROW"
            continue
        try:
            value = json.loads(raw, parse_constant=reject_constant)
            raw.encode("utf-8")
            json.dumps(value, ensure_ascii=False).encode("utf-8")
            if not isinstance(value, dict):
                raise ValueError(raw)
        except (ValueError, RecursionError):
            yield line, raw, None, "BAD_JSON"
        else:
            yield line, raw, value, None
