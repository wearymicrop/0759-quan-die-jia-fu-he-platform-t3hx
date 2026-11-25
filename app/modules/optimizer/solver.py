from app.modules.optimizer.allocation import simulate


def combos(rules, allowed, start=0, selected=()):
    yield selected
    for i in range(start, len(rules)):
        rule = rules[i]
        if all(tuple(sorted((rule["code"], other["code"]))) in allowed for other in selected):
            yield from combos(rules, allowed, i + 1, (*selected, rule))


def solve(sale, qualification):
    if qualification["blocked"]:
        return {"id": sale["id"], "status": "isolated", "reason": "VERSION_OVERLAP", "source_line": sale["source_line"]}
    gross = {line["id"]: line["qty"] * line["price"] for line in sale["lines"]}
    rules = sorted(qualification["qualified"], key=lambda rule: (rule["rank"], rule["code"]))
    allowed = {(edge["a"], edge["b"]) for edge in qualification["matrix"] if edge["reason"] == "COMPATIBLE"}
    best = None
    trials = []
    for combo in combos(rules, allowed):
        net, applied = simulate(gross, combo)
        codes = tuple(rule["code"] for rule in combo)
        due = sum(net.values())
        score = (due, len(codes), tuple(sorted(codes)))
        trials.append({"codes": list(codes), "due": due})
        if best is None or score < best[0]:
            best = (score, net, applied)
    score, net, applied = best
    lines = [{**line, "gross": gross[line["id"]], "actual": net[line["id"]],
              "discount": gross[line["id"]] - net[line["id"]]} for line in sale["lines"]]
    ranked = sorted(trials, key=lambda row: (row["due"], len(row["codes"]), sorted(row["codes"])))
    return {"id": sale["id"], "status": "solved", "source_line": sale["source_line"], "at": sale["at"],
            "shop": sale["shop"], "chosen": [item["code"] for item in applied], "trials": ranked[:12], "trial_count": len(trials),
            "gross": sum(gross.values()), "discount": sum(gross.values()) - score[0], "due": score[0],
            "paid": sale["paid"], "lines": lines, "applied": applied}
