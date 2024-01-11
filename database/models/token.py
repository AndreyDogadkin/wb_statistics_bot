from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import Base

if TYPE_CHECKING:
    from database.models.account import WBAccount


class Token(Base):
    __tablename__ = 'wb_tokens'
    __table_args__ = ()

    wb_account_id: Mapped[int] = mapped_column(
        ForeignKey('wb_account.id', ondelete='CASCADE'),
    )
    wb_token_content = mapped_column(LargeBinary, nullable=True)
    wb_token_analytic = mapped_column(LargeBinary, nullable=True)

    wb_account: Mapped['WBAccount'] = relationship(
        'WBAccount',
        back_populates='tokens'
    )
