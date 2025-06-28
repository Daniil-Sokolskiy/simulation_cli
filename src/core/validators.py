from decimal import Decimal, InvalidOperation

_SCHEMA = {
    "EBITDA":       dict(kind=int,   min=None, max=None),
    "Interest Rate":dict(kind=int,   min=1,    max=100),
    "Multiple":     dict(kind=float, min=None, max=None),
    "Factor Score": dict(kind=int,   min=None, max=None),
}

def validate(name: str, raw: str):

    if name not in _SCHEMA:
        return None, "Unknown parameter"

    cfg = _SCHEMA[name]
    try:
        if cfg["kind"] is int:
            val = int(raw)
        elif cfg["kind"] is float:
            val = float(raw)
        else:                     
            val = Decimal(raw)
    except (ValueError, InvalidOperation):
        return None, "Wrong format"

    if cfg["min"] is not None and val < cfg["min"]:
        return None, f"Must be ≥ {cfg['min']}"
    if cfg["max"] is not None and val > cfg["max"]:
        return None, f"Must be ≤ {cfg['max']}"

    return val, None
