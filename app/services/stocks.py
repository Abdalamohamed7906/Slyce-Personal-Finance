"""Stock explorer: Trading 212 instrument list + price growth + AI summary.

- Trading 212 API gives the list of tradable instruments (needs YOUR key,
  generated in the T212 app; use the demo/practice account).
- Price history comes from yfinance (T212's public API doesn't provide it).
- The LLM only writes the plain-English "what is this" text.
"""
import time

import httpx

from app.config import get_settings
from app.services.llm import ask_llm

_cache: dict = {"at": 0.0, "items": []}
CACHE_SECONDS = 6 * 60 * 60  # instrument list rarely changes; T212 rate-limits this

# Used when no Trading 212 key is configured, so you can build the UI now.
SAMPLE_INSTRUMENTS = [
    {"ticker": "AAPL_US_EQ", "name": "Apple", "type": "STOCK", "currency": "USD"},
    {"ticker": "MSFT_US_EQ", "name": "Microsoft", "type": "STOCK", "currency": "USD"},
    {"ticker": "VUSAl_EQ", "name": "Vanguard S&P 500 ETF", "type": "ETF", "currency": "GBP"},
    {"ticker": "VWRPl_EQ", "name": "Vanguard FTSE All-World ETF", "type": "ETF", "currency": "GBP"},
]


def list_instruments(query: str | None = None, limit: int = 50) -> list[dict]:
    settings = get_settings()
    if settings.trading212_api_key:
        if time.time() - _cache["at"] > CACHE_SECONDS:
            resp = httpx.get(
                f"{settings.trading212_base_url}/equity/metadata/instruments",
                auth=(settings.trading212_api_key, settings.trading212_api_secret),
                timeout=20,
            )
            resp.raise_for_status()
            _cache["items"] = [
                {
                    "ticker": i.get("ticker"),
                    "name": i.get("name"),
                    "type": i.get("type"),
                    "currency": i.get("currencyCode"),
                }
                for i in resp.json()
            ]
            _cache["at"] = time.time()
        items = _cache["items"]
    else:
        items = SAMPLE_INSTRUMENTS

    if query:
        q = query.lower()
        items = [
            i for i in items
            if q in (i["ticker"] or "").lower() or q in (i["name"] or "").lower()
        ]
    return items[:limit]


def t212_to_yahoo(ticker: str) -> str:
    """Rough mapping from Trading 212 tickers to Yahoo symbols.
    'AAPL_US_EQ' -> 'AAPL', 'VUSAl_EQ' (London) -> 'VUSA.L'.
    Extend this as you find tickers that don't map."""
    base = ticker.split("_")[0]
    if base.endswith("l") and "_US_" not in ticker:
        return base[:-1] + ".L"
    return base


def price_growth(ticker: str, period: str = "1y") -> tuple[float | None, float | None]:
    """Return (start_price, end_price) over `period` (1mo, 6mo, 1y, 5y...)."""
    try:
        import yfinance as yf

        hist = yf.Ticker(t212_to_yahoo(ticker)).history(period=period)
        if hist.empty:
            return None, None
        return float(hist["Close"].iloc[0]), float(hist["Close"].iloc[-1])
    except Exception:
        return None, None


def describe(ticker: str, name: str | None) -> str:
    text = ask_llm(
        f"In 2 short sentences, explain to a beginner what {name or ticker} "
        f"({ticker}) is and what it does. Neutral tone. Do not recommend buying "
        "or selling.",
        max_tokens=120,
    )
    return text or f"{name or ticker}: add an LLM API key to get a plain-English summary."
