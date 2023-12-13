from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
)

from config_data import main_config

if main_config.database.DB_PROD:
    DB_URL = main_config.database.DB_URL
else:
    DB_URL = main_config.database.DB_URL_TEST


class DBConnector:
    def __init__(self, url, echo=False):
        self.engine = create_async_engine(
            url=url,
            echo=echo,
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
