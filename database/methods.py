import datetime

from sqlalchemy import select, Select, exists, func
from sqlalchemy.orm import selectinload

from bot.base_messages.messages_templates import get_favorite_message_templates
from config_data.config import (
    REQUESTS_PER_DAY_LIMIT,
    DAY_LIMIT_DELTA,
    MAX_LIMIT_FAVORITES,
    MAX_LIMIT_ACCOUNTS
)
from database import database_connector
from database.models import User, Token, FavoriteRequest, WBAccount
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

    def __get_query_select_account(
            self,
            telegram_id: int,
    ) -> Select:
        """Запрос на получение токена."""
        query = select(WBAccount).where(
            WBAccount.user_id == telegram_id,
            WBAccount.is_now_active == True  # noqa
        ).options(
            selectinload(WBAccount.tokens),
            selectinload(WBAccount.favorites)
        )
        return query

    async def get_user(self, telegram_id: int) -> User | None:
        """Проверка наличия пользователя в БД."""
        async with self.session() as s:
            query = self.__get_query_select_user(telegram_id)
            user = await s.execute(query)
            return user.scalar_one_or_none()

    async def add_user_if_not_exist(self, telegram_id: int) -> None:
        """
        Добавление пользователя если такого не существует.
        Добавление базового аккаунта созданному пользователю.
        """
        user = await self.get_user(telegram_id)
        if not user:
            async with self.session() as s:
                user = User(
                    telegram_id=telegram_id,
                    last_request=datetime.datetime.now()
                )
                user.wb_accounts.append(
                    WBAccount(
                        user_id=telegram_id,
                        name=f'Мой магазин',
                        is_now_active=True
                    )
                )
                s.add(user)
                await s.commit()

    async def get_user_accounts(
            self,
            telegram_id: int
    ) -> list[WBAccount] | None:
        """Получить все аккаунты выбранного пользователя."""
        query = select(WBAccount).where(
            WBAccount.user_id == telegram_id
        )
        async with self.session() as s:
            accounts = await s.execute(query)
            accounts = accounts.scalars().all()
            if accounts:
                return accounts

    async def get_active_account(self, telegram_id) -> WBAccount | None:
        """Получить активный аккаунт пользователя."""
        query = select(WBAccount).where(
            WBAccount.user_id == telegram_id,
            WBAccount.is_now_active == True
        )
        async with self.session() as s:
            active_account = await s.execute(query)
            return active_account.scalar_one_or_none()

    async def check_limit_accounts(self, telegram_id: int) -> bool:
        """Проверить достигнут ли лимит созданных аккаунтов."""
        query = select(func.count()).select_from(WBAccount).where(
            WBAccount.user_id == telegram_id
        )
        async with self.session() as s:
            accounts_count = await s.execute(query)
            accounts_count = accounts_count.scalar()
            if accounts_count < MAX_LIMIT_ACCOUNTS:
                return True
            return False

    async def check_account_name(
            self,
            telegram_id: int,
            account_name: str
    ) -> WBAccount:
        """Проверка на повторяющиеся имена."""
        query = select(
            exists(WBAccount).where(
                WBAccount.user_id == telegram_id,
                WBAccount.name == account_name
            )
        )
        async with self.session() as s:
            account = await s.execute(query)
            return account.scalar()

    async def create_user_account(
            self,
            telegram_id: int,
            account_name: str
    ) -> bool:
        """
        Создать новый аккаунт пользователя.
        При создании новый аккаунт становится активным, а старый
        деактивируется.
        """
        name_exists = await self.check_account_name(telegram_id, account_name)
        if not name_exists:
            active_account = await self.get_active_account(telegram_id)
            account = WBAccount(
                user_id=telegram_id,
                name=account_name,
                is_now_active=True
            )
            async with self.session() as s:
                s.add(active_account)
                s.add(account)
                active_account.is_now_active = False
                await s.commit()
            return True
        return False

    async def change_account_name(
            self,
            telegram_id: int,
            account_id: int,
            new_name: str,
    ) -> bool:
        """Изменить имя аккаунта если имя не занято."""
        name_exists = await self.check_account_name(telegram_id, new_name)
        if not name_exists:
            query = select(WBAccount).where(
                WBAccount.id == account_id,
                WBAccount.user_id == telegram_id,
            )
            async with self.session() as s:
                account = await s.execute(query)
                account = account.scalar_one_or_none()
                if account:
                    account.name = new_name
                    await s.commit()
                    return True
        return False

    async def change_active_account(
            self,
            telegram_id: int,
            select_account_id: int
    ) -> bool:
        """Изменить активный аккаунт пользователя."""
        active_account = await self.get_active_account(telegram_id=telegram_id)
        query = select(WBAccount).where(
            WBAccount.user_id == telegram_id,
            WBAccount.id == select_account_id
        )
        if active_account.id != select_account_id:
            async with self.session() as s:
                select_account = await s.execute(query)
                select_account = select_account.scalar_one_or_none()
                s.add(active_account)
                active_account.is_now_active = False
                select_account.is_now_active = True
                await s.commit()
            return True
        return False

    async def delete_account(self, telegram_id: int, account_id: int):
        """Удалить аккаунт пользователя."""
        pass

    async def __get_user_token_and_account_id(
            self,
            telegram_id: int
    ) -> tuple[Token, WBAccount]:
        """Проверка наличия токенов у пользователя."""
        async with self.session() as s:
            query = self.__get_query_select_account(telegram_id)
            account = await s.execute(query)
            account = account.scalar_one_or_none()
            return account.tokens, account.id

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
            token, account_id = (
                await self.__get_user_token_and_account_id(telegram_id)
            )
            if token:
                s.add(token)
                token.wb_token_content = encrypted_token
            else:
                token = Token(
                    wb_account_id=account_id,
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
            token, account_id = await self.__get_user_token_and_account_id(
                telegram_id)
            if token:
                s.add(token)
                token.wb_token_analytic = encrypted_token
            else:
                token = Token(
                    wb_account_id=account_id,
                    wb_token_analytic=encrypted_token,
                )
                s.add(token)
            await s.commit()

    async def get_user_content_token(self, telegram_id: int) -> str | None:
        """Получение токена типа 'Контент'."""
        query = self.__get_query_select_account(telegram_id)
        async with self.session.begin() as s:
            account = await s.execute(query)
            account = account.scalar_one_or_none()
            token = account.tokens
            if token and token.wb_token_content:
                tokens_dict: dict = AESEncryption.encrypt_keys(
                    decrypt=True,
                    token_content=token.wb_token_content
                )
                return tokens_dict.get('token_content')

    async def get_user_analytic_token(self, telegram_id: int) -> str | None:
        """Получение токена типа 'Аналитика'."""
        query = self.__get_query_select_account(telegram_id)
        async with self.session.begin() as s:
            account = await s.execute(query)
            account = account.scalar_one_or_none()
            token = account.tokens
            if token and token.wb_token_analytic:
                tokens_dict: dict = AESEncryption.encrypt_keys(
                    decrypt=True,
                    token_analytic=token.wb_token_analytic
                )
                return tokens_dict.get('token_analytic')

    async def get_user_tokens(self, telegram_id: int) -> dict[str: str] | None:
        """Получить токены пользователя."""
        query = select(WBAccount).where(
            WBAccount.is_now_active == True,
            WBAccount.user_id == telegram_id
        ).options(
            selectinload(WBAccount.tokens)
        )
        async with self.session() as s:
            account = await s.execute(query)
            account = account.scalar_one_or_none()
            decrypted_tokens = account.tokens
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
            account_id: int,
            nm_id: int,
            period: int
    ) -> FavoriteRequest | None:
        """Проверить наличие запроса пользователя в избранном."""
        query = select(FavoriteRequest).where(
            FavoriteRequest.wb_account_id == account_id,
            FavoriteRequest.nm_id == nm_id,
            FavoriteRequest.period == period,
        )
        async with self.session() as s:
            favorite = await s.execute(query)
            favorite = favorite.scalar_one_or_none()
            return favorite

    async def check_limit_favorite(self, telegram_id: int) -> tuple[bool, int]:
        """Проверить лимит на добавление в избранное."""
        query = self.__get_query_select_account(telegram_id=telegram_id)
        async with self.session() as s:
            account = await s.execute(query)
            account = account.scalar_one_or_none()
            len_favorites = len(account.favorites)
            return len_favorites < MAX_LIMIT_FAVORITES, account.id

    async def add_favorite_request(
            self,
            telegram_id: int,
            name: str,
            nm_id: int,
            period: int,
            photo_url: str
    ) -> None:
        """Добавить запрос в избранное."""
        limit_favorites, account_id = await self.check_limit_favorite(
            telegram_id
        )
        favorite = await self.check_favorite(account_id, nm_id, period)
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
                    wb_account_id=account_id,
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
        query = self.__get_query_select_account(telegram_id=telegram_id)
        async with self.session() as s:
            account = await s.execute(query)
            account = account.scalar_one_or_none()
            favorites = account.favorites
            return favorites

    async def delete_user_favorite(
            self,
            telegram_id: int,
            nm_id: int,
            period: int
    ):
        """Удалить избранный запрос пользователя."""
        account = await self.get_active_account(telegram_id)
        query = select(FavoriteRequest).where(
            FavoriteRequest.wb_account_id == account.id,
            FavoriteRequest.nm_id == nm_id,
            FavoriteRequest.period == period
        )
        async with self.session() as s:
            favorite = await s.execute(query)
            favorite = favorite.scalar_one()
            await s.delete(favorite)
            await s.commit()

    async def delete_user(self, telegram_id):
        """Удаление пользователя."""
        query = self.__get_query_select_user(telegram_id)
        async with self.session() as s:
            user = await s.execute(query)
            user = user.scalar_one_or_none()
            if user:
                await s.delete(user)
                await s.commit()
