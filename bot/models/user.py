from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, UniqueConstraint, BigInteger, DateTime
from sqlalchemy.orm import mapped_column, Mapped, relationship

from bot.models.base import Base

if TYPE_CHECKING:
    from bot.models.account import WBAccount


class User(Base):
    """Модель для таблицы пользователя."""

    __tablename__ = 'user_account'
    __table_args__ = (
        CheckConstraint(
            'requests_per_day >= 0',
            name='requests_per_day_not_negative'
        ),
        UniqueConstraint(
            'telegram_id',
            name='telegram_id_uniq'
        )
    )

    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_premium: Mapped[bool] = mapped_column(default=False)
    last_request = mapped_column(DateTime, nullable=True)
    requests_per_day: Mapped[int] = mapped_column(default=0)

    wb_accounts: Mapped[list['WBAccount']] = relationship(
        'WBAccount',
        back_populates='user',
        cascade='all, delete',
        passive_deletes=True,
        single_parent=True
    )
