def allocate(amount, balances):
    total = sum(balances.values())
    if not total:
        return dict.fromkeys(balances, 0)
    quotients = {key: divmod(amount * value, total) for key, value in balances.items()}
    shares = {key: part[0] for key, part in quotients.items()}
    rest = amount - sum(shares.values())
    for key in sorted(shares, key=lambda key: (-quotients[key][1], key))[:rest]:
        shares[key] += 1
    return shares


def simulate(gross, rules):
    net = gross.copy()
    applied = []
    for rule in rules:
        eligible = {key: net[key] for key in rule["eligible"]}
        subtotal = sum(eligible.values())
        amount = (subtotal * rule["value"] + 5000) // 10_000 if rule["kind"] == "percent" else rule["value"]
        amount = min(subtotal, amount)
        shares = allocate(amount, eligible)
        for key, share in shares.items():
            net[key] -= share
        applied.append({"code": rule["code"], "version": rule["version"], "rule_index": rule["source_index"],
                        "base": subtotal, "amount": amount, "shares": shares})
    return net, applied
