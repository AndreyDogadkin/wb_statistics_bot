import datetime

from sqlalchemy import select, Select

from bot.base_messages.messages_templates import get_favorite_message_templates
from config_data.config import (
    REQUESTS_PER_DAY_LIMIT,
    DAY_LIMIT_DELTA,
    MAX_LEN_FAVORITES,
)
from database import database_connector
from database.models import User, Token, FavoriteRequest
from exceptions.wb_exceptions import ForUserException
from utils import AESEncryption


class DBMethods:

    session = database_connector.session_factory

    def __get_query_select_user(self, telegram_id: int) -> Select:
        """Запрос на получение пользователя."""
        query = select(User).where(
            User.telegram_id == telegram_id
        )
        return query

    def __get_query_select_token(
            self,
            telegram_id: int,
            content: bool = False,
            analytic: bool = False
    ) -> Select:
        """Запрос на получение токена."""
        select_field = Token
        if content:
            select_field = Token.wb_token_content
        elif analytic:
            select_field = Token.wb_token_analytic
        query = select(select_field).where(
            Token.user_id == telegram_id
        )
        return query

    async def get_user(self, telegram_id: int) -> User:
        """Проверка наличия пользователя в БД."""
        async with self.session() as s:
            query = self.__get_query_select_user(telegram_id)
            user = await s.execute(query)
            return user.scalar_one_or_none()

    async def add_user_if_not_exist(self, telegram_id: int) -> None:
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

    async def check_user_token(self, telegram_id: int) -> Token:
        """Проверка наличия токенов у пользователя."""
        async with self.session() as s:
            query = self.__get_query_select_token(telegram_id)
            token = await s.execute(query)
        return token.scalar_one_or_none()

    async def save_content_token(
            self,
            telegram_id: int,
            token_content: str
    ) -> None:
        """Сохранение или обновление токена типа 'Контент'."""
        tokens_dict: dict = AESEncryption.encrypt_keys(
            token_content=token_content
        )
        encrypted_token = tokens_dict.get('token_content')
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

    async def save_analytic_token(
            self,
            telegram_id: int,
            token_analytic: str
    ) -> None:
        """Сохранение или обновление токена типа 'Аналитика'."""
        tokens_dict: dict = AESEncryption.encrypt_keys(
            token_analytic=token_analytic
        )
        encrypted_token = tokens_dict.get('token_analytic')
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

    async def get_user_content_token(self, telegram_id: int) -> str | None:
        """Получение токена типа 'Контент'."""
        async with self.session.begin() as s:
            query = self.__get_query_select_token(telegram_id, content=True)
            token = await s.execute(query)
            token = token.scalar_one_or_none()
            if token:
                tokens_dict: dict = AESEncryption.encrypt_keys(
                    decrypt=True,
                    token_content=token
                )
                return tokens_dict.get('token_content')

    async def get_user_analytic_token(self, telegram_id: int) -> str | None:
        """Получение токена типа 'Аналитика'."""
        async with self.session.begin() as s:
            query = self.__get_query_select_token(telegram_id, analytic=True)
            token = await s.execute(query)
            token = token.scalar_one_or_none()
            if token:
                tokens_dict: dict = AESEncryption.encrypt_keys(
                    decrypt=True,
                    token_analytic=token
                )
                return tokens_dict.get('token_analytic')

    async def get_user_tokens(self, telegram_id: int) -> dict[str: str] | None:
        """Получить токены пользователя."""
        query = select(Token).where(
            Token.user_id == telegram_id
        )
        async with self.session() as s:
            decrypted_tokens = await s.execute(query)
            decrypted_tokens = decrypted_tokens.scalar_one_or_none()
            if (decrypted_tokens and decrypted_tokens.wb_token_content
                    and decrypted_tokens.wb_token_analytic):
                encrypted_tokens = AESEncryption.encrypt_keys(
                    decrypt=True,
                    wb_token_analytic=decrypted_tokens.wb_token_analytic,
                    wb_token_content=decrypted_tokens.wb_token_content
                )
                return encrypted_tokens

    async def set_user_last_request(
            self,
            telegram_id: int
    ) -> datetime.datetime:
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

    async def set_plus_one_to_user_requests_per_day(
            self,
            telegram_id: int
    ) -> None:
        """Прибавить пользователю счетчик запросов на 1."""
        async with self.session.begin() as s:
            query = self.__get_query_select_user(telegram_id)
            user = await s.execute(query)
            user = user.scalar_one()
            user.requests_per_day = user.requests_per_day + 1
            await s.commit()

    async def check_user_limits(
            self,
            telegram_id: int
    ) -> tuple[bool, int, datetime.datetime]:
        """Проверить и вернуть лимиты запросов пользователя."""
        async with self.session.begin() as s:
            query = self.__get_query_select_user(telegram_id)
            user = await s.execute(query)
            user = user.scalar_one()
            now = datetime.datetime.now()
            last_request: datetime.datetime = user.last_request
            requests_per_day = user.requests_per_day
            check = False, requests_per_day, last_request
            if (now - last_request) >= DAY_LIMIT_DELTA:
                user.requests_per_day = 0
                check = True, 0, last_request
            elif requests_per_day < REQUESTS_PER_DAY_LIMIT:
                check = True, requests_per_day, last_request
            await s.commit()
            return check

    async def check_favorite(
            self,
            telegram_id: int,
            nm_id: int,
            period: int
    ) -> FavoriteRequest | None:
        """Проверить наличие запроса пользователя в избранном."""
        query = select(FavoriteRequest).where(
            FavoriteRequest.user_id == telegram_id,
            FavoriteRequest.nm_id == nm_id,
            FavoriteRequest.period == period,
        )
        async with self.session() as s:
            favorite = await s.execute(query)
            favorite = favorite.scalar_one_or_none()
            return favorite

    async def check_limit_favorite(self, telegram_id: int) -> bool:
        """Проверить лимит на добавление в избранное."""
        query = select(FavoriteRequest).where(
            FavoriteRequest.user_id == telegram_id
        )
        async with self.session() as s:
            favorites = await s.execute(query)
            len_favorites = len(favorites.scalars().all())
            return len_favorites < MAX_LEN_FAVORITES

    async def add_favorite_request(
            self,
            telegram_id: int,
            name: str,
            nm_id: int,
            period: int,
            photo_url: str
    ) -> None:
        """Добавить запрос в избранное."""
        favorite = await self.check_favorite(telegram_id, nm_id, period)
        limit_favorites = await self.check_limit_favorite(telegram_id)
        if not favorite:
            if not limit_favorites:
                raise ForUserException(
                    message=get_favorite_message_templates[
                        'max_limit_favorite'
                    ]
                )
            async with self.session() as s:
                favorite = FavoriteRequest(
                    name=name,
                    user_id=telegram_id,
                    nm_id=nm_id,
                    period=period,
                    photo_url=photo_url
                )
                s.add(favorite)
                await s.commit()

    async def get_user_favorites(
            self,
            telegram_id: int
    ) -> list[FavoriteRequest]:
        """Получить все избранные запросы пользователя."""
        query = select(FavoriteRequest).where(
            FavoriteRequest.user_id == telegram_id
        )
        async with self.session() as s:
            favorites = await s.execute(query)
            favorites = favorites.scalars().all()
            return favorites

    async def delete_user_favorite(
            self,
            telegram_id: int,
            nm_id: int,
            period: int
    ):
        """Удалить избранный запрос пользователя."""
        query = select(FavoriteRequest).where(
            FavoriteRequest.user_id == telegram_id,
            FavoriteRequest.nm_id == nm_id,
            FavoriteRequest.period == period
        )
        async with self.session() as s:
            favorite = await s.execute(query)
            favorite = favorite.scalar_one()
            await s.delete(favorite)
            await s.commit()

    async def delete_user_account(self, telegram_id):
        """Удаление пользователя."""
        query = self.__get_query_select_user(telegram_id)
        async with self.session() as s:
            user = await s.execute(query)
            user = user.scalar_one_or_none()
            if user:
                await s.delete(user)
                await s.commit()
