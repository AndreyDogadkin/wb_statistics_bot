import asyncio
from os import getenv

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from models.models import Base

load_dotenv()

db_url = getenv('DB_URL')

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
