"""Savings tracker: how much you *should* have saved if you followed your rule.

Deliberately plain maths (no AI) so the numbers are always correct.
"""
from datetime import date
from decimal import Decimal

from app.services.split import PENNY


def savings_target(
    paychecks: list[tuple[date, Decimal]],
    annual_rate: float = 0.0,
    today: date | None = None,
) -> tuple[Decimal, Decimal]:
    """Return (plain_total, total_with_interest).

    `paychecks` is a list of (paid_on, savings_amount).
    Each savings amount is grown from its pay date to `today` at
    `annual_rate` (e.g. 0.04 for 4%), compounded daily-ish.
    """
    today = today or date.today()
    plain = Decimal("0")
    grown = Decimal("0")
    for paid_on, saved in paychecks:
        saved = Decimal(saved)
        plain += saved
        years = max((today - paid_on).days, 0) / 365
        grown += saved * Decimal(str((1 + annual_rate) ** years))
    return plain.quantize(PENNY), grown.quantize(PENNY)


def commentary(target: Decimal, actual: Decimal | None) -> str:
    """Simple rule-based message. You could swap this for an LLM later,
    passing it the numbers, but never let the LLM do the maths."""
    if actual is None:
        return f"If you'd followed your rule, you'd have about £{target} saved."
    diff = actual - target
    if diff >= 0:
        return f"Nice! You're £{diff} ahead of your savings target."
    return (
        f"You're £{-diff} behind target. Moving a little from 'wants' to "
        f"'savings' each paycheck would help close the gap."
    )
