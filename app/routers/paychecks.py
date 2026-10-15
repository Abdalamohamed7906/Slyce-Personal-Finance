from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Paycheck, User
from app.schemas import PaycheckCreate, PaycheckOut, SplitRequest, SplitResult
from app.services.split import split_paycheck
from app.services.tips import generate_tip

router = APIRouter(tags=["paychecks"])


@router.post("/split", response_model=SplitResult)
def preview_split(body: SplitRequest):
    """Try the calculator without an account (nothing is saved)."""
    return split_paycheck(body.amount, body.needs_pct, body.wants_pct, body.savings_pct)


@router.post("/paychecks", response_model=PaycheckOut, status_code=201)
def add_paycheck(
    body: PaycheckCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    s = split_paycheck(body.amount, body.needs_pct, body.wants_pct, body.savings_pct)
    pc = Paycheck(
        user_id=user.id,
        paid_on=body.paid_on,
        needs_pct=body.needs_pct,
        wants_pct=body.wants_pct,
        savings_pct=body.savings_pct,
        tip=generate_tip(s) if body.with_tip else None,
        **s,
    )
    db.add(pc)
    db.commit()
    db.refresh(pc)
    return pc


@router.get("/paychecks", response_model=list[PaycheckOut])
def list_paychecks(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.scalars(
        select(Paycheck).where(Paycheck.user_id == user.id).order_by(Paycheck.paid_on.desc())
    ).all()


@router.delete("/paychecks/{paycheck_id}", status_code=204)
def delete_paycheck(
    paycheck_id: int, user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    pc = db.get(Paycheck, paycheck_id)
    if not pc or pc.user_id != user.id:  # never let users touch others' data
        raise HTTPException(404, "Paycheck not found")
    db.delete(pc)
    db.commit()
