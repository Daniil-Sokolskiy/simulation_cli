import pytest
from src.core.validators import validate

@pytest.mark.parametrize(
    "name, raw, ok",
    [
        ("EBITDA", "1000", True),
        ("Interest Rate", "50", True),
        ("Interest Rate", "0", False),
        ("Interest Rate", "101", False),
        ("Multiple", "2.5", True),
        ("Multiple", "abc", False),
        ("Factor Score", "7", True),
        ("Factor Score", "7.2", False),
    ],
)
def test_validate(name, raw, ok):
    val, err = validate(name, raw)
    assert (err is None) == ok
