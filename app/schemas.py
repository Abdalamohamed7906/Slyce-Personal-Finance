"""Request/response shapes (what the API accepts and returns)."""
from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


# ---------- Auth ----------
class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    email: EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Split ----------
class SplitRule(BaseModel):
    needs_pct: int = Field(50, ge=0, le=100)
    wants_pct: int = Field(30, ge=0, le=100)
    savings_pct: int = Field(20, ge=0, le=100)

    @model_validator(mode="after")
    def must_total_100(self):
        if self.needs_pct + self.wants_pct + self.savings_pct != 100:
            raise ValueError("needs_pct + wants_pct + savings_pct must equal 100")
        return self


class SplitRequest(SplitRule):
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class SplitResult(BaseModel):
    amount: Decimal
    needs: Decimal
    wants: Decimal
    savings: Decimal


class PaycheckCreate(SplitRequest):
    paid_on: date = Field(default_factory=date.today)
    with_tip: bool = True


class PaycheckOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    amount: Decimal
    paid_on: date
    needs_pct: int
    wants_pct: int
    savings_pct: int
    needs: Decimal
    wants: Decimal
    savings: Decimal
    tip: str | None


# ---------- Savings tracker ----------
class SavingsReport(BaseModel):
    since: date | None
    paychecks_counted: int
    target_savings: Decimal          # sum of savings portions
    target_with_interest: Decimal    # same, grown at annual_rate
    annual_rate: float
    actual_savings: Decimal | None
    difference: Decimal | None       # actual - target_with_interest (negative = behind)
    commentary: str


# ---------- Stocks ----------
class Instrument(BaseModel):
    ticker: str
    name: str | None = None
    type: str | None = None
    currency: str | None = None


class StockSummary(BaseModel):
    ticker: str
    name: str | None
    period: str
    start_price: float | None
    end_price: float | None
    growth_pct: float | None
    summary: str
    disclaimer: str = (
        "For education only, not financial advice. "
        "Past performance does not predict future returns."
    )
