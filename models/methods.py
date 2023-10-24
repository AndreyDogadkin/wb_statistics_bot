from sqlalchemy import select, update

from models.engine import session
from models.models import User

base_session = session


class DBMethods:

    def __init__(self, _session=base_session):
        self.session = _session

    async def check_user(self, telegram_id):
        """Проверка наличия пользователя в БД."""
        async with self.session.begin() as s:
            res = await s.execute(select(User).where(User.telegram_id == telegram_id))  # noq
        return res.scalar()

    async def add_user(self, telegram_id):
        """Добавление пользователя в БД."""
        user = await self.check_user(telegram_id)
        if not user:
            async with self.session() as s:
                user = User(telegram_id=telegram_id)
                s.add(user)
                await s.commit()

    async def save_standard_token(self, telegram_id, token_standard):
        """Сохранение токена 'Стандартный' в БД."""
        async with self.session() as s:
            await s.execute(update(
                User
            ).where(User.telegram_id == telegram_id).values(wb_token_standard=token_standard))  # noqa
            await s.commit()

    async def get_user_standard_token(self, telegram_id):
        """Получение токена 'Стандартный' в БД"""
        async with self.session.begin() as s:
            res = await s.execute(select(User.wb_token_standard).where(User.telegram_id == telegram_id))  # noqa
            return res.scalar()
