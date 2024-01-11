from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import mapped_column, Mapped, relationship

from database.models.base import Base

if TYPE_CHECKING:
    from database.models import User, Token


class WBAccount(Base):
    """Модель для таблицы аккаунтов пользователя."""

    __tablename__ = 'wb_account'
    __table_args__ = (
        UniqueConstraint(
            'name',
            'user_id',
            name='uniq_account_name'
        ),
    )
    user_id: Mapped['int'] = mapped_column(
        ForeignKey('user_account.telegram_id', ondelete='CASCADE')
    )
    name: Mapped[str] = mapped_column(String)
    is_now_active: Mapped[bool] = mapped_column(default=False)

    tokens: Mapped['Token'] = relationship(
        'Token',
        back_populates='wb_account',
        cascade='all, delete',
        passive_deletes=True,
        single_parent=True
    )
    favorites: Mapped[list['WBAccount']] = relationship(
        'FavoriteRequest',
        back_populates='wb_account',
        cascade='all, delete',
        passive_deletes=True,
        single_parent=True
    )
    user: Mapped['User'] = relationship(
        'User',
        back_populates='wb_accounts'
    )

