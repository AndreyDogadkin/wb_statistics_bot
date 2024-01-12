from typing import TYPE_CHECKING

from sqlalchemy import UniqueConstraint, ForeignKey, BigInteger, String
from sqlalchemy.orm import mapped_column, Mapped, relationship

from database.models.base import Base

if TYPE_CHECKING:
    from database.models.user import WBAccount


class FavoriteRequest(Base):
    __tablename__ = 'account_favorites_requests'
    __table_args__ = (
        UniqueConstraint(
            'wb_account_id', 'nm_id', 'period',
            name='all_columns_uniq'
        ),
    )

    wb_account_id: Mapped[int] = mapped_column(
        ForeignKey('wb_account.id', ondelete='CASCADE')
    )
    name: Mapped[str] = mapped_column(String)
    photo_url: Mapped[str] = mapped_column(String)
    nm_id: Mapped[int] = mapped_column(BigInteger)
    period: Mapped[int] = mapped_column(default=1)

    wb_account: Mapped['WBAccount'] = relationship(
        'WBAccount',
        back_populates='favorites',
    )
