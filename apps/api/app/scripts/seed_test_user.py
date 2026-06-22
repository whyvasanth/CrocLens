import os
from uuid import uuid4

from sqlalchemy import select

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import Portfolio, User, UserProfile
from app.schemas.api import HoldingCreateRequest, LiabilityCreateRequest
from app.services.portfolio_service import (
    create_holding,
    create_liability,
    list_user_holdings,
    list_user_liabilities,
)


TEST_EMAIL = os.getenv("CROCLENS_TEST_USER_EMAIL", "test@croclens.local").strip().lower()
TEST_PASSWORD = os.getenv("CROCLENS_TEST_USER_PASSWORD", "Test-user-123")
TEST_NAME = os.getenv("CROCLENS_TEST_USER_NAME", "CrocLens Test User")


def seed_test_user() -> None:
    Base.metadata.create_all(bind=engine)

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email == TEST_EMAIL).where(User.auth_provider == "local"))
        if user is None:
            user = User(
                id=str(uuid4()),
                email=TEST_EMAIL,
                full_name=TEST_NAME,
                status="active",
                auth_provider="local",
                password_hash=hash_password(TEST_PASSWORD),
            )
            db.add(user)
            db.flush()
            action = "created"
        else:
            user.full_name = TEST_NAME
            user.status = "active"
            user.password_hash = hash_password(TEST_PASSWORD)
            action = "updated"

        if user.profile is None:
            user.profile = UserProfile(
                id=str(uuid4()),
                beginner_mode=True,
                risk_tolerance="medium",
                time_horizon="medium",
                primary_goal="learn",
                household_income_range="prefer_not",
            )

        if not user.portfolios:
            user.portfolios.append(
                Portfolio(
                    id=str(uuid4()),
                    name="Test Portfolio",
                    base_currency="USD",
                )
            )
            db.flush()

        if not list_user_holdings(db, user):
            for holding in _default_holdings():
                create_holding(db, user, holding)

        if not list_user_liabilities(db, user):
            for liability in _default_liabilities():
                create_liability(db, user, liability)

        db.commit()

    print(f"Test user {action}: {TEST_EMAIL}")
    print("Password: set from CROCLENS_TEST_USER_PASSWORD or the documented local default.")


def _default_holdings() -> list[HoldingCreateRequest]:
    return [
        HoldingCreateRequest(
            symbol="VTI",
            name="Total Stock Market ETF",
            asset_type="ETFs",
            account_name="Taxable brokerage",
            quantity=18,
            cost_basis=4200,
            market_value=4700,
            as_of_date="2026-06-22",
        ),
        HoldingCreateRequest(
            symbol="CASH",
            name="Emergency cash",
            asset_type="Cash",
            account_name="Savings",
            quantity=0,
            market_value=6500,
            as_of_date="2026-06-22",
        ),
        HoldingCreateRequest(
            symbol="401K",
            name="Workplace retirement account",
            asset_type="Retirement",
            account_name="401(k)",
            quantity=0,
            market_value=12800,
            as_of_date="2026-06-22",
        ),
    ]


def _default_liabilities() -> list[LiabilityCreateRequest]:
    return [
        LiabilityCreateRequest(
            name="Student loan",
            liability_type="Student loan",
            balance=4100,
            interest_rate=0.045,
            minimum_payment=95,
            due_day=15,
        ),
        LiabilityCreateRequest(
            name="Credit card balance",
            liability_type="Credit card",
            balance=900,
            interest_rate=0.199,
            minimum_payment=45,
            due_day=22,
        ),
    ]


if __name__ == "__main__":
    seed_test_user()
