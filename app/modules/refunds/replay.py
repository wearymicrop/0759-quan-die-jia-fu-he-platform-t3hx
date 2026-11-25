from collections import defaultdict
from datetime import datetime, timedelta, timezone

from app.modules.refunds.units import original_share

LOCAL = timezone(timedelta(hours=8))


def day(instant):
    return str(datetime.fromisoformat(instant).astimezone(LOCAL).date())


def replay(solutions, events):
    orders = {row["id"]: row for row in solutions}
    index = {(row["id"], line["id"]): line for row in solutions for line in row.get("lines", [])}
    counts = defaultdict(int)
    results = []
    for event in sorted(events, key=lambda row: (row["at"], row["id"])):
        key = (event["order"], event["line"])
        sale = orders.get(key[0])
        line = index.get(key)
        reason = None
        if sale is None:
            reason = "SALE_MISSING"
        elif sale["status"] != "solved":
            reason = "SALE_ISOLATED"
        elif line is None:
            reason = "SALE_LINE_MISSING"
        elif event["at"] < sale["at"]:
            reason = "RETURN_BEFORE_SALE"
        elif counts[key] + event["qty"] > line["qty"]:
            reason = "RETURN_OVER_QTY"
        if reason:
            results.append({**event, "status": "isolated", "reason": reason})
            continue
        shares = original_share(line, counts[key], event["qty"])
        counts[key] += event["qty"]
        results.append({**event, **shares, "status": "posted", "original_line": sale["source_line"],
                        "sale_day": day(sale["at"]), "return_day": day(event["at"]),
                        "returned_qty": counts[key], "cash_gap": event["cash"] - shares["expected"]})
    return results
