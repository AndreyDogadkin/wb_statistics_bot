from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)

from bot.core import main_config

if main_config.database.DB_PROD:
    DB_URL = main_config.database.db_url
else:
    DB_URL = main_config.database.test_db_url

    @event.listens_for(Engine, 'connect')
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


class DBConnector:
    def __init__(self, url):
        self.engine = create_async_engine(
            url=url,
            echo=False,
        )
        self.session_factory = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            expire_on_commit=False,
            autocommit=False,
        )

    async def session_dependency(self):
        async with self.session_factory() as s:
            yield s
            await s.close()


database_connector = DBConnector(url=DB_URL)
