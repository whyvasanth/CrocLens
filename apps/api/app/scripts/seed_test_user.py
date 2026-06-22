import os
from uuid import uuid4

from sqlalchemy import select

from app.core.security import hash_password
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.models import Portfolio, User, UserProfile


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

        db.commit()

    print(f"Test user {action}: {TEST_EMAIL}")
    print("Password: set from CROCLENS_TEST_USER_PASSWORD or the documented local default.")


if __name__ == "__main__":
    seed_test_user()
