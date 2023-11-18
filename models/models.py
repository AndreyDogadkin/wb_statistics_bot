from sqlalchemy import BigInteger, BLOB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    """Тестовая модель для таблицы пользователя."""  # TODO Заменить на другие модели.
    __tablename__ = 'user_account'

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    wb_token_content = mapped_column(BLOB)
    wb_token_analytic = mapped_column(BLOB)
