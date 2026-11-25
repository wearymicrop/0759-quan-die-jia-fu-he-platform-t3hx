from collections import defaultdict
from itertools import combinations


def classify(book):
    versions = defaultdict(list)
    for rule in book["versions"]:
        versions[rule["code"]].append(rule)
    conflicts = []
    for code, entries in sorted(versions.items()):
        for left, right in combinations(entries, 2):
            start = max(left["start"], right["start"])
            end = min(left["end"], right["end"])
            if start < end:
                conflicts.append({"code": code, "reason": "VERSION_OVERLAP", "start": start, "end": end,
                                  "versions": [left["version"], right["version"]],
                                  "source_indices": [left["source_index"], right["source_index"]]})
    return {**book, "index": dict(versions), "conflicts": conflicts}


def active_version(book, code, instant):
    rules = book["index"].get(code, [])
    active = [row for row in rules if row["start"] <= instant < row["end"]]
    if len(active) > 1:
        return None, "VERSION_OVERLAP", active
    if not active:
        return None, "RULE_INACTIVE" if rules else "RULE_UNKNOWN", rules
    return active[0], None, active
