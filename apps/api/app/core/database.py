import logging
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.core.config import settings

logger = logging.getLogger(__name__)

# Primary database configuration with local SQLite fallback for seamless local execution
database_url = settings.DATABASE_URL
if "postgresql" in database_url:
    database_url = "sqlite+aiosqlite:///./knowledge_assistant.db"
    logger.info("Defaulting to local SQLite database engine for local environment.")

engine = create_async_engine(database_url, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    """Ensure database tables exist on application startup."""
    import app.models.base  # Ensure all models are registered with Base.metadata
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables initialized successfully.")




