from datetime import date
from decimal import Decimal

import pytest

from app.services.savings import savings_target
from app.services.split import split_paycheck


def test_basic_split():
    s = split_paycheck(Decimal("1000"))
    assert (s["needs"], s["wants"], s["savings"]) == (Decimal("500.00"), Decimal("300.00"), Decimal("200.00"))


def test_parts_always_add_up():
    s = split_paycheck(Decimal("1234.57"))
    assert s["needs"] + s["wants"] + s["savings"] == Decimal("1234.57")


def test_custom_rule():
    s = split_paycheck(Decimal("1000"), 60, 20, 20)
    assert s["needs"] == Decimal("600.00")


def test_bad_rule():
    with pytest.raises(ValueError):
        split_paycheck(Decimal("1000"), 50, 50, 50)


def test_savings_target_no_interest():
    plain, grown = savings_target(
        [(date(2026, 1, 1), Decimal("200")), (date(2026, 2, 1), Decimal("200"))],
        today=date(2026, 3, 1),
    )
    assert plain == grown == Decimal("400.00")


def test_savings_target_with_interest():
    plain, grown = savings_target([(date(2025, 1, 1), Decimal("100"))], 0.05, today=date(2026, 1, 1))
    assert plain == Decimal("100.00")
    assert grown == Decimal("105.00")
