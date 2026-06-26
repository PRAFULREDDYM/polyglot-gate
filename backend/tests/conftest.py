import asyncio
import os
import sys
from pathlib import Path

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


os.environ["LLM_PROVIDER"] = "mock"

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

import app.models  # noqa: E402,F401
from app.config import settings  # noqa: E402
from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.services.llm_provider import MockProvider, get_llm_provider  # noqa: E402

settings.LLM_PROVIDER = "mock"


class SyncASGIClient:
    def __init__(self, app):
        self.app = app

    def get(self, url: str, **kwargs) -> httpx.Response:
        return asyncio.run(self._request("GET", url, **kwargs))

    def post(self, url: str, **kwargs) -> httpx.Response:
        return asyncio.run(self._request("POST", url, **kwargs))

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        transport = httpx.ASGITransport(app=self.app)
        async with httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        ) as test_client:
            return await test_client.request(method, url, **kwargs)


@pytest.fixture
def db(tmp_path) -> Session:
    db_path = tmp_path / "test.db"
    database_url = f"sqlite:///{db_path}"
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
        db_path.unlink(missing_ok=True)


@pytest.fixture
def llm() -> MockProvider:
    return MockProvider()


@pytest.fixture
def client(db: Session, llm: MockProvider):
    def override_get_db():
        yield db

    def override_get_llm_provider():
        return llm

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_llm_provider] = override_get_llm_provider

    yield SyncASGIClient(app)

    app.dependency_overrides.clear()
