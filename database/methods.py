import datetime

from sqlalchemy import select, Select

from config_data.config import REQUESTS_PER_DAY_LIMIT, DAY_LIMIT_DELTA
from database import database_connector
from database.models import User, Token
from utils import AESEncryption


class DBMethods:

    session = database_connector.session_factory

    def __get_query_select_user(self, telegram_id) -> Select:
        query = select(User).where(
            User.telegram_id == telegram_id
        )
        return query

    def __get_query_select_token(
            self,
            telegram_id,
            content: bool = False,
            analytic: bool = False
    ) -> Select:
        select_field = Token
        if content:
            select_field = Token.wb_token_content
        elif analytic:
            select_field = Token.wb_token_analytic
        query = select(select_field).where(
            Token.user_id == telegram_id
        )
        return query

    async def get_user(self, telegram_id) -> User:
        """Проверка наличия пользователя в БД."""
        async with self.session() as s:
            query = self.__get_query_select_user(telegram_id)
            user = await s.execute(query)
            return user.scalar_one_or_none()

    async def add_user(self, telegram_id) -> None:
        """Добавление пользователя в БД."""
        user = await self.get_user(telegram_id)
        if not user:
            async with self.session() as s:
                user = User(
                    telegram_id=telegram_id,
                    last_request=datetime.datetime.now()
                )
                s.add(user)
                await s.commit()

    async def check_user_token(self, telegram_id) -> Token:
        """Проверка наличия токенов у пользователя."""
        async with self.session() as s:
            query = self.__get_query_select_token(telegram_id)
            token = await s.execute(query)
        return token.scalar_one_or_none()

    async def save_content_token(self, telegram_id, token_content) -> None:
        """Сохранение или обновление токена типа 'Контент'."""
        encrypted_token = AESEncryption().encrypt(token_content)
        async with self.session() as s:
            token = await self.check_user_token(telegram_id)
            if token:
                s.add(token)
                token.wb_token_content = encrypted_token
            else:
                token = Token(
                    user_id=telegram_id,
                    wb_token_content=encrypted_token,
                )
                s.add(token)
            await s.commit()

    async def save_analytic_token(self, telegram_id, token_analytic) -> None:
        """Сохранение или обновление токена типа 'Аналитика'."""
        encrypted_token = AESEncryption().encrypt(token_analytic)
        async with self.session() as s:
            token = await self.check_user_token(telegram_id)
            if token:
                s.add(token)
                token.wb_token_analytic = encrypted_token
            else:
                token = Token(
                    user_id=telegram_id,
                    wb_token_analytic=encrypted_token,
                )
                s.add(token)
            await s.commit()

    async def get_user_content_token(self, telegram_id) -> Token | None:
        """Получение токена типа 'Контент'."""
        async with self.session.begin() as s:
            query = self.__get_query_select_token(telegram_id, content=True)
            token = await s.execute(query)
            token = token.scalar_one_or_none()
            if token:
                return AESEncryption().decrypt(
                    token
                )

    async def get_user_analytic_token(self, telegram_id) -> Token | None:
        """Получение токена типа 'Аналитика'."""
        async with self.session.begin() as s:
            query = self.__get_query_select_token(telegram_id, analytic=True)
            token = await s.execute(query)
            token = token.scalar_one_or_none()
            if token:
                return AESEncryption().decrypt(
                    token
                )

    async def set_user_last_request(self, telegram_id) -> datetime:
        """Установить пользователю дату и время последнего запроса."""
        async with self.session.begin() as s:
            query = self.__get_query_select_user(telegram_id)
            user = await s.execute(query)
            user = user.scalar_one()
            now = datetime.datetime.now()
            last_request = user.last_request
            if (now - last_request) >= DAY_LIMIT_DELTA:
                last_request = now
                user.last_request = last_request
            await s.commit()
        return last_request

    async def set_plus_one_to_user_requests_per_day(self, telegram_id) -> None:
        """Прибавить пользователю счетчик запросов на 1."""
        async with self.session.begin() as s:
            query = self.__get_query_select_user(telegram_id)
            user = await s.execute(query)
            user = user.scalar_one()
            user.requests_per_day = user.requests_per_day + 1
            await s.commit()

    async def check_user_limits(self, telegram_id) -> tuple[bool, int, datetime]:
        """Проверить и вернуть лимиты запросов пользователя."""
        async with self.session.begin() as s:
            query = self.__get_query_select_user(telegram_id)
            user = await s.execute(query)
            user = user.scalar_one()
            now = datetime.datetime.now()
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
