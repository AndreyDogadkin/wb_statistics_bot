import datetime

from sqlalchemy import select, update, insert

from config_data.config import REQUESTS_PER_DAY_LIMIT, DAY_LIMIT_DELTA
from database.engine import session
from database.models import User, Token
from utils.aes_encryption import AESEncryption

base_session = session


class DBMethods:

    def __init__(self, _session=base_session):
        self.session = _session

    async def check_user(self, telegram_id):
        """Проверка наличия пользователя в БД."""
        async with self.session.begin() as s:
            res = await s.execute(
                select(
                    User
                ).where(
                    User.telegram_id == telegram_id
                )
            )
        return res.scalar_one_or_none()

    async def add_user(self, telegram_id):
        """Добавление пользователя в БД."""
        user = await self.check_user(telegram_id)
        if not user:
            async with self.session() as s:
                user = User(
                    telegram_id=telegram_id,
                    last_request=datetime.datetime.now()
                )
                s.add(user)
                await s.commit()

    async def check_user_token(self, telegram_id):
        """Проверка наличия токенов у пользователя."""
        async with self.session.begin() as s:
            res = await s.execute(
                select(
                    Token
                ).where(
                    Token.user_id == telegram_id
                )
            )
            token = res.scalar_one_or_none()
        return token

    async def save_content_token(self, telegram_id, token_content):
        """Сохранение токена типа 'Контент'."""
        encrypted_token = AESEncryption().encrypt(token_content)
        async with self.session() as s:
            check = await self.check_user_token(telegram_id)
            if check:
                await s.execute(
                    update(
                        Token
                    ).where(
                        Token.user_id == telegram_id
                    ).values(
                        wb_token_content=encrypted_token
                    )
                )
            else:
                await s.execute(
                    insert(
                        Token
                    ).values(
                        wb_token_content=encrypted_token,
                        user_id=telegram_id
                    )
                )
            await s.commit()

    async def save_analytic_token(self, telegram_id, token_analytic):
        """Сохранение токена типа 'Аналитика'."""
        encrypted_token = AESEncryption().encrypt(token_analytic)
        async with self.session() as s:
            check = await self.check_user_token(telegram_id)
            if check:
                await s.execute(
                    update(
                        Token
                    ).where(
                        Token.user_id == telegram_id
                    ).values(
                        wb_token_analytic=encrypted_token
                    )
                )
            else:
                await s.execute(
                    insert(
                        Token
                    ).values(
                        wb_token_analytic=encrypted_token,
                        user_id=telegram_id
                    )
                )
            await s.commit()

    async def get_user_content_token(self, telegram_id):
        """Получение токена типа 'Контент'."""
        async with self.session.begin() as s:
            res = await s.execute(
                select(
                    Token.wb_token_content
                ).where(
                    Token.user_id == telegram_id
                )
            )
            token = res.scalar_one_or_none()
        if token:
            return AESEncryption().decrypt(token)

    async def get_user_analytic_token(self, telegram_id):
        """Получение токена типа 'Аналитика'."""
        async with self.session.begin() as s:
            res = await s.execute(
                select(
                    Token.wb_token_analytic
                ).where(
                    Token.user_id == telegram_id
                )
            )
            token = res.scalar_one_or_none()
        if token:
            return AESEncryption().decrypt(token)

    async def set_user_last_request(self, telegram_id):
        """Установить пользователю дату и время последнего запроса."""
        async with self.session.begin() as s:
            res = await s.execute(
                select(
                    User
                ).where(
                    User.telegram_id == telegram_id
                )
            )
            user = res.scalar_one()
            now = datetime.datetime.now()
            last_request = user.last_request
            if (now - last_request) >= DAY_LIMIT_DELTA:
                last_request = now
                user.last_request = last_request
            await s.commit()
        return last_request

    async def set_plus_one_to_user_requests_per_day(self, telegram_id):
        """Прибавить пользователю счетчик запросов на 1."""
        async with self.session.begin() as s:
            res = await s.execute(
                select(
                    User
                ).where(
                    User.telegram_id == telegram_id
                )
            )
            user = res.scalar()
            user.requests_per_day = user.requests_per_day + 1
            await s.commit()

    async def check_user_limits(self, telegram_id):
        """Проверить и вернуть лимиты запросов пользователя."""
        now = datetime.datetime.now()
        async with self.session.begin() as s:
            res = await s.execute(
                select(
                    User
                ).where(
                    User.telegram_id == telegram_id
                )
            )
            user = res.scalar_one()
            last_request = user.last_request
            requests_per_day = user.requests_per_day
            check = False, requests_per_day, last_request
            if (now - last_request) >= DAY_LIMIT_DELTA:
                user.requests_per_day = 0
                check = True, 0, last_request
            elif requests_per_day < REQUESTS_PER_DAY_LIMIT:
                check = True, requests_per_day, last_request
            await s.commit()
            return check
