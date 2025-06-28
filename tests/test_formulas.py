from decimal import Decimal
from src.core.formulas import valuation, avg_price

def test_valuation_ok():
    params = {"EBITDA": 100, "Multiple": 3, "Factor Score": 50}
    assert valuation(params) == Decimal("150.0")

def test_valuation_missing():
    assert valuation({"EBITDA": 10}) is None

def test_avg_price_ok():
    p1 = {"Price": 10}
    p2 = {"Price": 14}
    assert avg_price(p1, p2) == Decimal("12")

def test_avg_price_bad():
    assert avg_price({}, {}) is None
