from pathlib import Path
import os

os.environ["APP_ENV"] = "test"
os.environ["AUTH_MODE"] = "local"
os.environ["DATABASE_URL"] = "sqlite:///./apps/api/.pytest_cache/croclens-test.db"

Path("apps/api/.pytest_cache").mkdir(parents=True, exist_ok=True)

import pytest

from app import models  # noqa: F401
from app.db.base import Base
from app.db.session import engine


@pytest.fixture(autouse=True)
def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
