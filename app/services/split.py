"""The split engine. Pure maths, no database, so it's easy to test."""
from decimal import ROUND_HALF_UP, Decimal

PENNY = Decimal("0.01")


def split_paycheck(
    amount: Decimal, needs_pct: int = 50, wants_pct: int = 30, savings_pct: int = 20
) -> dict[str, Decimal]:
    """Split `amount` into needs / wants / savings.

    Uses Decimal (never float) for money. Any leftover penny from rounding
    goes to savings, so the three parts always add up to exactly `amount`.
    """
    if needs_pct + wants_pct + savings_pct != 100:
        raise ValueError("Percentages must add up to 100")
    amount = Decimal(amount).quantize(PENNY)
    if amount <= 0:
        raise ValueError("Amount must be positive")

    needs = (amount * needs_pct / 100).quantize(PENNY, ROUND_HALF_UP)
    wants = (amount * wants_pct / 100).quantize(PENNY, ROUND_HALF_UP)
    savings = amount - needs - wants
    return {"amount": amount, "needs": needs, "wants": wants, "savings": savings}
