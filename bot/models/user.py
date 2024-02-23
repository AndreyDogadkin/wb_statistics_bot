from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint, BigInteger
from sqlalchemy.orm import mapped_column, Mapped, relationship

from bot.models.base import Base

if TYPE_CHECKING:
    from bot.models.account import WBAccount


class User(Base):
    """Модель для таблицы пользователя."""

    __tablename__ = 'user_account'
    __table_args__ = (
        UniqueConstraint(
            'telegram_id',
            name='telegram_id_uniq'
        ),
    )

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_premium: Mapped[bool] = mapped_column(default=False)
    is_admin: Mapped[bool] = mapped_column(default=False)

    wb_accounts: Mapped[list['WBAccount']] = relationship(
        'WBAccount',
        back_populates='user',
        cascade='all, delete',
        passive_deletes=True,
        single_parent=True
    )
