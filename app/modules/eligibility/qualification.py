from app.modules.versions.effective import active_version


def evaluated(sale, book):
    qualified = []
    findings = []
    for code in sale["coupons"]:
        rule, reason, matched = active_version(book, code, sale["at"])
        evidence = {"coupon": code, "versions": [row["version"] for row in matched],
                    "rule_indices": [row["source_index"] for row in matched]}
        if reason:
            findings.append({**evidence, "reason": reason})
            continue
        eligible = [line for line in sale["lines"] if not rule["categories"] or line["category"] in rule["categories"]]
        gross = sum(line["qty"] * line["price"] for line in eligible)
        if rule["shops"] and sale["shop"] not in rule["shops"]:
            reason = "SHOP_MISMATCH"
        elif not eligible:
            reason = "CATEGORY_MISMATCH"
        elif gross < rule["minimum"]:
            reason = "MINIMUM_NOT_MET"
        else:
            reason = "QUALIFIED"
            qualified.append({**rule, "eligible": [line["id"] for line in eligible]})
        findings.append({**evidence, "reason": reason, "eligible_gross": gross})
    return {"id": sale["id"], "qualified": qualified, "findings": findings,
            "blocked": any(item["reason"] == "VERSION_OVERLAP" for item in findings)}
