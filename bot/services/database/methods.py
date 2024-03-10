import logging

from sqlalchemy import select, Select, exists, func, union_all
from sqlalchemy.orm import selectinload

from bot.base.exceptions import ForUserException
from bot.base.messages_templates import get_favorite_message_templates
from bot.core.enums import Limits
from bot.models import User, Token, FavoriteRequest, WBAccount
from bot.services.database import database_connector
from bot.services.database.decorators import log_exceptions_db_methods
from bot.utils import AESEncryption

logger = logging.getLogger(__name__)


@log_exceptions_db_methods(logger)
class DBMethods:
    session = database_connector.session_factory

    def __get_query_select_user(self, telegram_id: int) -> Select:
        """
        Получить select запрос пользователя.
        :param telegram_id:
        :return: Select для исполнения запроса получения пользователя по
            телеграм id.
        """
        query = select(User).where(User.telegram_id == telegram_id)
        return query

    def __get_query_select_active_account(
        self,
        telegram_id: int,
    ) -> Select:
        """
        Получить select запрос активного аккаунта пользователя со
        связанными объектами.
        :param telegram_id:
        :return: Select для исполнения запроса на получение активного
            аккаунта пользователя.
        """
        query = (
            select(WBAccount)
            .where(
                WBAccount.user_id == telegram_id,
                WBAccount.is_now_active == True,  # noqa
            )
            .options(
                selectinload(WBAccount.tokens),
                selectinload(WBAccount.favorites),
            )
        )
        return query

    async def get_user(self, telegram_id) -> User | None:
        """Получить пользователя."""
        query = self.__get_query_select_user(telegram_id)
        async with self.session() as s:
            user = await s.execute(query)
            user = user.scalar_one_or_none()
            return user

    async def get_users_tokens_accounts_count(self) -> list[int]:
        """Получить количество зарегистрированных пользователей."""
        query_users = select(func.count(User.id))
        query_accounts = select(func.count(WBAccount.id))
        query_tokens = select(func.count(Token.id))
        async with self.session() as s:
            users_count = await s.execute(
                union_all(
                    query_users,
                    query_tokens,
                    query_accounts,
                )
            )
            return users_count.scalars().all()

    async def set_user_is_admin(
        self, telegram_id: int, add_to_admins: bool
    ) -> bool:
        """Установить пользователю значение is_admin."""
        query = self.__get_query_select_user(telegram_id)
        async with self.session() as s:
            user = await s.execute(query)
            user = user.scalar_one_or_none()
            if not user:
                return False
            user.is_admin = add_to_admins
            await s.commit()
            return True

    async def set_user_is_active(
        self, telegram_id: int, is_active: bool
    ) -> bool:
        """Установить пользователю значение is_active."""
        query = self.__get_query_select_user(telegram_id)
        async with self.session() as s:
            user = await s.execute(query)
            user = user.scalar_one_or_none()
            if not user:
                return False
            user.is_active = is_active
            await s.commit()
            return True

    async def user_exists(self, telegram_id: int) -> bool:
        """
        Проверить наличия пользователя в БД.
        :param telegram_id:
        :return: True если пользователь с таким telegram id есть,
            иначе False.
        """
        query = select(exists(User).where(User.telegram_id == telegram_id))
        async with self.session() as s:
            user = await s.execute(query)
            user = user.scalar_one()
            return user

    async def add_user_if_not_exist(self, telegram_id: int) -> None:
        """
        Добавление пользователя если такого не существует.
        При успешном добавлении пользователя создается его базовый аккаунт
        для работы с WB API.
        :param telegram_id:
        :return: None
        """
        user_exists: bool = await self.user_exists(telegram_id)
        if not user_exists:
            async with self.session() as s:
                user = User(
                    telegram_id=telegram_id,
                )
                user.wb_accounts.append(
                    WBAccount(
                        user_id=telegram_id,
                        name='Мой магазин',
                        is_now_active=True,
                    )
                )
                s.add(user)
                await s.commit()

    async def get_user_accounts(
        self, telegram_id: int
    ) -> list[WBAccount] | None:
        """
        Получить все аккаунты выбранного пользователя.
        :param telegram_id:
        :return: List[WBAccount] если есть один или больше аккаунтов,
            иначе None.
        """
        query = select(WBAccount).where(WBAccount.user_id == telegram_id)
        async with self.session() as s:
            accounts = await s.execute(query)
            accounts = accounts.scalars().all()
            if accounts:
                return accounts

    async def get_active_account(self, telegram_id) -> WBAccount | None:
        """
        Получить активный аккаунт пользователя.
        :param telegram_id:
        :return: WBAccount если активный существует, иначе None
        """
        query = self.__get_query_select_active_account(telegram_id)
        async with self.session() as s:
            active_account = await s.execute(query)
            return active_account.scalar_one_or_none()

    async def check_limit_accounts(self, telegram_id: int) -> bool:
        """
        Проверить лимит созданных аккаунтов пользователя.
        :param telegram_id:
        :return: True если лимит не достигнут, иначе False.
        """
        query = (
            select(func.count())
            .select_from(WBAccount)
            .where(WBAccount.user_id == telegram_id)
        )
        async with self.session() as s:
            accounts_count = await s.execute(query)
            accounts_count = accounts_count.scalar()
            if accounts_count < Limits.MAX_LIMIT_ACCOUNTS:
                return True
            return False

    async def check_account_name(
        self, telegram_id: int, account_name: str
    ) -> bool:
        """
        Проверить наличие у пользователя аккаунтов с переданным названием.
        :param telegram_id:
        :param account_name:
        :return: True если аккаунт с таким именем уже существует,
            иначе False.
        """
        query = select(
            exists(WBAccount).where(
                WBAccount.user_id == telegram_id,
                WBAccount.name == account_name,
            )
        )
        async with self.session() as s:
            account = await s.execute(query)
            return account.scalar()

    async def create_user_account(
        self, telegram_id: int, account_name: str
    ) -> bool:
        """
        Создать новый аккаунт пользователя.
        При создании новый аккаунт становится активным, а старый
        деактивируется.
        :param telegram_id:
        :param account_name:
        :return: True если аккаунт успешно создан, False если аккаунт с
            таким именем уже существует.
        """
        name_exists = await self.check_account_name(telegram_id, account_name)
        if not name_exists:
            active_account = await self.get_active_account(telegram_id)
            account = WBAccount(
                user_id=telegram_id, name=account_name, is_now_active=True
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
        """
        Изменить название существующего аккаунта пользователя.
        :param telegram_id:
        :param account_id:
        :param new_name:
        :return: True если название аккаунта успешно изменено, False если
            аккаунт с таким именем уже существует или изменяемого аккаунта
            не существует.
        """
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
        self, telegram_id: int, select_account_id: int
    ) -> bool:
        """
        Изменить активный аккаунт пользователя.
        При изменении активный аккаунт становится деактивированным,
        переданный аккаунт - активным
        :param telegram_id:
        :param select_account_id:
        :return: True если активный аккаунт успешно изменен, иначе False.
        """
        active_account = await self.get_active_account(telegram_id=telegram_id)
        query = select(WBAccount).where(
            WBAccount.user_id == telegram_id, WBAccount.id == select_account_id
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

    async def delete_account(self, telegram_id: int, account_id: int) -> bool:
        """
        Удалить аккаунт пользователя.
        Невозможно удалить единственный аккаунт пользователя.
        Невозможно удалить активный аккаунт пользователя.
        :param telegram_id:
        :param account_id:
        :return: True если аккаунт успешно удален, False если аккаунта не
            существует.
        """
        account_query = select(WBAccount).where(
            WBAccount.user_id == telegram_id, WBAccount.id == account_id
        )
        accounts_count_query = (
            select(func.count())
            .select_from(WBAccount)
            .where(WBAccount.user_id == telegram_id)
        )
        async with self.session() as s:
            accounts_count = await s.execute(accounts_count_query)
            accounts_count = accounts_count.scalar()
            account = await s.execute(account_query)
            account = account.scalar_one_or_none()
            if account and not account.is_now_active and accounts_count > 1:
                await s.delete(account)
                await s.commit()
                return True
            return False

    async def __get_user_token_and_account_id(
        self, telegram_id: int
    ) -> tuple[Token | None, WBAccount]:
        """
        Получить Токены пользователя и id активного аккаунта.
        :param telegram_id:
        :return: Token если запись создана,
            id активного аккаунта.
        """
        """Проверка наличия токенов у пользователя."""
        async with self.session() as s:
            query = self.__get_query_select_active_account(telegram_id)
            account = await s.execute(query)
            account = account.scalar_one_or_none()
            return account.tokens, account.id

    async def save_content_token(
        self, telegram_id: int, token_content: str
    ) -> None:
        """
        Сохранение или обновление токена типа 'Контент'.
        :param telegram_id:
        :param token_content:
        :return:
        """
        tokens_dict: dict = AESEncryption.encrypt_keys(
            token_content=token_content
        )
        encrypted_token = tokens_dict.get('token_content')
        async with self.session() as s:
            token, account_id = await self.__get_user_token_and_account_id(
                telegram_id
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
        self, telegram_id: int, token_analytic: str
    ) -> None:
        """
        Сохранение или обновление токена типа 'Аналитика'.
        :param telegram_id:
        :param token_analytic:
        :return:
        """
        tokens_dict: dict = AESEncryption.encrypt_keys(
            token_analytic=token_analytic
        )
        encrypted_token = tokens_dict.get('token_analytic')
        async with self.session() as s:
            token, account_id = await self.__get_user_token_and_account_id(
                telegram_id
            )
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
        """
        Получение токена типа "Контент".
        :param telegram_id:
        :return: Токен "Контент" пользователя если он существует, иначе None.
        """
        query = self.__get_query_select_active_account(telegram_id)
        async with self.session.begin() as s:
            account = await s.execute(query)
            account = account.scalar_one_or_none()
            token = account.tokens
            if token and token.wb_token_content:
                tokens_dict: dict = AESEncryption.encrypt_keys(
                    decrypt=True, token_content=token.wb_token_content
                )
                return tokens_dict.get('token_content')

    async def get_user_analytic_token(self, telegram_id: int) -> str | None:
        """
        Получение токена типа "Аналитика".
        :param telegram_id:
        :return: Токен "Аналитика" пользователя если он существует, иначе None.
        """
        query = self.__get_query_select_active_account(telegram_id)
        async with self.session.begin() as s:
            account = await s.execute(query)
            account = account.scalar_one_or_none()
            token = account.tokens
            if token and token.wb_token_analytic:
                tokens_dict: dict = AESEncryption.encrypt_keys(
                    decrypt=True, token_analytic=token.wb_token_analytic
                )
                return tokens_dict.get('token_analytic')

    async def get_user_tokens(self, telegram_id: int) -> dict[str:str] | None:
        """
        Получить токены "Контент" и "Аналитика" пользователя.
        :param telegram_id:
        :return: Токены пользователя обоих типов, если существуют оба токена,
            иначе None
        """
        query = (
            select(WBAccount)
            .where(
                WBAccount.is_now_active == True,
                WBAccount.user_id == telegram_id,
            )
            .options(selectinload(WBAccount.tokens))
        )
        async with self.session() as s:
            account = await s.execute(query)
            account = account.scalar_one_or_none()
            decrypted_tokens = account.tokens
            if (
                decrypted_tokens
                and decrypted_tokens.wb_token_content
                and decrypted_tokens.wb_token_analytic
            ):
                encrypted_tokens = AESEncryption.encrypt_keys(
                    decrypt=True,
                    wb_token_analytic=decrypted_tokens.wb_token_analytic,
                    wb_token_content=decrypted_tokens.wb_token_content,
                )
                return encrypted_tokens

    async def check_and_get_favorite(
        self, account_id: int, nm_id: int, period: int
    ) -> FavoriteRequest | None:
        """
        Проверить наличие запроса пользователя в избранном.
        :param account_id:
        :param nm_id:
        :param period:
        :return: FavoriteRequest пользователя если такой существует,
            иначе None
        """
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
        """
        Проверить лимит на добавление в избранное.
        :param telegram_id:
        :return: Tuple: bool: Количество избранных меньше максимального лимита,
            int: id активного аккаунта пользователя.
        """
        query = self.__get_query_select_active_account(telegram_id=telegram_id)
        async with self.session() as s:
            account = await s.execute(query)
            account = account.scalar_one_or_none()
            len_favorites = len(account.favorites)
            return len_favorites < Limits.MAX_LIMIT_FAVORITES, account.id

    async def add_favorite_request(
        self,
        telegram_id: int,
        name: str,
        nm_id: int,
        period: int,
        photo_url: str,
    ) -> None:
        """
        Добавить запрос в избранное.
        :param telegram_id:
        :param name:
        :param nm_id:
        :param period:
        :param photo_url:
        :return:
        :raises: ForUserException: Если у пользователя закончился лимит
            избранных запросов.
        """
        limit_favorites, account_id = await self.check_limit_favorite(
            telegram_id
        )
        favorite = await self.check_and_get_favorite(account_id, nm_id, period)
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
                    photo_url=photo_url,
                )
                s.add(favorite)
                await s.commit()

    async def get_user_favorites(
        self, telegram_id: int
    ) -> list[FavoriteRequest]:
        """
        Получить все избранные запросы пользователя.
        :param telegram_id:
        :return: Количество избранных запросов пользователя.
        """
        query = self.__get_query_select_active_account(telegram_id=telegram_id)
        async with self.session() as s:
            account = await s.execute(query)
            account = account.scalar_one_or_none()
            favorites = account.favorites
            return favorites

    async def delete_user_favorite(
        self, telegram_id: int, nm_id: int, period: int
    ) -> None:
        """
        Удалить избранный запрос пользователя.
        :param telegram_id:
        :param nm_id:
        :param period:
        :return:
        """
        account = await self.get_active_account(telegram_id)
        query = select(FavoriteRequest).where(
            FavoriteRequest.wb_account_id == account.id,
            FavoriteRequest.nm_id == nm_id,
            FavoriteRequest.period == period,
        )
        async with self.session() as s:
            favorite = await s.execute(query)
            favorite = favorite.scalar_one()
            await s.delete(favorite)
            await s.commit()

    async def delete_user(self, telegram_id) -> bool:
        """
        Удалить пользователя.
        :param telegram_id:
        :return: True если пользователь успешно удален, иначе False&
        """
        query = self.__get_query_select_user(telegram_id)
        async with self.session() as s:
            user = await s.execute(query)
            user = user.scalar_one_or_none()
            if user:
                await s.delete(user)
                await s.commit()
                return True
        return False
