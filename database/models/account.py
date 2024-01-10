from typing import TYPE_CHECKING

from sqlalchemy import (ForeignKey, String)
from sqlalchemy.orm import mapped_column, Mapped, relationship

from database.models.base import Base

if TYPE_CHECKING:
    from database.models.user import User
    from database.models.token import Token


class WBAccount(Base):
    """Модель для таблицы аккаунтов пользователя."""

    __tablename__ = 'wb_account'
    __table_args__ = ()
    user_id: Mapped['int'] = mapped_column(
        ForeignKey('user_account.telegram_id', ondelete='CASCADE')
    )
    name: Mapped['str'] = mapped_column(String)
    tokens: Mapped['Token'] = relationship(
        'Token',
        back_populates='wb_account',
        cascade='all, delete',
        passive_deletes=True,
        single_parent=True
    )

    user: Mapped['User'] = relationship(
        'User',
        back_populates='wb_account'
    )

