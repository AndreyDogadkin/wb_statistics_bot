import asyncio

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config_data.config import get_config, BASE_DIR
from database.models import Base

config = get_config()
if config.database.DB_PROD:
    DB_URL = config.database.DB_URL
else:
    DB_URL = 'sqlite+aiosqlite:////' + str(BASE_DIR) + '/test_database.sqlite3'

engine = create_async_engine(
    url=DB_URL,
    echo=False
)

session = async_sessionmaker(engine)


async def main():
    async with engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)


if __name__ == '__main__':
    asyncio.run(main())
