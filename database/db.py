from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import load_config

Base = declarative_base()
engine = None
SessionLocal = None

async def init_db(database_url: str):
    global engine, SessionLocal
    engine = create_async_engine(database_url, echo=False)
    SessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
