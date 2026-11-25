from collections import defaultdict


def trace(sales, qualified, returns, reconcile):
    refunds = defaultdict(list)
    differences = defaultdict(list)
    for row in returns:
        refunds[row["order"]].append(row)
    for gap in reconcile["differences"]:
        kind = "return" if gap["reason"] == "RETURN_CASH_GAP" else "sale"
        differences[kind, gap["id"]].append(gap)
    packets = []
    for sale in sales:
        evidence = refunds.pop(sale["id"], [])
        related = [*differences["sale", sale["id"]], *(item for row in evidence for item in differences["return", row["id"]])]
        packets.append({"order": sale["id"], "receipt_line": sale["source_line"], "status": sale["status"],
                        "coupon_checks": qualified[sale["id"]]["findings"], "applied": sale.get("applied", []),
                        "returns": evidence, "differences": related})
    return {"packets": packets, "orphan_returns": [row for entries in refunds.values() for row in entries]}
