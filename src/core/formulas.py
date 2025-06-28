from decimal import Decimal, InvalidOperation
from typing import Optional, Dict

__all__ = ["valuation", "avg_price"]

PERCENT = Decimal("100")

def _safe(val) -> Optional[Decimal]:
    try:
        return Decimal(val)
    except (TypeError, InvalidOperation):
        return None


def valuation(params: Dict[str, object]) -> Optional[Decimal]:

    ebitda   = _safe(params.get("EBITDA"))
    multiple = _safe(params.get("Multiple"))
    factor   = _safe(params.get("Factor Score"))

    if None in (ebitda, multiple, factor):
        return None

    return ebitda * multiple * (factor / PERCENT)


def avg_price(params_t1: Dict[str, object], params_t2: Dict[str, object]) -> Optional[Decimal]:

    p1 = _safe(params_t1.get("Price"))
    p2 = _safe(params_t2.get("Price"))

    if None in (p1, p2):
        return None

    return (p1 + p2) / 2
