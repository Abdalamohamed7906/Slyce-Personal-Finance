from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Paycheck, User
from app.schemas import SavingsReport
from app.services.savings import commentary, savings_target

router = APIRouter(prefix="/savings", tags=["savings"])


@router.get("/target", response_model=SavingsReport)
def target(
    since: date | None = Query(None, description="Only count paychecks from this date"),
    annual_rate: float = Query(0.0, ge=0, le=0.2, description="e.g. 0.04 for a 4% savings account"),
    actual: Decimal | None = Query(None, ge=0, description="What you've really saved"),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    stmt = select(Paycheck).where(Paycheck.user_id == user.id)
    if since:
        stmt = stmt.where(Paycheck.paid_on >= since)
    rows = db.scalars(stmt).all()

    plain, grown = savings_target([(p.paid_on, p.savings) for p in rows], annual_rate)
    return SavingsReport(
        since=since,
        paychecks_counted=len(rows),
        target_savings=plain,
        target_with_interest=grown,
        annual_rate=annual_rate,
        actual_savings=actual,
        difference=(actual - grown) if actual is not None else None,
        commentary=commentary(grown, actual),
    )
