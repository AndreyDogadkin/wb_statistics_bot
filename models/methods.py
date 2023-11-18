from sqlalchemy import select, update

from models.engine import session
from models.models import User
from utils.aes_encryption import AESEncryption

base_session = session


class DBMethods:

    def __init__(self, _session=base_session):
        self.session = _session

    async def check_user(self, telegram_id):
        """Проверка наличия пользователя в БД."""
        async with self.session.begin() as s:
            res = await s.execute(select(User).where(User.telegram_id == telegram_id))  # noqa
        return res.scalar()

    async def add_user(self, telegram_id):
        """Добавление пользователя в БД."""
        user = await self.check_user(telegram_id)
        if not user:
            async with self.session() as s:
                user = User(telegram_id=telegram_id)
                s.add(user)
                await s.commit()

    async def save_content_token(self, telegram_id, token_content):
        """Шифрование и сохранение токена типа 'Контент'."""
        encrypted_token = AESEncryption().encrypt(token_content)
        async with self.session() as s:
            await s.execute(update(
                User
            ).where(User.telegram_id == telegram_id).values(wb_token_content=encrypted_token))  # noqa
            await s.commit()

    async def save_analytic_token(self, telegram_id, token_analytic):
        """Шифрование и сохранение токена типа 'Аналитика'."""
        encrypted_token = AESEncryption().encrypt(token_analytic)
        async with self.session() as s:
            await s.execute(update(
                User
            ).where(User.telegram_id == telegram_id).values(wb_token_analytic=encrypted_token))
            await s.commit()

    async def get_user_content_token(self, telegram_id):
        """Получение токена типа 'Контент'."""
        async with self.session.begin() as s:
            res = await s.execute(select(User.wb_token_content).where(User.telegram_id == telegram_id))  # noqa
            token = res.scalar()
            if token:
                return AESEncryption().decrypt(token)

    async def get_user_analytic_token(self, telegram_id):
        """Получение токена типа 'Аналитика'."""
        async with self.session.begin() as s:
            res = await s.execute(select(User.wb_token_analytic).where(User.telegram_id == telegram_id))  # noqa
            token = res.scalar()
            if token:
                return AESEncryption().decrypt(token)
