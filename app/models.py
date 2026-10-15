"""Database tables."""
from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    paychecks: Mapped[list["Paycheck"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Paycheck(Base):
    """One paycheck and how it was split. Ratios are stored so history stays
    correct even if the user changes their rule later."""

    __tablename__ = "paychecks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    amount: Mapped[float] = mapped_column(Numeric(12, 2))
    paid_on: Mapped[date] = mapped_column(Date)

    needs_pct: Mapped[int] = mapped_column(Integer, default=50)
    wants_pct: Mapped[int] = mapped_column(Integer, default=30)
    savings_pct: Mapped[int] = mapped_column(Integer, default=20)

    needs: Mapped[float] = mapped_column(Numeric(12, 2))
    wants: Mapped[float] = mapped_column(Numeric(12, 2))
    savings: Mapped[float] = mapped_column(Numeric(12, 2))

    tip: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    user: Mapped[User] = relationship(back_populates="paychecks")
