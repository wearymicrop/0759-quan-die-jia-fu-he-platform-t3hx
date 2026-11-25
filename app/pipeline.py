from app.modules.eligibility.compatibility import matrix
from app.modules.eligibility.qualification import evaluated
from app.modules.optimizer.solver import solve
from app.modules.receipts.intake import read
from app.modules.reconcile.balance import balance
from app.modules.refunds.replay import replay
from app.modules.trace.register import trace
from app.modules.versions.effective import classify
from app.modules.versions.registry import load


def process(source):
    receipts = read(source["events"])
    versions = classify(load(source["rules"]))
    eligibility = {}
    optimizer = []
    for sale in receipts["sales"]:
        row = evaluated(sale, versions)
        row["matrix"] = matrix(row["qualified"], versions["pairs"])
        eligibility[sale["id"]] = row
        optimizer.append(solve(sale, row))
    refunds = replay(optimizer, receipts["returns"])
    checks = balance(receipts, optimizer, refunds)
    return {"receipts": receipts, "versions": versions, "eligibility": eligibility, "optimizer": optimizer,
            "refunds": refunds, "reconcile": checks, "trace": trace(optimizer, eligibility, refunds, checks)}
