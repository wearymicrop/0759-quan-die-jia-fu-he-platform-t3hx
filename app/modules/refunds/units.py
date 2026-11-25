def prefix(total, quantity, units):
    each, extra = divmod(total, quantity)
    return each * units + min(units, extra)


def original_share(line, already, qty):
    discount = prefix(line["discount"], line["qty"], already + qty) - prefix(line["discount"], line["qty"], already)
    gross = line["price"] * qty
    return {"gross": gross, "discount": discount, "expected": gross - discount}
