from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint, ForeignKey, BigInteger, String
from sqlalchemy.orm import mapped_column, Mapped, relationship

from database.models.base import Base

if TYPE_CHECKING:
    from database.models.user import User


class FavoriteRequest(Base):
    __tablename__ = 'user_favorites_requests'
    __table_args__ = (
        UniqueConstraint(
            'user_id', 'nm_id', 'period',
            name='all_columns_uniq'
        ),
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey('user_account.telegram_id', ondelete='CASCADE')
    )
    wb_account_id: Mapped[int] = mapped_column(
        ForeignKey('wb_account.id')
    )
    name: Mapped[str] = mapped_column(String)
    photo_url: Mapped[str] = mapped_column(String)
    nm_id: Mapped[int] = mapped_column(BigInteger)
    period: Mapped[int] = mapped_column(default=1)

    user: Mapped['User'] = relationship(
        'User',
        back_populates='favorites',
    )
    # TODO Добавить поле wb_account_id
