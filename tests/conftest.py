import pytest
import os
import sys
import asyncio

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from httpx import AsyncClient, ASGITransport

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

from config.db_config import get_session, metaData
from auth.models import User
from books.models import Book
from app.main import app

load_dotenv()

db_host = os.getenv("DB_HOST")
db_port = os.getenv("DB_PORT")
test_db_database = os.getenv("TEST_DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

TEST_DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@{db_host}:{db_port}/{test_db_database}"

engine = create_async_engine(TEST_DATABASE_URL, echo=True, poolclass=NullPool)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

async def get_test_session() -> AsyncSession:
    async with TestingSessionLocal() as session:
        yield session

@pytest.fixture(scope="session")
async def async_client() -> AsyncClient:

    app.dependency_overrides[get_session] = get_test_session

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        yield client

    app.dependency_overrides.clear()

@pytest.fixture(scope="session")
async def session() -> AsyncSession:

    gen = get_test_session()
    session = await gen.__anext__()
    try:
        yield session
    finally:
        await gen.aclose()

@pytest.fixture(scope="session", autouse=True)
async def setup_db():

    async with engine.begin() as conn:

        await conn.run_sync(metaData.create_all)

    yield

    async with engine.begin() as conn:

        await conn.run_sync(metaData.drop_all)