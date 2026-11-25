from time import perf_counter

from app.errors import DomainError
from app.manifest import manifest
from app.pipeline import process
from app.store import fetch, save


def create(source, label):
    started = perf_counter()
    digest = manifest(source)
    run_id = digest["digest"]
    try:
        _, record = fetch(run_id)
    except DomainError as exc:
        if exc.code != "RUN_NOT_FOUND":
            raise
    else:
        return {**record, "reused": True}
    result = process(source)
    return save(source, {"id": run_id, "manifest": digest, "sample": label,
                         "elapsed_ms": round((perf_counter() - started) * 1000, 2), "result": result})


def rerun(run_id):
    source, original = fetch(run_id)
    if manifest(source) != original["manifest"]:
        raise DomainError("RUN_VERSION_CHANGED", "原批次与当前规则版本不一致", 409)
    result = process(source)
    if result != original["result"]:
        raise DomainError("RUN_DRIFT", "复算结果与原始快照不一致", 409)
    return {**original, "reused": True}
