from fastapi import APIRouter, Depends, HTTPException, Query

from app.auth import get_current_user
from app.schemas import Instrument, StockSummary
from app.services import stocks

router = APIRouter(prefix="/stocks", tags=["stocks"], dependencies=[Depends(get_current_user)])

PERIODS = {"1mo", "3mo", "6mo", "1y", "2y", "5y"}


@router.get("/instruments", response_model=list[Instrument])
def instruments(q: str | None = None, limit: int = Query(50, le=200)):
    try:
        return stocks.list_instruments(q, limit)
    except Exception as exc:
        raise HTTPException(502, f"Couldn't reach Trading 212: {exc}")


@router.get("/{ticker}/summary", response_model=StockSummary)
def summary(ticker: str, period: str = "1y"):
    if period not in PERIODS:
        raise HTTPException(400, f"period must be one of {sorted(PERIODS)}")
    match = next((i for i in stocks.list_instruments(ticker, 200) if i["ticker"] == ticker), None)
    name = match["name"] if match else None
    start, end = stocks.price_growth(ticker, period)
    growth = round((end - start) / start * 100, 2) if start and end else None
    return StockSummary(
        ticker=ticker,
        name=name,
        period=period,
        start_price=start,
        end_price=end,
        growth_pct=growth,
        summary=stocks.describe(ticker, name),
    )
