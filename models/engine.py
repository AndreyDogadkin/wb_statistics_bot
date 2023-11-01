import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config_data.config import get_config
from models.models import Base

config = get_config()

db_url = config.database.DB_URL

engine = create_async_engine(
    url=db_url,
    echo=False
)

session = async_sessionmaker(engine)


async def main():
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == '__main__':
    asyncio.run(main())
