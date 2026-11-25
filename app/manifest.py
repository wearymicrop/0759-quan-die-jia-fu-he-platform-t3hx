import hashlib
import json

from app.config import RULE_VERSION, SOURCES


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def manifest(source):
    hashes = {name: sha(canonical(source[name])) for name in SOURCES}
    return {"rule_version": RULE_VERSION, "files": hashes,
            "digest": sha(canonical([RULE_VERSION, hashes]))}
