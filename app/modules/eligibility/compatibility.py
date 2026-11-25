from itertools import combinations


def matrix(eligible, pairs):
    allowed = {tuple(pair) for pair in pairs}
    edges = []
    for a, b in combinations(sorted(eligible, key=lambda rule: rule["code"]), 2):
        pair = (a["code"], b["code"])
        reason = "COMPATIBLE"
        if a["group"] == b["group"]:
            reason = "EXCLUSIVE_GROUP"
        elif pair not in allowed:
            reason = "PAIR_UNDECLARED"
        edges.append({"a": pair[0], "b": pair[1], "reason": reason})
    return edges
