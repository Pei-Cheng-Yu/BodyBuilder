from app.db.config import settings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,  # Set True to see SQL logs in console
    pool_pre_ping=True,  # Handles dropped connections automatically
)

# Create Session Factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


# Use for routes\
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
