from collections import defaultdict


def balance(intake, sales, returns):
    solved = [row for row in sales if row["status"] == "solved"]
    posted = [row for row in returns if row["status"] == "posted"]
    cuts = defaultdict(list)
    for row in posted:
        cuts[row["order"], row["line"]].append(row)
    line_books = []
    gaps = []
    for sale in solved:
        if sale["paid"] != sale["due"]:
            gaps.append({"id": sale["id"], "reason": "SALE_CASH_GAP", "gap": sale["paid"] - sale["due"],
                         "source_line": sale["source_line"]})
        for line in sale["lines"]:
            refunds = cuts[sale["id"], line["id"]]
            refunded = sum(row["expected"] for row in refunds)
            discount = sum(row["discount"] for row in refunds)
            refunded_gross = sum(row["gross"] for row in refunds)
            qty = sum(row["qty"] for row in refunds)
            left_gross = (line["qty"] - qty) * line["price"]
            left_discount = line["discount"] - discount
            left_net = left_gross - left_discount
            gap = line["actual"] - refunded - left_net
            line_books.append({"order": sale["id"], "line": line["id"], "gross": line["gross"],
                               "actual": line["actual"], "refunded": refunded, "retained": left_net, "gap": gap,
                               "refunded_qty": qty, "retained_qty": line["qty"] - qty,
                               "retained_gross": left_gross, "retained_discount": left_discount})
            if gap or left_net < 0 or left_discount < 0 or line["gross"] != refunded_gross + left_gross:
                gaps.append({"id": sale["id"], "line": line["id"], "reason": "LINE_IMBALANCE", "gap": gap})
    gaps.extend({"id": row["id"], "reason": "RETURN_CASH_GAP", "gap": row["cash_gap"], "source_line": row["source_line"]}
                for row in posted if row["cash_gap"])
    totals = {"gross": sum(row["gross"] for row in solved), "discount": sum(row["discount"] for row in solved),
              "due": sum(row["due"] for row in solved), "paid": sum(row["paid"] for row in solved),
              "refunded": sum(row["expected"] for row in posted), "cash_refunded": sum(row["cash"] for row in posted),
              "retained": sum(row["retained"] for row in line_books)}
    rows = intake["counts"]
    row_gap = rows["input"] - len(sales) - len(returns) - rows["duplicates"] - rows["empty"] - rows["isolated"]
    formula_gap = totals["gross"] - totals["discount"] - totals["due"]
    retention_gap = totals["due"] - totals["refunded"] - totals["retained"]
    status = "DIFFERENCE" if row_gap or formula_gap or retention_gap or gaps else "MATCHED"
    return {"status": status, "totals": totals, "differences": gaps, "lines": line_books,
            "row_gap": row_gap, "formula_gap": formula_gap, "retention_gap": retention_gap,
            "sales_isolated": len(sales) - len(solved), "returns_isolated": len(returns) - len(posted)}
