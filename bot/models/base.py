from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(DeclarativeBase):
    """Базовая абстрактная модель."""
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)
