from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Base class for all models
Base = declarative_base()

# Create Async Engine
try:
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        future=True,
        pool_pre_ping=True
    )
    # Async Session Local
    AsyncSessionLocal = async_sessionmaker(
        engine, expire_on_commit=False, class_=AsyncSession
    )
except Exception as e:
    logger.error(f"Failed to initialize database engine: {e}")
    engine = None
    AsyncSessionLocal = None

async def init_db():
    """Create all tables asynchronously."""
    if engine is None:
        return
    async with engine.begin() as conn:
        # Avoid dropping tables in production. 
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    """Dependency for getting DB session."""
    if AsyncSessionLocal is None:
        yield None
        return
        
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
