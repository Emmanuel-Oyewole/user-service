import pytest
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.config.database import Base, get_db_session

TEST_DATABASE_URL = "postgresql+asyncpg://user:password@localhost:5432/test_db"
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=None
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()


@pytest.fixture(scope="function", autouse=True)
async def setup_database():
    """Setup and teardown test database for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client with database override."""
    
    async def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db_session] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test"
    ) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
async def cleanup_engine():
    """Cleanup database engine after all tests."""
    yield
    await test_engine.dispose()


# @pytest.fixture(scope="function")
# async def redis_client():
#     """Create test Redis client."""
#     from src.config.cache import redis_manager
    
#     test_redis = redis_manager(host="localhost", port=6379, db=15)
#     await test_redis.connect()
    
#     yield test_redis
    
#     if test_redis._redis_client:
#         await test_redis._redis_client.flushdb()
#     await test_redis.disconnect()