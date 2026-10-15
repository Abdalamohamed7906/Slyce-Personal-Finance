"""Personalised money tips for a paycheck split."""
from decimal import Decimal

from app.services.llm import ask_llm

FALLBACK_TIPS = [
    "Move your savings on payday, before you spend: 'pay yourself first'.",
    "Aim for an emergency fund of 3 months of 'needs' before investing.",
    "Check your subscriptions: cancelled ones go straight to savings.",
]


def generate_tip(split: dict[str, Decimal]) -> str:
    prompt = (
        "You are a friendly money coach for young people in the UK. "
        f"Their paycheck of £{split['amount']} was split into needs £{split['needs']}, "
        f"wants £{split['wants']}, savings £{split['savings']}. "
        "Give ONE practical tip in under 40 words. No investment recommendations."
    )
    tip = ask_llm(prompt, max_tokens=120)
    if tip:
        return tip
    # Pick a fallback deterministically so tests are stable
    return FALLBACK_TIPS[int(split["amount"]) % len(FALLBACK_TIPS)]
