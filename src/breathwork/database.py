from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from . import config

engine = create_async_engine(f"sqlite+aiosqlite:///{config.DB_PATH}", echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    from .models import Base

    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    config.VIDEOS_DIR.mkdir(exist_ok=True)
    config.THUMBNAILS_DIR.mkdir(exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session():
    async with async_session() as session:
        yield session
