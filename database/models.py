from sqlalchemy import BigInteger, BLOB, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    """Тестовая модель для таблицы пользователя."""  # TODO Заменить на другие модели.
    __tablename__ = 'user_account'
    __table_args__ = ()

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_premium: Mapped[bool] = mapped_column(default=False)
    last_request = mapped_column(DateTime)
    requests_per_day = Mapped[int] = mapped_column(default=0)


class Tokens(Base):
    __tablename__ = 'user_tokens'
    __table_args__ = ()

    user_id: Mapped[int] = mapped_column(
        ForeignKey(User.telegram_id)
    )
    wb_token_content = mapped_column(BLOB)
    wb_token_analytic = mapped_column(BLOB)


class FavoriteRequests(Base):
    __tablename__ = 'user_favorites_requests'
    __table_args__ = ()

    user_id: Mapped[int] = mapped_column(
        ForeignKey(User.telegram_id)
    )
    nm_id: Mapped[int] = mapped_column(BigInteger)
    period: Mapped[int] = mapped_column()
