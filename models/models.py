from sqlalchemy import String, MetaData, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


meta = MetaData()


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user_account'

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    wb_token_standard: Mapped[str | None] = mapped_column(String(150))
    wb_token_statistics: Mapped[str | None] = mapped_column(String(150))
